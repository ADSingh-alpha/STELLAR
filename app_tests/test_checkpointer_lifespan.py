"""
Unit tests for app.agents.checkpointer and app.main (FastAPI lifespan & SSE streaming).
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from app.agents.checkpointer import create_postgres_pool, init_postgres_checkpointer
from app.main import app


def test_create_postgres_pool_configuration():
    """Verify AsyncConnectionPool kwargs have autocommit=True and prepare_threshold=0."""
    pool = create_postgres_pool("postgresql://test_user:test_pass@localhost:5432/test_db")
    assert pool.kwargs.get("autocommit") is True
    assert pool.kwargs.get("prepare_threshold") == 0


@pytest.mark.anyio
async def test_init_postgres_checkpointer_invokes_setup():
    """Verify init_postgres_checkpointer calls await checkpointer.setup()."""
    mock_pool = MagicMock()
    mock_pool.closed = True
    mock_pool.open = AsyncMock()

    with patch("app.agents.checkpointer.AsyncPostgresSaver") as mock_saver_cls:
        mock_saver = MagicMock()
        mock_saver.setup = AsyncMock()
        mock_saver_cls.return_value = mock_saver

        checkpointer, pool = await init_postgres_checkpointer(pool=mock_pool)

        mock_pool.open.assert_awaited_once()
        mock_saver.setup.assert_awaited_once()
        assert checkpointer == mock_saver


@pytest.mark.anyio
async def test_health_endpoint():
    """Verify health endpoint indicates service readiness and GPU allocation flags."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["gpu_alloc_growth"] == "true"
        assert data["pytorch_alloc_conf"] == "expandable_segments:True"


@pytest.mark.anyio
async def test_query_stream_sse_endpoint():
    """Verify /query/stream returns text/event-stream with LangGraph astream_events."""
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "session_id": "session-test-sse-123",
                "query": "Calculate NDVI for Bangalore agricultural fields",
                "aoi_bbox": [77.5, 12.9, 77.6, 13.0],
            }
            resp = await client.post("/query/stream", json=payload)
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers["content-type"]
            body = resp.text
            assert "data: " in body
            assert "on_chain_start" in body or "on_tool_start" in body or "on_chain_end" in body
