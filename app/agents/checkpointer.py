"""
Durable PostgreSQL Checkpointing for STELLAR AI.

Replaces ephemeral MemorySaver and custom DB session glue with AsyncPostgresSaver
backed by psycopg_pool.AsyncConnectionPool with autocommit=True and prepare_threshold=0.
"""

import os
import logging
from typing import Optional, Tuple, Any
import psycopg_pool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

logger = logging.getLogger("stellar.checkpointer")


def create_postgres_pool(
    conninfo: Optional[str] = None,
    min_size: int = 1,
    max_size: Optional[int] = 10,
    timeout: float = 2.0,
) -> psycopg_pool.AsyncConnectionPool:
    """
    Creates an AsyncConnectionPool configured with autocommit=True and prepare_threshold=0
    for durable, non-leaking LangGraph state checkpointing.
    """
    db_url = conninfo or os.environ.get(
        "DATABASE_URL",
        "postgresql://stellar_user:stellar_password@localhost:5432/stellar"
    )
    # Normalize postgres:// scheme to postgresql:// for psycopg3
    if db_url.startswith("postgres://"):
        db_url = "postgresql://" + db_url[len("postgres://"):]

    return psycopg_pool.AsyncConnectionPool(
        conninfo=db_url,
        min_size=min_size,
        max_size=max_size,
        timeout=timeout,
        kwargs={"autocommit": True, "prepare_threshold": 0},
        open=False,
    )


async def init_postgres_checkpointer(
    pool: Optional[psycopg_pool.AsyncConnectionPool] = None,
    conninfo: Optional[str] = None,
) -> Tuple[AsyncPostgresSaver, psycopg_pool.AsyncConnectionPool]:
    """
    Constructs AsyncPostgresSaver, opens connection pool, and executes
    database setup migrations (checkpointer.setup()).
    """
    if pool is None:
        pool = create_postgres_pool(conninfo)

    if pool.closed:
        await pool.open()

    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()
    logger.info("AsyncPostgresSaver successfully initialized with database schema.")
    return checkpointer, pool
