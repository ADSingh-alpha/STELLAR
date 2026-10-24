"""
Unit tests for app.agents.state (StellarAgentState).
"""
import pytest
from typing import get_type_hints
from langchain_core.messages import HumanMessage
from app.agents.state import StellarAgentState


def test_stellar_agent_state_keys():
    """Verify StellarAgentState contains ONLY the 7 required fields."""
    expected_fields = {
        "messages",
        "intent",
        "aoi_bbox",
        "raster_artifact_uri",
        "specialist_metrics",
        "iteration_count",
        "error_state",
    }
    hints = get_type_hints(StellarAgentState)
    assert set(hints.keys()) == expected_fields
    assert len(hints) == 7


def test_stellar_agent_state_instantiation():
    """Verify instantiation with valid types and URI pointer."""
    state: StellarAgentState = {
        "messages": [HumanMessage(content="Calculate NDVI over area")],
        "intent": "ndvi",
        "aoi_bbox": (77.5, 12.9, 77.6, 13.0),
        "raster_artifact_uri": "s3://stellar-cache/cog/sentinel2_2024.tif",
        "specialist_metrics": {"mean_ndvi": 0.65},
        "iteration_count": 1,
        "error_state": None,
    }
    assert state["intent"] == "ndvi"
    assert state["aoi_bbox"] == (77.5, 12.9, 77.6, 13.0)
    assert state["raster_artifact_uri"].startswith("s3://")
    assert state["iteration_count"] == 1
