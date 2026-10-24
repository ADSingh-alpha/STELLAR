# app/agents/graph.py
import re
import json
import logging
from typing import Literal, Optional, Tuple, Any, Dict
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END

from app.agents.state import StellarAgentState, IntentType
from app.agents.prompts import (
    ROUTER_SYSTEM_PROMPT,
    SPECIALIST_AGENT_SYSTEM_PROMPT,
    SYNTHESIZER_SYSTEM_PROMPT,
)
from app.agents.tools import STELLAR_TOOLS, geospatial_tool_node

logger = logging.getLogger("stellar.graph")

MAX_ITERATIONS = 3


class RouteDecision(BaseModel):
    intent: IntentType = Field(..., description="Classified geospatial intent.")
    missing_aoi: bool = Field(
        default=False,
        description="True if raster computation is needed but AOI coordinates are missing."
    )


# ---------------------------------------------------------------------------
# Deterministic Fallback Mock LLM for Offline / Dry-Run Testing
# ---------------------------------------------------------------------------

class DeterministicMockLLM:
    """
    Ensures build_stellar_graph works seamlessly even when external LLM credentials
    are not configured in test or offline environments.
    """
    def __init__(self, tools=None, schema_cls=None):
        self.tools = tools or []
        self.schema_cls = schema_cls

    def with_structured_output(self, schema_cls):
        return DeterministicMockLLM(tools=self.tools, schema_cls=schema_cls)

    def bind_tools(self, tools):
        return DeterministicMockLLM(tools=tools, schema_cls=self.schema_cls)

    async def ainvoke(self, messages, **kwargs):
        # 1. Structured output for RouteDecision
        if self.schema_cls == RouteDecision:
            user_text = ""
            for m in reversed(messages):
                if hasattr(m, "content") and m.content and not isinstance(m, SystemMessage):
                    user_text = str(m.content).lower()
                    break

            if "ndvi" in user_text or "vegetation" in user_text:
                return RouteDecision(intent="ndvi", missing_aoi=False)
            elif "ndwi" in user_text or "water" in user_text:
                return RouteDecision(intent="ndwi", missing_aoi=False)
            elif "flood" in user_text:
                return RouteDecision(intent="flood", missing_aoi=False)
            elif "urban" in user_text:
                return RouteDecision(intent="urban_change", missing_aoi=False)
            else:
                return RouteDecision(intent="general_qa", missing_aoi=False)

        # 2. Specialist node with bound tools
        if self.tools:
            if messages and isinstance(messages[-1], ToolMessage):
                return AIMessage(content="Geospatial analysis computed successfully based on tool results.")

            # Extract AOI coordinates from system context note if available
            bbox = None
            for m in messages:
                if hasattr(m, "content") and "Current AOI BBox:" in str(m.content):
                    match = re.search(r"Current AOI BBox:\s*(\([^)]+\))", str(m.content))
                    if match:
                        try:
                            bbox = eval(match.group(1))
                        except Exception:
                            pass
            if bbox is None:
                bbox = (77.5, 12.9, 77.6, 13.0)

            # Extract intent from system context note
            intent = "ndvi"
            for m in messages:
                if hasattr(m, "content") and "Target Intent:" in str(m.content):
                    for potential in ["ndvi", "ndwi", "flood", "urban_change"]:
                        if potential in str(m.content):
                            intent = potential
                            break

            tool_call = {
                "name": "compute_geospatial_index",
                "args": {
                    "index_type": intent,
                    "min_lon": bbox[0],
                    "min_lat": bbox[1],
                    "max_lon": bbox[2],
                    "max_lat": bbox[3],
                    "max_cloud_cover": 20.0,
                },
                "id": "call_geo_1",
                "type": "tool_call",
            }
            return AIMessage(content="Executing compute_geospatial_index.", tool_calls=[tool_call])

        # 3. Default synthesizer synthesis
        return AIMessage(content="### STELLAR Geospatial Intelligence Report\nTelemetry and spectral indices synthesized.")


def route_from_classifier(state: StellarAgentState) -> str:
    """Routes after intent classification."""
    if state.get("missing_aoi"):
        return "clarification"
    if state.get("intent") == "general_qa":
        return "synthesizer"
    return "specialist"


