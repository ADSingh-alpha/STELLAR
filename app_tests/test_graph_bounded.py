"""
Unit tests for app.agents.graph (Bounded StateGraph, Structured Routing, MAX_ITERATIONS guard).
"""
import pytest
from langchain_core.messages import HumanMessage, AIMessage
from app.agents.graph import create_stellar_graph, RouteDecision, MAX_ITERATIONS
from app.agents.state import StellarAgentState


@pytest.mark.anyio
async def test_structured_routing_ndvi():
    """Verify router classifies NDVI query and executes specialist workflow."""
    graph = create_stellar_graph()
    initial_state: StellarAgentState = {
        "messages": [HumanMessage(content="Please calculate NDVI over Bangalore vegetation")],
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
    assert result["intent"] == "ndvi"
    assert result["aoi_bbox"] == (77.5, 12.9, 77.6, 13.0)
    assert result["specialist_metrics"] is not None
    assert "mean_ndvi" in result["specialist_metrics"]
    assert result["raster_artifact_uri"] is not None
    assert result["iteration_count"] <= MAX_ITERATIONS
    assert result["error_state"] is None


@pytest.mark.anyio
async def test_general_qa_routing():
    """Verify general QA routes directly without tool invocations."""
    graph = create_stellar_graph()
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
    """Verify that exceeding MAX_ITERATIONS forces routing to fallback_handler."""
    graph = create_stellar_graph()

    # Pre-seed state at MAX_ITERATIONS (3) with a tool call pending
    tool_call = {
        "name": "calculate_ndvi",
        "args": {
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
        "iteration_count": MAX_ITERATIONS,  # Already at max iterations!
        "error_state": None,
    }

    result = await graph.ainvoke(state)
    assert result["error_state"] == "MAX_ITERATIONS_EXCEEDED"
    assert "Maximum iteration limit" in result["messages"][-1].content
