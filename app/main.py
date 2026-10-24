# app/main.py
from app.core.gpu_guard import configure_gpu_memory
configure_gpu_memory()  # MUST run before any ML imports

import os
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional, Tuple, Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.agents.graph import build_stellar_graph

logger = logging.getLogger("stellar.main")
DB_URI = os.getenv("DATABASE_URL", "postgresql://stellar:password@localhost:5432/stellar_geodb")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with AsyncConnectionPool(
            conninfo=DB_URI,
            max_size=10,
            timeout=2.0,
            kwargs={"autocommit": True, "prepare_threshold": 0},
        ) as pool:
            checkpointer = AsyncPostgresSaver(pool)
            await checkpointer.setup()
            # Inject your configured ChatModel (e.g., ChatGoogleGenerativeAI / ChatOpenAI)
            from app.core.llm import get_chat_model
            llm = get_chat_model()
            app.state.stellar_graph = build_stellar_graph(llm=llm, checkpointer=checkpointer)
            yield
    except Exception as exc:
        logger.warning("PostgreSQL unavailable or offline (%s); using in-memory checkpointer fallback.", exc)
        from app.core.llm import get_chat_model
        llm = get_chat_model()
        from langgraph.checkpoint.memory import MemorySaver
        checkpointer = MemorySaver()
        app.state.stellar_graph = build_stellar_graph(llm=llm, checkpointer=checkpointer)
        yield


app = FastAPI(title="STELLAR AI Agentic Service", lifespan=lifespan)

# CORS middleware for frontend UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentQueryRequest(BaseModel):
    session_id: str
    query: str
    aoi_bbox: Optional[Tuple[float, float, float, float]] = None


# Alias for backward-compatibility with earlier API clients
QueryStreamRequest = AgentQueryRequest


@app.get("/health")
async def health_check():
    """Health status and configuration verification."""
    return {
        "status": "healthy",
        "service": "stellar-ai-service",
        "graph_ready": hasattr(app.state, "stellar_graph"),
        "gpu_alloc_growth": os.environ.get("TF_FORCE_GPU_ALLOW_GROWTH"),
        "pytorch_alloc_conf": os.environ.get("PYTORCH_CUDA_ALLOC_CONF"),
    }


@app.post("/ai/stream")
async def stream_agent_response(payload: AgentQueryRequest):
    config = {
        "configurable": {"thread_id": payload.session_id},
        "recursion_limit": 8,
    }
    initial_input = {
        "messages": [("user", payload.query)],
        "aoi_bbox": payload.aoi_bbox,
        "iteration_count": 0,
    }

    async def event_stream():
        async for event in app.state.stellar_graph.astream_events(
            initial_input, config=config, version="v2"
        ):
            kind = event["event"]
            if kind == "on_chain_start" and event["name"] in {"classifier", "specialist", "tools", "synthesizer"}:
                yield f"data: {json.dumps({'type': 'node_transition', 'node': event['name']})}\n\n"
            elif kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
            elif kind == "on_tool_end":
                yield f"data: {json.dumps({'type': 'tool_completed', 'tool': event['name']})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# Backward-compatible endpoint route
@app.post("/query/stream")
async def stream_query_alias(payload: AgentQueryRequest):
    return await stream_agent_response(payload)