def route_from_specialist(state: StellarAgentState) -> str:
    """
    Enforces loop termination if iteration_count >= MAX_ITERATIONS,
    otherwise routes to tools or synthesizer based on tool_calls.
    """
    last_message = state["messages"][-1]
    if state.get("iteration_count", 0) >= MAX_ITERATIONS:
        return "synthesizer"
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return "synthesizer"


# ---------------------------------------------------------------------------
# StateGraph Builder
# ---------------------------------------------------------------------------

def build_stellar_graph(llm: Any = None, checkpointer: Any = None):
    """
    Compiles the bounded STELLAR multi-agent StateGraph with durable checkpointing.
    """
    if llm is None:
        llm = DeterministicMockLLM()

    structured_router_llm = llm.with_structured_output(RouteDecision)
    specialist_llm = llm.bind_tools(STELLAR_TOOLS)

    async def classifier_node(state: StellarAgentState) -> dict:
        decision: RouteDecision = await structured_router_llm.ainvoke(
            [SystemMessage(content=ROUTER_SYSTEM_PROMPT)] + state["messages"]
        )
        return {
            "intent": decision.intent,
            "missing_aoi": decision.missing_aoi,
            "iteration_count": state.get("iteration_count", 0),
        }

    async def specialist_node(state: StellarAgentState) -> dict:
        current_iter = state.get("iteration_count", 0) + 1
        context_note = f"\nCurrent AOI BBox: {state.get('aoi_bbox')} | Target Intent: {state.get('intent')}"
        response = await specialist_llm.ainvoke(
            [SystemMessage(content=SPECIALIST_AGENT_SYSTEM_PROMPT + context_note)] + state["messages"]
        )
        updates: dict = {
            "messages": [response],
            "iteration_count": current_iter,
        }

        # If previous message was a ToolMessage, extract metrics & artifact URI
        if state.get("messages") and isinstance(state["messages"][-1], ToolMessage):
            last_msg = state["messages"][-1]
            try:
                data = last_msg.content if isinstance(last_msg.content, dict) else json.loads(last_msg.content)
                if isinstance(data, dict):
                    metrics = {k: float(v) for k, v in data.items() if isinstance(v, (int, float))}
                    updates["specialist_metrics"] = metrics
                    updates["raster_artifact_uri"] = data.get("raster_artifact_uri") or data.get("artifact_uri")
            except Exception:
                pass

        return updates

    async def synthesizer_node(state: StellarAgentState) -> dict:
        meta_context = (
            f"\nSpecialist Metrics: {state.get('specialist_metrics')}"
            f"\nArtifact URI: {state.get('raster_artifact_uri')}"
            f"\nError State: {state.get('error_state')}"
        )
        response = await llm.ainvoke(
            [SystemMessage(content=SYNTHESIZER_SYSTEM_PROMPT + meta_context)] + state["messages"]
        )
        return {"messages": [response]}

    async def clarification_node(state: StellarAgentState) -> dict:
        msg = AIMessage(
            content="Please select or draw an Area of Interest (AOI) bounding box on the map (or provide `[min_lon, min_lat, max_lon, max_lat]` coordinates) so I can run the satellite analysis."
        )
        return {"messages": [msg]}

    builder = StateGraph(StellarAgentState)
    builder.add_node("classifier", classifier_node)
    builder.add_node("specialist", specialist_node)
    builder.add_node("tools", geospatial_tool_node)
    builder.add_node("synthesizer", synthesizer_node)
    builder.add_node("clarification", clarification_node)

    builder.add_edge(START, "classifier")
    builder.add_conditional_edges(
        "classifier",
        route_from_classifier,
        {
            "clarification": "clarification",
            "specialist": "specialist",
            "synthesizer": "synthesizer",
        },
    )
    builder.add_conditional_edges(
        "specialist",
        route_from_specialist,
        {
            "tools": "tools",
            "synthesizer": "synthesizer",
        },
    )
    builder.add_edge("tools", "specialist")
    builder.add_edge("synthesizer", END)
    builder.add_edge("clarification", END)

    return builder.compile(checkpointer=checkpointer)


# Backward-compatible alias
create_stellar_graph = build_stellar_graph
