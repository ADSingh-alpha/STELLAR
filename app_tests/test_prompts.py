"""
Unit tests for app.agents.prompts.
"""
from app.agents.prompts import (
    ROUTER_SYSTEM_PROMPT,
    SPECIALIST_AGENT_SYSTEM_PROMPT,
    SYNTHESIZER_SYSTEM_PROMPT,
)


def test_system_prompts_content():
    """Verify system prompts contain essential guidance and rules."""
    assert "Geospatial Intent Classifier" in ROUTER_SYSTEM_PROMPT
    assert "RouteDecision" in ROUTER_SYSTEM_PROMPT
    assert "missing_aoi=True" in ROUTER_SYSTEM_PROMPT

    assert "Senior Remote Sensing & Geospatial Specialist Agent" in SPECIALIST_AGENT_SYSTEM_PROMPT
    assert "WGS84 / EPSG:4326" in SPECIALIST_AGENT_SYSTEM_PROMPT
    assert "min_lon, min_lat, max_lon, max_lat" in SPECIALIST_AGENT_SYSTEM_PROMPT
    assert "<= 1.0 degree per side" in SPECIALIST_AGENT_SYSTEM_PROMPT

    assert "Geospatial Intelligence Report Synthesizer" in SYNTHESIZER_SYSTEM_PROMPT
    assert "specialist_metrics" in SYNTHESIZER_SYSTEM_PROMPT
    assert "raster_artifact_uri" in SYNTHESIZER_SYSTEM_PROMPT
