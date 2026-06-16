"""LLM factory — every call routes through the TrueFoundry AI Gateway
(OpenAI-compatible), so we get observability, fallbacks and guardrails for free.

crewai is imported lazily so the API still boots (in mock mode) without it.
"""
from __future__ import annotations

from .config import settings


def get_llm(deep: bool = False):
    from crewai import LLM

    return LLM(
        model=settings.llm_model,
        base_url=settings.llm_base_url or None,
        api_key=settings.llm_api_key or None,
        temperature=0.2,
    )
