"""
Unit tests for app.agents.tools (BoundingBoxInput, compute_geospatial_index, ToolNode error handling).
"""
import pytest
from pydantic import ValidationError
from langchain_core.messages import ToolCall
from app.agents.tools import (
    BoundingBoxInput,
    compute_geospatial_index,
    geospatial_tool_node,
    STELLAR_TOOLS,
)


def test_bounding_box_input_valid():
    """Verify valid bounding box under 1.0 degree span succeeds."""
    bbox = BoundingBoxInput(
        index_type="ndvi",
        min_lon=77.5,
        max_lon=78.2,
        min_lat=12.5,
        max_lat=13.1,
        max_cloud_cover=15.0
    )
    assert bbox.index_type == "ndvi"
    assert bbox.min_lon == 77.5
    assert bbox.max_cloud_cover == 15.0


def test_bounding_box_input_inverted_coords():
    """Verify min >= max raises ValidationError."""
    with pytest.raises(ValidationError):
        BoundingBoxInput(
            index_type="ndvi",
            min_lon=80.0,
            max_lon=79.0,
            min_lat=10.0,
            max_lat=11.0,
        )

    with pytest.raises(ValidationError):
        BoundingBoxInput(
            index_type="ndwi",
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
            index_type="ndvi",
            min_lon=75.0,
            max_lon=76.5,
            min_lat=12.0,
            max_lat=12.5,
        )
    assert "exceeds the 1.0-degree maximum limit" in str(exc_info.value)

    # Latitude span > 1.0
    with pytest.raises(ValidationError) as exc_info:
        BoundingBoxInput(
            index_type="flood",
            min_lon=75.0,
            max_lon=75.5,
            min_lat=10.0,
            max_lat=11.5,
        )
    assert "exceeds the 1.0-degree maximum limit" in str(exc_info.value)


@pytest.mark.anyio
async def test_compute_geospatial_index_execution():
    """Verify compute_geospatial_index executes non-blocking and returns expected structure."""
    res = await compute_geospatial_index.ainvoke({
        "index_type": "ndvi",
        "min_lon": 77.0,
        "min_lat": 12.0,
        "max_lon": 77.5,
        "max_lat": 12.5,
        "max_cloud_cover": 20.0,
    })
    assert isinstance(res, dict)
    assert res["status"] == "success"
    assert res["index_type"] == "ndvi"
    assert "mean_value" in res
    assert "artifact_uri" in res


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
        "name": "compute_geospatial_index",
        "args": {
            "index_type": "ndvi",
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
