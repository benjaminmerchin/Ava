"""LLM factory — every call routes through the TrueFoundry AI Gateway
(OpenAI-compatible), so we get observability + multi-model access. crewai is
imported lazily so the API still boots (mock mode) without it."""
from __future__ import annotations

import os

from .config import settings


def _gateway_model(model: str) -> str:
    """litellm routes ``openai/<x>`` to an OpenAI-compatible endpoint, sending
    ``<x>`` as the model to the TF gateway (e.g. ``anthropic/claude-opus-4-8``)."""
    return model if model.startswith("openai/") else f"openai/{model}"


def get_llm(model: str):
    from crewai import LLM

    # CrewAI doesn't reliably forward api_key/base_url to litellm for custom
    # "openai/" models — litellm's OpenAI-compatible provider reads these env vars.
    os.environ["OPENAI_API_KEY"] = settings.tfy_api_key
    os.environ["OPENAI_API_BASE"] = settings.tfy_base_url
    os.environ["OPENAI_BASE_URL"] = settings.tfy_base_url

    return LLM(
        model=_gateway_model(model),
        base_url=settings.tfy_base_url,
        api_key=settings.tfy_api_key,
        temperature=0.2,
    )
