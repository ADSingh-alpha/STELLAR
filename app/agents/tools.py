# app/agents/tools.py
import asyncio
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode


class BoundingBoxInput(BaseModel):
    index_type: Literal["ndvi", "ndwi", "flood", "urban_change"] = Field(
        ..., description="Spectral or SAR index to compute."
    )
    min_lon: float = Field(..., ge=-180.0, le=180.0, description="Westernmost longitude (EPSG:4326)")
    min_lat: float = Field(..., ge=-90.0, le=90.0, description="Southernmost latitude (EPSG:4326)")
    max_lon: float = Field(..., ge=-180.0, le=180.0, description="Easternmost longitude (EPSG:4326)")
    max_lat: float = Field(..., ge=-90.0, le=90.0, description="Northernmost latitude (EPSG:4326)")
    max_cloud_cover: float = Field(default=20.0, ge=0.0, le=100.0, description="Maximum allowed cloud cover %")

    @model_validator(mode="after")
    def validate_spatial_bounds(self) -> "BoundingBoxInput":
        if self.min_lon >= self.max_lon:
            raise ValueError(f"Invalid longitude bounds: min_lon ({self.min_lon}) must be < max_lon ({self.max_lon}). Did you swap lat/lon?")
        if self.min_lat >= self.max_lat:
            raise ValueError(f"Invalid latitude bounds: min_lat ({self.min_lat}) must be < max_lat ({self.max_lat}). Did you swap lat/lon?")
        if (self.max_lon - self.min_lon) > 1.0 or (self.max_lat - self.min_lat) > 1.0:
            raise ValueError("Bounding box span exceeds the 1.0-degree maximum limit per side. Please narrow the AOI.")
        return self


def _sync_compute_raster_metrics(
    index_type: str, min_lon: float, min_lat: float, max_lon: float, max_lat: float, max_cloud_cover: float
) -> dict:
    """Synchronous rasterio/GDAL window computation executed off the main event loop."""
    # Replace/integrate with existing STELLAR rasterio window read logic here
    return {
        "status": "success",
        "index_type": index_type,
        "mean_value": 0.62,
        "min_value": 0.14,
        "max_value": 0.84,
        "cloud_cover_pct": 5.1,
        "artifact_uri": f"s3://stellar-cache/{index_type}_{min_lon:.3f}_{min_lat:.3f}.tif",
    }


@tool("compute_geospatial_index", args_schema=BoundingBoxInput, return_direct=False)
async def compute_geospatial_index(
    index_type: str,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    max_cloud_cover: float = 20.0,
) -> dict:
    """Computes validated satellite spectral/SAR indices over a WGS84 bounding box without blocking the event loop."""
    return await asyncio.to_thread(
        _sync_compute_raster_metrics, index_type, min_lon, min_lat, max_lon, max_lat, max_cloud_cover
    )


STELLAR_TOOLS = [compute_geospatial_index]
GEOSPATIAL_TOOLS = STELLAR_TOOLS

# handle_tool_errors=True catches Pydantic ValidationErrors and returns them to the agent to self-correct
geospatial_tool_node = ToolNode(tools=STELLAR_TOOLS, handle_tool_errors=True)
