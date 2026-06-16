"""LLM factory — every call routes through the TrueFoundry AI Gateway
(OpenAI-compatible → AWS Bedrock), so we get observability, fallbacks and
guardrails for free, exactly like the lyvica-resilient-agent.

crewai is imported lazily so the API still boots (in mock mode) without it.
"""
from __future__ import annotations

from .config import settings


def _gateway_model(model: str) -> str:
    """litellm routes ``openai/<x>`` to an OpenAI-compatible endpoint, sending
    ``<x>`` as the model name to the TF gateway (e.g. ``aws-bedrock/us.anthropic...``)."""
    return model if model.startswith("openai/") else f"openai/{model}"


def get_llm(deep: bool = False):
    from crewai import LLM

    return LLM(
        model=_gateway_model(settings.model_primary),
        base_url=settings.tfy_base_url,
        api_key=settings.tfy_api_key,
        temperature=0.2,
    )
