"""
Bounded StateGraph & Structured Routing for STELLAR AI.

Enforces deterministic structured routing via .with_structured_output(RouteDecision),
bounded graph iterations with MAX_ITERATIONS = 3 hard guard, and 100% async LLM execution
using .ainvoke().
"""

import json
import logging
from typing import Any, Dict, Literal, Optional, Tuple, Union
from pydantic import BaseModel, Field

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from app.agents.state import StellarAgentState, IntentType
from app.agents.tools import geospatial_tool_node, GEOSPATIAL_TOOLS

logger = logging.getLogger("stellar.graph")

MAX_ITERATIONS = 3


# ---------------------------------------------------------------------------
# Structured Routing Decision Schema
# ---------------------------------------------------------------------------

class RouteDecision(BaseModel):
    """
    Deterministic routing decision produced by .with_structured_output().
    Eliminates fragile regex parsing of unstructured model outputs.
    """
    intent: Literal["ndvi", "ndwi", "flood", "urban_change", "general_qa"] = Field(
        ...,
        description="Classified geospatial task or general question answering intent"
    )
    aoi_bbox: Optional[Tuple[float, float, float, float]] = Field(
        default=None,
        description="WGS84 bounding box (min_lon, min_lat, max_lon, max_lat) if geospatial analysis is requested"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning trace for intent classification and coordinate identification"
    )


# ---------------------------------------------------------------------------
# Fallback / Deterministic Router for Offline / Mock Environments
# ---------------------------------------------------------------------------

class DeterministicRouterModel:
    """
    Guarantees deterministic structured output even when external LLM API
    keys are unset during unit testing or dry runs.
    """
    def with_structured_output(self, schema_cls):
        self.schema_cls = schema_cls
        return self

    async def ainvoke(self, messages, **kwargs) -> RouteDecision:
        user_query = ""
        for m in reversed(messages):
            if isinstance(m, (HumanMessage, dict)) and getattr(m, "content", None):
                user_query = str(m.content).lower()
                break
            elif isinstance(m, dict) and "content" in m:
                user_query = str(m["content"]).lower()
                break

        # Keyword-based deterministic classification
        if "ndvi" in user_query or "vegetation" in user_query:
            return RouteDecision(
                intent="ndvi",
                aoi_bbox=(77.5, 12.9, 77.6, 13.0),
                reasoning="Query requested vegetation/NDVI analysis."
            )
        elif "ndwi" in user_query or "water" in user_query:
            return RouteDecision(
                intent="ndwi",
                aoi_bbox=(77.5, 12.9, 77.6, 13.0),
                reasoning="Query requested water body/NDWI analysis."
            )
        elif "flood" in user_query or "inundation" in user_query:
            return RouteDecision(
                intent="flood",
                aoi_bbox=(77.5, 12.9, 77.6, 13.0),
                reasoning="Query requested flood extent analysis."
            )
        elif "urban" in user_query or "expansion" in user_query or "city" in user_query:
            return RouteDecision(
                intent="urban_change",
                aoi_bbox=(77.5, 12.9, 77.6, 13.0),
                reasoning="Query requested urban change detection."
            )
        else:
            return RouteDecision(
                intent="general_qa",
                aoi_bbox=None,
                reasoning="General question not requiring geospatial raster analysis."
            )


# ---------------------------------------------------------------------------
# Node Implementations
# ---------------------------------------------------------------------------

