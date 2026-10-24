"""
Unit tests for STELLAR AI Graph (tests/test_ai_graph.py).

Verifies:
1. Passing inverted coordinates (min_lon=80.0, max_lon=75.0) triggers
   BoundingBoxInput's ValidationError inside ToolNode(handle_tool_errors=True)
   and returns a ToolMessage without raising an unhandled exception.
2. Setting iteration_count = 3 forces route_from_specialist to exit directly to "synthesizer".
"""
import pytest
from pydantic import ValidationError
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from app.agents.state import StellarAgentState
from app.agents.tools import geospatial_tool_node, BoundingBoxInput
from app.agents.graph import (
    build_stellar_graph,
    route_from_specialist,
    MAX_ITERATIONS,
)


@pytest.mark.anyio
async def test_inverted_coordinates_tool_node_returns_tool_message():
    """
    Passing inverted coordinates (min_lon=80.0, max_lon=75.0) triggers
    BoundingBoxInput's ValidationError inside ToolNode(handle_tool_errors=True)
    and returns a ToolMessage without raising an unhandled exception.
    """
    # Compile an isolated ToolNode graph to test error capture
    builder = StateGraph(StellarAgentState)
    builder.add_node("tools", geospatial_tool_node)
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    tool_graph = builder.compile()

    # Create invalid tool call with inverted longitude coordinates: min_lon > max_lon
    invalid_tool_call = {
        "name": "compute_geospatial_index",
        "args": {
            "index_type": "ndvi",
            "min_lon": 80.0,  # Inverted!
            "max_lon": 75.0,  # min_lon > max_lon
            "min_lat": 12.0,
            "max_lat": 12.5,
            "max_cloud_cover": 20.0,
        },
        "id": "call_inv_coords_001",
        "type": "tool_call",
    }

    state_input: StellarAgentState = {
        "messages": [
            AIMessage(
                content="Triggering calculation with invalid coordinates",
                tool_calls=[invalid_tool_call],
            )
        ],
        "intent": "ndvi",
        "missing_aoi": False,
        "aoi_bbox": (80.0, 12.0, 75.0, 12.5),
        "date_range": None,
        "raster_artifact_uri": None,
        "specialist_metrics": None,
        "iteration_count": 0,
        "error_state": None,
    }

    # 1. Directly prove that BoundingBoxInput raises ValidationError for inverted coordinates
    with pytest.raises(ValidationError) as exc_info:
        BoundingBoxInput(
            index_type="ndvi",
            min_lon=80.0,
            max_lon=75.0,
            min_lat=12.0,
            max_lat=12.5,
        )
    assert "Invalid longitude bounds" in str(exc_info.value)
    assert "min_lon (80.0) must be < max_lon (75.0)" in str(exc_info.value)

    # 2. Execute graph: must NOT raise an unhandled ValidationError
    output = await tool_graph.ainvoke(state_input)

    # Must return a ToolMessage capturing the error for self-correction
    assert "messages" in output
    last_msg = output["messages"][-1]
    assert isinstance(last_msg, ToolMessage), f"Expected ToolMessage, got {type(last_msg)}"
    assert last_msg.tool_call_id == "call_inv_coords_001"
    assert last_msg.status == "error"

    content_str = str(last_msg.content)
    assert "Error" in content_str or "ToolInvocationError" in content_str


def test_iteration_count_3_forces_route_from_specialist_to_synthesizer():
    """
    Setting iteration_count = 3 forces route_from_specialist to exit directly to 'synthesizer'.
    """
    # 1. State with a pending tool call that would normally route to 'tools'
    tool_call = {
        "name": "compute_geospatial_index",
        "args": {
            "index_type": "ndvi",
            "min_lon": 77.5,
            "min_lat": 12.9,
            "max_lon": 77.6,
            "max_lat": 13.0,
        },
        "id": "call_pending_1",
        "type": "tool_call",
    }

    # When iteration_count = 0 (under limit), it would route to 'tools'
    state_under_limit: StellarAgentState = {
        "messages": [AIMessage(content="", tool_calls=[tool_call])],
        "intent": "ndvi",
        "missing_aoi": False,
        "aoi_bbox": (77.5, 12.9, 77.6, 13.0),
        "date_range": None,
        "raster_artifact_uri": None,
        "specialist_metrics": None,
        "iteration_count": 0,
        "error_state": None,
    }
    assert route_from_specialist(state_under_limit) == "tools"

    # 2. When iteration_count = 3 (MAX_ITERATIONS), it MUST route to 'synthesizer'
    state_at_limit: StellarAgentState = {
        "messages": [AIMessage(content="", tool_calls=[tool_call])],
        "intent": "ndvi",
        "missing_aoi": False,
        "aoi_bbox": (77.5, 12.9, 77.6, 13.0),
        "date_range": None,
        "raster_artifact_uri": None,
        "specialist_metrics": None,
        "iteration_count": 3,
        "error_state": None,
    }
    destination = route_from_specialist(state_at_limit)
    assert destination == "synthesizer", f"Expected 'synthesizer', got '{destination}'"


@pytest.mark.anyio
async def test_compiled_graph_iteration_count_3_exits_to_synthesizer():
    """
    End-to-end compiled graph verification that iteration_count = 3 exits at synthesizer.
    """
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
        "id": "call_pending_2",
        "type": "tool_call",
    }

    state_input: StellarAgentState = {
        "messages": [
            HumanMessage(content="Calculate NDVI"),
            AIMessage(content="Planning analysis", tool_calls=[tool_call]),
        ],
        "intent": "ndvi",
        "missing_aoi": False,
        "aoi_bbox": (77.5, 12.9, 77.6, 13.0),
        "date_range": None,
        "raster_artifact_uri": None,
        "specialist_metrics": None,
        "iteration_count": 3,  # Already at MAX_ITERATIONS
        "error_state": None,
    }

    result = await graph.ainvoke(state_input)
    # The final message must be from synthesizer (no tool_calls)
    final_message = result["messages"][-1]
    assert isinstance(final_message, AIMessage)
    assert not getattr(final_message, "tool_calls", None)
