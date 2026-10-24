"""
Unit tests for app.core.gpu_guard.
"""
import os
import pytest
from app.core.gpu_guard import setup_gpu_guard


def test_gpu_guard_environment_variables():
    """Verify GPU memory allocation environment variables are set."""
    assert os.environ.get("TF_FORCE_GPU_ALLOW_GROWTH") == "true"
    assert os.environ.get("PYTORCH_CUDA_ALLOC_CONF") == "expandable_segments:True"


def test_setup_gpu_guard_idempotent():
    """Verify setup_gpu_guard executes without error even if TensorFlow/Torch or GPUs are missing."""
    setup_gpu_guard()
    assert os.environ.get("TF_FORCE_GPU_ALLOW_GROWTH") == "true"
