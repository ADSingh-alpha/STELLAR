# app/agents/state.py
from typing import Annotated, TypedDict, Literal, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

IntentType = Literal["ndvi", "ndwi", "flood", "urban_change", "general_qa"]


class StellarAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    intent: Optional[IntentType]
    missing_aoi: bool
    aoi_bbox: Optional[tuple[float, float, float, float]]  # Strictly (min_lon, min_lat, max_lon, max_lat) in EPSG:4326
    date_range: Optional[tuple[str, str]]                  # ("YYYY-MM-DD", "YYYY-MM-DD")
    raster_artifact_uri: Optional[str]                     # Pointer/URI to processed COG/GeoTIFF, NEVER raw bytes
    specialist_metrics: Optional[dict[str, float]]         # Scalar summary stats (mean_ndvi, cloud_cover_pct, area_km2)
    iteration_count: int                                   # Hard loop-breaker counter
    error_state: Optional[str]                             # Populated if tool retries fail
