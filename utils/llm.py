"""
Shared LLM factory.
All agent nodes import `get_llm()` so the model is configured in one place.
"""

from __future__ import annotations

from functools import lru_cache
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.3) -> ChatOpenAI:
    """Return a cached ChatOpenAI instance."""
    return ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=temperature,
        api_key=OPENAI_API_KEY,
    )
