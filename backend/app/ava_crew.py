"""Ava's runtime crew (LEAN default / DEEP), with a TrueFoundry model fallback chain.

Every model in the chain is served through the TrueFoundry gateway; if one fails
(gated, rate-limited, down) we fail over to the next. On total failure the API
falls back to the deterministic mock. Each run is recorded for the /inspect view.
"""
from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from . import trace
from .config import settings
from .dom import analyze_dom
from .llm import get_llm
from .rag import retrieve
from .schemas import AskRequest, AvaResponse
from .tools import make_doc_search_tool

_GUIDE_BACKSTORY = (
    "A support assistant that explains the WHY and points at the element to act on "
    "(the root cause) — and never clicks on the user's behalf."
)

_OUTPUT_SPEC = (
    "Produce Ava's answer, in English:\n"
    "- speech: a short, natural explanation (1-2 sentences) that directly answers the user.\n"
    "- highlight_selector: the CSS selector of the single MOST relevant element for the user's goal. "
    "Prefer a specific matching action (e.g. a 'See all plans' button for a pricing question) over a "
    "generic one (e.g. 'Settings'). Use an exact selector from the interface state; null if none fits.\n"
    "- next_step: the concrete next action for the user, or null.\n"
    "Never offer to click on the user's behalf."
)


def _lean_crew(req: AskRequest, model: str) -> Crew:
    """One agent, one LLM call — context injected for low latency."""
    llm = get_llm(model)
    state = analyze_dom(req.dom, req.question)
    docs = retrieve(req.tenant_id, req.question, k=3)
    doc_text = (
        "\n\n".join(f"[{s.source} · {s.title}]\n{s.text}" for s in docs)
        or "(no relevant documentation)"
    )

    ava = Agent(
        role="Ava",
        goal="Guide the user step by step, in English, clearly and briefly.",
        backstory=_GUIDE_BACKSTORY,
        llm=llm, verbose=False, allow_delegation=False,
    )
    task = Task(
        description=(
            f"User question: {req.question}\n\n"
            f"Interface state:\n{state}\n\n"
            f"Relevant product documentation:\n{doc_text}\n\n"
            f"{_OUTPUT_SPEC}"
        ),
        expected_output="Structured object: speech / highlight_selector / next_step.",
        agent=ava, output_pydantic=AvaResponse,
    )
    return Crew(agents=[ava], tasks=[task], process=Process.sequential, verbose=False)


def _deep_crew(req: AskRequest, model: str) -> Crew:
    """Perception ∥ Knowledge → Guide — real 3-agent orchestration."""
    llm = get_llm(model)
    state = analyze_dom(req.dom, req.question)
    doc_tool = make_doc_search_tool(req.tenant_id)

    perception = Agent(
        role="Perception",
        goal="Diagnose the interface state and which element matches the user's goal.",
        backstory="An expert that reads the DOM state to understand the app's business logic.",
        llm=llm, verbose=False, allow_delegation=False,
    )
    knowledge = Agent(
        role="Knowledge",
        goal="Find the steps and rules in the product docs relevant to the question.",
        backstory="Knows the product documentation and which section answers each situation.",
        llm=llm, tools=[doc_tool], verbose=False, allow_delegation=False,
    )
    guide = Agent(
        role="Guide", goal="Guide the user step by step, in English.",
        backstory=_GUIDE_BACKSTORY, llm=llm, verbose=False, allow_delegation=False,
    )

    t_perception = Task(
        description=(
            f"User question: {req.question}\n\nInterface state:\n{state}\n\n"
            "Identify the single most relevant element for the user's goal and explain why. "
            "Give its exact CSS selector."
        ),
        expected_output="Short diagnosis: element, selector, reason.",
        agent=perception, async_execution=True,
    )
    t_knowledge = Task(
        description=(
            f"User question: {req.question}\n\nContext:\n{state}\n\n"
            "Use doc_search to find the relevant steps/rules. Summarize them."
        ),
        expected_output="Relevant steps/rules from the documentation.",
        agent=knowledge, async_execution=True,
    )
    t_guide = Task(
        description=f"User question: {req.question}\n\n{_OUTPUT_SPEC}",
        expected_output="Structured object: speech / highlight_selector / next_step.",
        agent=guide, context=[t_perception, t_knowledge], output_pydantic=AvaResponse,
    )
    return Crew(
        agents=[perception, knowledge, guide],
        tasks=[t_perception, t_knowledge, t_guide],
        process=Process.sequential, verbose=False,
    )


def _to_response(result) -> AvaResponse:
    out = getattr(result, "pydantic", None)
    if isinstance(out, AvaResponse):
        return out
    raw = getattr(result, "json_dict", None) or {}
    return AvaResponse(
        speech=raw.get("speech") or str(result),
        highlight_selector=raw.get("highlight_selector"),
        next_step=raw.get("next_step"),
    )


def _record(req: AskRequest, result, model: str, resp: AvaResponse, deep: bool) -> None:
    trace.record(
        {
            "question": req.question,
            "mode": "deep" if deep else "lean",
            "model": model,
            "fell_back": resp.fell_back,
            "agents": [
                {
                    "agent": getattr(to, "agent", None) or "Agent",
                    "output": (getattr(to, "raw", None) or str(to))[:1400],
                }
                for to in (getattr(result, "tasks_output", None) or [])
            ],
            "answer": {
                "speech": resp.speech,
                "highlight_selector": resp.highlight_selector,
                "next_step": resp.next_step,
            },
        }
    )


def run_ava(req: AskRequest, deep: bool = False) -> AvaResponse:
    """Try each model in the TrueFoundry chain; fail over to the next on error."""
    chain = settings.model_chain or ([settings.model_primary] if settings.model_primary else [])
    if req.inject_fail:  # demo hook: force a failover to show resilience live
        chain = ["anthropic/__force_fail__", *chain]
    last_err: Exception | None = None
    for i, model in enumerate(chain):
        try:
            crew = _deep_crew(req, model) if deep else _lean_crew(req, model)
            result = crew.kickoff()
            resp = _to_response(result)
            resp.source = "crew"
            resp.model = model
            resp.fell_back = i > 0
            _record(req, result, model, resp, deep)
            if i > 0:
                print(f"[ava] primary failed → answered by fallback: {model}")
            return resp
        except Exception as e:  # noqa: BLE001 — try the next model in the chain
            last_err = e
            print(f"[ava] model {model!r} failed: {type(e).__name__}: {str(e)[:160]} — trying next")
    raise last_err or RuntimeError("no models in chain")
