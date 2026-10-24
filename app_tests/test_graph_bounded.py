"""
Unit tests for app.agents.graph (build_stellar_graph, RouteDecision, MAX_ITERATIONS, clarification).
"""
import pytest
from langchain_core.messages import HumanMessage, AIMessage
from app.agents.graph import build_stellar_graph, create_stellar_graph, RouteDecision, MAX_ITERATIONS
from app.agents.state import StellarAgentState


@pytest.mark.anyio
async def test_structured_routing_ndvi():
    """Verify router classifies NDVI query and executes specialist workflow."""
    graph = build_stellar_graph()
    initial_state: StellarAgentState = {
        "messages": [HumanMessage(content="Please calculate NDVI over Bangalore vegetation")],
        "intent": None,
        "missing_aoi": False,
        "aoi_bbox": (77.5, 12.9, 77.6, 13.0),
        "date_range": None,
        "raster_artifact_uri": None,
        "specialist_metrics": None,
        "iteration_count": 0,
        "error_state": None,
    }

    result = await graph.ainvoke(initial_state)
    assert result["intent"] == "ndvi"
    assert result["aoi_bbox"] == (77.5, 12.9, 77.6, 13.0)
    assert result["specialist_metrics"] is not None
    assert "mean_value" in result["specialist_metrics"]
    assert result["raster_artifact_uri"] is not None
    assert result["iteration_count"] <= MAX_ITERATIONS


@pytest.mark.anyio
async def test_missing_aoi_clarification():
    """Verify missing_aoi routes to clarification node requesting bounding box."""
    # Custom mock router that sets missing_aoi=True
    class MissingAOIRouterMock:
        def with_structured_output(self, schema_cls):
            return self

        def bind_tools(self, tools):
            return self

        async def ainvoke(self, messages, **kwargs):
            return RouteDecision(intent="ndvi", missing_aoi=True)

    graph = build_stellar_graph(llm=MissingAOIRouterMock())
    initial_state: StellarAgentState = {
        "messages": [HumanMessage(content="Compute vegetation index")],
        "intent": None,
        "missing_aoi": False,
        "aoi_bbox": None,
        "date_range": None,
        "raster_artifact_uri": None,
        "specialist_metrics": None,
        "iteration_count": 0,
        "error_state": None,
    }

    result = await graph.ainvoke(initial_state)
    assert result["missing_aoi"] is True
    last_msg = result["messages"][-1]
    assert "Area of Interest (AOI)" in str(last_msg.content)


@pytest.mark.anyio
async def test_general_qa_routing():
    """Verify general QA routes directly without tool invocations."""
    graph = build_stellar_graph()
    initial_state: StellarAgentState = {
        "messages": [HumanMessage(content="What satellites are in orbit?")],
        "intent": None,
        "missing_aoi": False,
        "aoi_bbox": None,
        "date_range": None,
        "raster_artifact_uri": None,
        "specialist_metrics": None,
        "iteration_count": 0,
        "error_state": None,
    }

    result = await graph.ainvoke(initial_state)
    assert result["intent"] == "general_qa"
    assert result["aoi_bbox"] is None
    assert result["raster_artifact_uri"] is None


@pytest.mark.anyio
async def test_max_iteration_guard_enforced():
    """Verify that reaching MAX_ITERATIONS forces routing directly to synthesizer."""
    graph = build_stellar_graph()

    tool_call = {
        "name": "compute_geospatial_index",
        "args": {
            "index_type": "ndvi",
            "min_lon": 77.5,
            "min_lat": 12.9,
            "max_lon": 77.6,
            "max_lat": 13.0,
        },
        "id": "call_loop_1",
        "type": "tool_call",
    }

    state: StellarAgentState = {
        "messages": [
            HumanMessage(content="Analyze vegetation"),
            AIMessage(content="", tool_calls=[tool_call])
        ],
        "intent": "ndvi",
        "missing_aoi": False,
        "aoi_bbox": (77.5, 12.9, 77.6, 13.0),
        "date_range": None,
        "raster_artifact_uri": None,
        "specialist_metrics": None,
        "iteration_count": MAX_ITERATIONS,  # Already at MAX_ITERATIONS!
        "error_state": None,
    }

    result = await graph.ainvoke(state)
    # Graph routes directly from specialist to synthesizer when iteration_count >= MAX_ITERATIONS
    last_msg = result["messages"][-1]
    assert isinstance(last_msg, AIMessage)
    assert last_msg.tool_calls == []
