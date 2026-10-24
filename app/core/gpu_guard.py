"""
GPU & VRAM Isolation Guard for STELLAR AI Service.

Sets memory growth and allocation policies for TensorFlow and PyTorch
before any ML library is imported or initializes CUDA resources,
preventing CUDA out-of-memory crashes.
"""

import os
import logging

logger = logging.getLogger("stellar.gpu_guard")

# 1. Enforce environment variables BEFORE importing any ML library
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "true"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"


def setup_gpu_guard() -> None:
    """
    Safely configure TensorFlow and PyTorch GPU memory growth.
    Catches ImportError if tensorflow/torch are not present.
    """
    try:
        import tensorflow as tf
        physical_gpus = tf.config.experimental.list_physical_devices("GPU")
        if physical_gpus:
            for gpu in physical_gpus:
                try:
                    tf.config.experimental.set_memory_growth(gpu, True)
                    logger.info("TensorFlow memory growth enabled for %s", gpu)
                except Exception as exc:
                    logger.warning("Could not set TensorFlow memory growth for %s: %s", gpu, exc)
    except ImportError:
        # TensorFlow is not installed in the current environment
        pass
    except Exception as exc:
        logger.warning("Error configuring TensorFlow memory growth: %s", exc)

    try:
        import torch
        if torch.cuda.is_available():
            logger.info("PyTorch CUDA available with alloc config: %s", os.environ.get("PYTORCH_CUDA_ALLOC_CONF"))
    except ImportError:
        pass
    except Exception as exc:
        logger.warning("Error inspecting PyTorch CUDA configuration: %s", exc)


# Ensure safe setup runs on module load
setup_gpu_guard()
