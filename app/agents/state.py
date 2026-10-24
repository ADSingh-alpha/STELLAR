"""
Slim & Strictly Typed Graph State for STELLAR AI.

Replaces untyped dictionaries and raw NumPy/base64 payloads with a compact,
strictly validated TypedDict to prevent memory bloat and VRAM exhaustion.
Only raster artifact URIs/pointers are stored, never raw raster arrays or bytes.
"""

from typing import Annotated, Optional, Literal, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

# Allowed intent classifications
IntentType = Literal["ndvi", "ndwi", "flood", "urban_change", "general_qa"]


class StellarAgentState(TypedDict):
    """
    Slim, bounded LangGraph state for STELLAR multi-agent workflows.
    Guarantees zero raw raster array or base64 storage in memory/checkpoints.
    """
    messages: Annotated[list[AnyMessage], add_messages]
    intent: Optional[Literal["ndvi", "ndwi", "flood", "urban_change", "general_qa"]]
    aoi_bbox: Optional[tuple[float, float, float, float]]
    raster_artifact_uri: Optional[str]
    specialist_metrics: Optional[dict[str, float]]
    iteration_count: int
    error_state: Optional[str]
