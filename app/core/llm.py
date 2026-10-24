"""
app/core/llm.py

Factory for initializing the primary ChatModel for STELLAR multi-agent workflows.
Supports Google Gemini, OpenAI, or a deterministic offline fallback model.
"""

import os
import logging
from typing import Any

logger = logging.getLogger("stellar.llm")


def get_chat_model() -> Any:
    """
    Returns an initialized ChatModel.
    Checks environment for GOOGLE_API_KEY / GEMINI_API_KEY or OPENAI_API_KEY.
    Falls back to DeterministicMockLLM for offline development and testing.
    """
    # 1. Google Gemini
    google_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if google_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            model = os.getenv("STELLAR_LLM_MODEL", "gemini-1.5-pro")
            return ChatGoogleGenerativeAI(model=model, google_api_key=google_key, temperature=0.0)
        except ImportError:
            logger.warning("langchain-google-genai not installed despite API key.")

    # 2. OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from langchain_openai import ChatOpenAI
            model = os.getenv("STELLAR_LLM_MODEL", "gpt-4o")
            return ChatOpenAI(model=model, api_key=openai_key, temperature=0.0)
        except ImportError:
            logger.warning("langchain-openai not installed despite API key.")

    # 3. Deterministic Mock LLM Fallback (testing/offline)
    from app.agents.graph import DeterministicMockLLM
    return DeterministicMockLLM()
