"""
Stellar AI - Asynchronous Task Queue & Job State Store
Resolves the 'Synchronous Inference' bottleneck by managing:
1. Long-running VLM and GDAL inference jobs asynchronously outside the request-response cycle.
2. Distributed Redis task queue integration (Celery/RQ/Redis Streams ready).
3. Non-blocking polling (/api/v1/jobs/{job_id}) and real-time WebSocket progress updates.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_JOB_PREFIX = "stellar:job:"
REDIS_CHANNEL_PREFIX = "stellar:channel:"

# In-memory fallback dictionary for zero-dependency execution
_LOCAL_JOBS: Dict[str, Dict[str, Any]] = {}


def _get_redis_client():
    if not REDIS_AVAILABLE or not REDIS_URL:
        return None
    try:
        client = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=2.0)
        client.ping()
        return client
    except Exception:
        return None


class TaskQueueManager:
    """Manages asynchronous job lifecycle across Redis and in-memory fallback."""

    def __init__(self):
        self._redis = _get_redis_client()

    def is_redis_active(self) -> bool:
        if self._redis is not None:
            try:
                return bool(self._redis.ping())
            except Exception:
                self._redis = None
        return False

    def enqueue_job(
        self,
        job_id: str,
        query: str,
        geo_context: Optional[Dict[str, Any]] = None,
        modalities: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Register a new job in the queue with status 'queued'."""
        now = datetime.utcnow().isoformat() + "Z"
        job_data = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "query": query,
            "geo_context": geo_context or {},
            "modalities": modalities or {},
            "user_id": user_id,
            "session_id": session_id,
            "started_at": now,
            "completed_at": None,
            "error": None,
            "result": None,
        }

        if self.is_redis_active():
            try:
                key = f"{REDIS_JOB_PREFIX}{job_id}"
                self._redis.set(key, json.dumps(job_data, default=str), ex=86400)  # 24hr TTL
            except Exception:
                pass

        _LOCAL_JOBS[job_id] = job_data
        return job_data

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the current state of a job."""
        if self.is_redis_active():
            try:
                key = f"{REDIS_JOB_PREFIX}{job_id}"
                raw = self._redis.get(key)
                if raw:
                    return json.loads(raw)
            except Exception:
                pass

        return _LOCAL_JOBS.get(job_id)

    def update_job_status(
        self,
        job_id: str,
        status: str,
        progress: Optional[int] = None,
        result: Optional[Any] = None,
        error: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update job status and publish progress event."""
        job = self.get_job(job_id) or _LOCAL_JOBS.get(job_id)
        if not job:
            return None

        job["status"] = status
        if progress is not None:
            job["progress"] = progress
        if result is not None:
            job["result"] = result
        if error is not None:
            job["error"] = error
        if status in ("completed", "failed"):
            job["completed_at"] = datetime.utcnow().isoformat() + "Z"

        # Update local memory
        _LOCAL_JOBS[job_id] = job

        # Update Redis & publish event
        if self.is_redis_active():
            try:
                key = f"{REDIS_JOB_PREFIX}{job_id}"
                self._redis.set(key, json.dumps(job, default=str), ex=86400)
                channel = f"{REDIS_CHANNEL_PREFIX}{job_id}"
                self._redis.publish(channel, json.dumps({
                    "job_id": job_id,
                    "status": status,
                    "progress": job.get("progress", 0),
                    "error": error,
                    "completed_at": job.get("completed_at"),
                }, default=str))
            except Exception:
                pass

        return job


# Singleton task queue instance
task_queue = TaskQueueManager()
