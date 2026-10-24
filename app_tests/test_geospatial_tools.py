"""
Unit tests for app.agents.tools (BoundingBoxInput, safe reads, ToolNode error handling).
"""
import pytest
from pydantic import ValidationError
from langchain_core.messages import ToolCall
from app.agents.tools import (
    BoundingBoxInput,
    safe_read_raster_window,
    calculate_ndvi,
    geospatial_tool_node,
    GEOSPATIAL_TOOLS,
)


def test_bounding_box_input_valid():
    """Verify valid bounding box under 1.0 degree span succeeds."""
    bbox = BoundingBoxInput(
        min_lon=77.5,
        max_lon=78.2,
        min_lat=12.5,
        max_lat=13.1,
        max_cloud_cover=15.0
    )
    assert bbox.min_lon == 77.5
    assert bbox.max_cloud_cover == 15.0


def test_bounding_box_input_inverted_coords():
    """Verify min >= max raises ValidationError."""
    with pytest.raises(ValidationError):
        BoundingBoxInput(
            min_lon=80.0,
            max_lon=79.0,
            min_lat=10.0,
            max_lat=11.0,
        )

    with pytest.raises(ValidationError):
        BoundingBoxInput(
            min_lon=79.0,
            max_lon=80.0,
            min_lat=15.0,
            max_lat=14.0,
        )


def test_bounding_box_input_span_exceeded():
    """Verify spans greater than 1.0 degree raise ValidationError."""
    # Longitude span > 1.0
    with pytest.raises(ValidationError) as exc_info:
        BoundingBoxInput(
            min_lon=75.0,
            max_lon=76.5,
            min_lat=12.0,
            max_lat=12.5,
        )
    assert "exceeds maximum allowable span of 1.0 degree" in str(exc_info.value)

    # Latitude span > 1.0
    with pytest.raises(ValidationError) as exc_info:
        BoundingBoxInput(
            min_lon=75.0,
            max_lon=75.5,
            min_lat=10.0,
            max_lat=11.5,
        )
    assert "exceeds maximum allowable span of 1.0 degree" in str(exc_info.value)


@pytest.mark.anyio
async def test_safe_read_raster_window_non_blocking():
    """Verify raster window reading runs in thread without error."""
    res = await safe_read_raster_window("s3://fake/test.tif", (77.0, 12.0, 77.5, 12.5))
    assert isinstance(res, dict)
    assert "status" in res


@pytest.mark.anyio
async def test_tool_node_handles_validation_error_gracefully():
    """Verify ToolNode catches Pydantic validation errors and converts them to ToolMessages."""
    from langgraph.graph import StateGraph, START, END
    from langchain_core.messages import AIMessage
    from app.agents.state import StellarAgentState

    builder = StateGraph(StellarAgentState)
    builder.add_node("tools", geospatial_tool_node)
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    test_graph = builder.compile()

    # Malformed call: span > 1.0 degree
    invalid_tool_call = {
        "name": "calculate_ndvi",
        "args": {
            "min_lon": 70.0,
            "max_lon": 75.0,  # 5 degrees span -> triggers validation error!
            "min_lat": 10.0,
            "max_lat": 10.5,
        },
        "id": "call_test_123",
        "type": "tool_call",
    }

    state_input: StellarAgentState = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[invalid_tool_call],
            )
        ],
        "intent": "ndvi",
        "missing_aoi": False,
        "aoi_bbox": None,
        "date_range": None,
        "raster_artifact_uri": None,
        "specialist_metrics": None,
        "iteration_count": 0,
        "error_state": None,
    }

    output = await test_graph.ainvoke(state_input)
    assert "messages" in output
    tool_message = output["messages"][-1]
    assert tool_message.tool_call_id == "call_test_123"
    assert tool_message.status == "error" or "Error" in str(tool_message.content)
