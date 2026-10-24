"""
FastAPI Microservice Entrypoint for STELLAR (SatQuery AI).

Enforces GPU VRAM guard at the top of the file, manages durable PostgreSQL
checkpointer lifecycle via lifespan context manager, and streams execution events
using stellar_graph.astream_events(..., version="v2").
"""

# ---------------------------------------------------------------------------
# 1. GPU & VRAM Isolation Guard (Must execute at the very top of app/main.py)
# ---------------------------------------------------------------------------
from app.core.gpu_guard import setup_gpu_guard

setup_gpu_guard()

# Safe explicit TensorFlow memory growth configuration as specified
try:
    import tensorflow as tf
    physical_gpus = tf.config.experimental.list_physical_devices("GPU")
    if physical_gpus:
        for gpu in physical_gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
except ImportError:
    pass
except Exception:
    pass

import os
import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Tuple

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from app.agents.graph import create_stellar_graph
from app.agents.checkpointer import init_postgres_checkpointer, create_postgres_pool
from app.agents.state import StellarAgentState

logger = logging.getLogger("stellar.main")
logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------

class QueryStreamRequest(BaseModel):
    """Payload for real-time streaming agent query."""
    session_id: str = Field(..., description="Unique user or session thread ID for durable checkpointing")
    query: str = Field(..., description="Natural language user request for Earth Observation analysis")
    aoi_bbox: Optional[Tuple[float, float, float, float]] = Field(
        default=None,
        description="Optional pre-selected WGS84 bounding box (min_lon, min_lat, max_lon, max_lat)"
    )
    date_range: Optional[Tuple[str, str]] = Field(
        default=None,
        description="Optional temporal filter range ('YYYY-MM-DD', 'YYYY-MM-DD')"
    )


# ---------------------------------------------------------------------------
# Lifespan Context Manager (PostgreSQL Checkpointer Lifecycle)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages startup and shutdown lifecycles:
    - Sets up durable PostgreSQL checkpointing via AsyncPostgresSaver and AsyncConnectionPool.
    - Compiles and binds the state graph to app.state.stellar_graph.
    - Closes connection pools on shutdown.
    """
    logger.info("Starting STELLAR AI Microservice...")
    pool = None
    try:
        checkpointer, pool = await init_postgres_checkpointer()
        app.state.pg_pool = pool
        app.state.checkpointer = checkpointer
        app.state.stellar_graph = create_stellar_graph(checkpointer=checkpointer)
        logger.info("Bound compiled StateGraph with durable AsyncPostgresSaver.")
    except Exception as exc:
        logger.warning(
            "Could not connect to PostgreSQL database (%s). Initializing fallback checkpointer for test/offline mode.",
            exc
        )
        try:
            from langgraph.checkpoint.memory import MemorySaver
            fallback_checkpointer = MemorySaver()
            app.state.checkpointer = fallback_checkpointer
            app.state.stellar_graph = create_stellar_graph(checkpointer=fallback_checkpointer)
        except Exception:
            app.state.stellar_graph = create_stellar_graph()

    yield

    # Clean shutdown
    if pool and not pool.closed:
        logger.info("Closing PostgreSQL connection pool...")
        await pool.close()
    logger.info("STELLAR AI Microservice shutdown complete.")


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="STELLAR AI Microservice",
    description="Multi-Agent Geospatial Earth Observation Intelligence Microservice",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint verifying graph readiness and memory configuration."""
    return {
        "status": "healthy",
        "service": "stellar-ai-microservice",
        "graph_ready": hasattr(app.state, "stellar_graph"),
        "gpu_alloc_growth": os.environ.get("TF_FORCE_GPU_ALLOW_GROWTH"),
        "pytorch_alloc_conf": os.environ.get("PYTORCH_CUDA_ALLOC_CONF"),
    }


@app.post("/query/stream")
async def stream_query(request: QueryStreamRequest):
    """
    Streams multi-agent reasoning events in real-time via Server-Sent Events (SSE).
    Uses stellar_graph.astream_events(..., version="v2") with recursion_limit=8
    and session thread persistence.
    """
    if not hasattr(app.state, "stellar_graph"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stellar agent graph is not initialized."
        )

    stellar_graph = app.state.stellar_graph
    session_id = request.session_id

    async def event_generator():
        config = {
            "configurable": {"thread_id": session_id},
            "recursion_limit": 8,
        }

        initial_input: Dict[str, Any] = {
            "messages": [HumanMessage(content=request.query)],
            "intent": None,
            "missing_aoi": False,
            "aoi_bbox": request.aoi_bbox,
            "date_range": request.date_range,
            "raster_artifact_uri": None,
            "specialist_metrics": None,
            "iteration_count": 0,
            "error_state": None,
        }

        try:
            async for event in stellar_graph.astream_events(
                initial_input,
                version="v2",
                config=config,
            ):
                event_data = {
                    "event": event.get("event"),
                    "name": event.get("name"),
                    "data": event.get("data"),
                }
                yield f"data: {json.dumps(event_data, default=str)}\n\n"
        except Exception as exc:
            logger.error("Error during streaming graph execution: %s", exc, exc_info=True)
            error_payload = {
                "event": "error",
                "detail": str(exc),
            }
            yield f"data: {json.dumps(error_payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