def create_stellar_graph(
    llm: Any = None,
    checkpointer: Any = None
) -> CompiledStateGraph:
    """
    Constructs and compiles the bounded STELLAR multi-agent StateGraph.
    All LLM calls within nodes strictly use .ainvoke().
    """
    if llm is None:
        llm = DeterministicRouterModel()

    async def router_node(state: StellarAgentState) -> Dict[str, Any]:
        """
        Classifies incoming query into structured RouteDecision using .with_structured_output().
        """
        messages = state.get("messages", [])
        structured_llm = llm.with_structured_output(RouteDecision)
        
        # Async invocation
        decision: RouteDecision = await structured_llm.ainvoke(messages)

        existing_iterations = state.get("iteration_count", 0)
        return {
            "intent": decision.intent,
            "aoi_bbox": decision.aoi_bbox,
            "iteration_count": existing_iterations,
            "error_state": None,
        }

    async def specialist_agent_node(state: StellarAgentState) -> Dict[str, Any]:
        """
        Specialist agent cycle that selects appropriate geospatial tool or synthesizes.
        Increments iteration_count on every execution.
        """
        current_iterations = state.get("iteration_count", 0) + 1
        intent = state.get("intent")
        bbox = state.get("aoi_bbox")
        messages = state.get("messages", [])

        # Check if the last message is a ToolMessage with results
        if messages and isinstance(messages[-1], ToolMessage):
            last_tool_msg = messages[-1]
            try:
                data = json.loads(last_tool_msg.content)
                metrics = {k: float(v) for k, v in data.items() if isinstance(v, (int, float))}
                artifact_uri = data.get("raster_artifact_uri")
                return {
                    "iteration_count": current_iterations,
                    "specialist_metrics": metrics,
                    "raster_artifact_uri": artifact_uri,
                }
            except Exception:
                pass

        # If general QA, no tool needed
        if intent == "general_qa" or not bbox:
            return {
                "iteration_count": current_iterations,
            }

        # Select tool based on intent
        tool_name_map = {
            "ndvi": "calculate_ndvi",
            "ndwi": "calculate_ndwi",
            "flood": "detect_flood_extent",
            "urban_change": "analyze_urban_change",
        }
        target_tool = tool_name_map.get(intent, "calculate_ndvi")

        # Create structured tool call
        tool_call = {
            "name": target_tool,
            "args": {
                "min_lon": bbox[0],
                "min_lat": bbox[1],
                "max_lon": bbox[2],
                "max_lat": bbox[3],
                "max_cloud_cover": 20.0,
            },
            "id": f"call_{intent}_{current_iterations}",
            "type": "tool_call",
        }

        ai_msg = AIMessage(
            content=f"Executing geospatial tool {target_tool} for AOI {bbox}",
            tool_calls=[tool_call]
        )

        return {
            "messages": [ai_msg],
            "iteration_count": current_iterations,
        }

    async def synthesize_report_node(state: StellarAgentState) -> Dict[str, Any]:
        """
        Synthesizes the final intelligence report asynchronously using metrics and state.
        """
        intent = state.get("intent", "general_qa")
        metrics = state.get("specialist_metrics") or {}
        artifact_uri = state.get("raster_artifact_uri")
        bbox = state.get("aoi_bbox")

        report_lines = [
            f"### STELLAR Earth Observation Intelligence Report",
            f"- **Intent**: {intent}",
        ]
        if bbox:
            report_lines.append(f"- **Bounding Box (WGS84)**: {bbox}")
        if metrics:
            report_lines.append("- **Specialist Metrics**:")
            for k, v in metrics.items():
                report_lines.append(f"  - {k}: {v}")
        if artifact_uri:
            report_lines.append(f"- **Artifact Pointer**: `{artifact_uri}`")

        final_content = "\n".join(report_lines)
        return {
            "messages": [AIMessage(content=final_content)],
            "error_state": None,
        }

    async def fallback_handler_node(state: StellarAgentState) -> Dict[str, Any]:
        """
        Safety fallback handler triggered when MAX_ITERATIONS (3) is exceeded
        or unrecoverable errors occur. Enforces bounded graph execution.
        """
        iterations = state.get("iteration_count", 0)
        error_msg = (
            f"Execution halted: Maximum iteration limit ({MAX_ITERATIONS}) reached "
            f"(current={iterations}). Bounded execution guard enforced to prevent runaway cost and OOM."
        )
        return {
            "messages": [AIMessage(content=error_msg)],
            "error_state": "MAX_ITERATIONS_EXCEEDED",
        }

    # -----------------------------------------------------------------------
    # Conditional Edge Guards
    # -----------------------------------------------------------------------

    def route_after_router(state: StellarAgentState) -> str:
        if state.get("iteration_count", 0) >= MAX_ITERATIONS:
            return "fallback_handler"
        intent = state.get("intent")
        if intent == "general_qa":
            return "synthesize_report"
        return "specialist_agent"

    def route_after_specialist(state: StellarAgentState) -> str:
        # 1. Hard iteration bound guard: direct to fallback or synthesis
        if state.get("iteration_count", 0) >= MAX_ITERATIONS:
            logger.warning("Max iterations reached (%d). Routing to fallback.", MAX_ITERATIONS)
            return "fallback_handler"

        # 2. Check for tool calls
        messages = state.get("messages", [])
        if messages and isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
            return "tools"

        return "synthesize_report"

    def route_after_tools(state: StellarAgentState) -> str:
        # Enforce hard iteration bound guard
        if state.get("iteration_count", 0) >= MAX_ITERATIONS:
            return "fallback_handler"
        return "specialist_agent"

    # -----------------------------------------------------------------------
    # StateGraph Assembly
    # -----------------------------------------------------------------------

    workflow = StateGraph(StellarAgentState)

    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("specialist_agent", specialist_agent_node)
    workflow.add_node("tools", geospatial_tool_node)
    workflow.add_node("synthesize_report", synthesize_report_node)
    workflow.add_node("fallback_handler", fallback_handler_node)

    # Edges
    workflow.add_edge(START, "router")

    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "synthesize_report": "synthesize_report",
            "specialist_agent": "specialist_agent",
            "fallback_handler": "fallback_handler",
        }
    )

    workflow.add_conditional_edges(
        "specialist_agent",
        route_after_specialist,
        {
            "tools": "tools",
            "synthesize_report": "synthesize_report",
            "fallback_handler": "fallback_handler",
        }
    )

    workflow.add_conditional_edges(
        "tools",
        route_after_tools,
        {
            "specialist_agent": "specialist_agent",
            "fallback_handler": "fallback_handler",
        }
    )

    workflow.add_edge("synthesize_report", END)
    workflow.add_edge("fallback_handler", END)

    return workflow.compile(checkpointer=checkpointer)
