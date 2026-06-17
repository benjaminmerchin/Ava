"""Ava's runtime crew, two modes:

- LEAN (default, live demo): one agent, one LLM call. DOM analysis + doc retrieval
  are done deterministically in Python and injected — fast (~one round-trip).
- DEEP (AVA_DEEP_MODE=true): Perception ∥ Knowledge → Guide, a real 3-agent crew
  showcasing CrewAI orchestration (for the pitch / eval comparison).

Both return the strict structured response Ava speaks (in English).
"""
from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from .dom import analyze_dom
from .llm import get_llm
from .rag import retrieve
from .schemas import AskRequest, AvaResponse
from .tools import make_doc_search_tool

_GUIDE_BACKSTORY = (
    "A support assistant that explains the WHY and points at the element to fix "
    "(the root cause) — and never clicks on the user's behalf."
)

_OUTPUT_SPEC = (
    "Produce Ava's answer, in English:\n"
    "- speech: a short, natural explanation (1-2 sentences) that says WHY.\n"
    "- highlight_selector: the CSS selector of the element to fix (the ROOT CAUSE), or null.\n"
    "- next_step: the concrete next action for the user, or null.\n"
    "Never offer to click on the user's behalf."
)


def _lean_crew(req: AskRequest) -> Crew:
    """One agent, one LLM call — context injected for low latency."""
    llm = get_llm()
    state = analyze_dom(req.dom)
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


def _deep_crew(req: AskRequest) -> Crew:
    """Perception ∥ Knowledge → Guide — real 3-agent orchestration."""
    llm = get_llm(deep=True)
    state = analyze_dom(req.dom)
    doc_tool = make_doc_search_tool(req.tenant_id)

    perception = Agent(
        role="State Reader",
        goal="Diagnose the interface state and why an element is blocked.",
        backstory="An expert that reads the DOM state to understand the app's business logic.",
        llm=llm, verbose=False, allow_delegation=False,
    )
    knowledge = Agent(
        role="Doc Expert",
        goal="Find the steps and rules in the product docs relevant to the question.",
        backstory="Knows the product documentation and which section answers each situation.",
        llm=llm, tools=[doc_tool], verbose=False, allow_delegation=False,
    )
    guide = Agent(
        role="Coach", goal="Guide the user step by step, in English.",
        backstory=_GUIDE_BACKSTORY, llm=llm, verbose=False, allow_delegation=False,
    )

    t_perception = Task(
        description=(
            f"User question: {req.question}\n\nInterface state:\n{state}\n\n"
            "Identify the element involved and explain why it is blocked. "
            "Give the CSS selector of the root cause if one exists."
        ),
        expected_output="Short diagnosis: element, selector, reason it's blocked.",
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


def run_ava(req: AskRequest, deep: bool = False) -> AvaResponse:
    crew = _deep_crew(req) if deep else _lean_crew(req)
    result = crew.kickoff()

    out = getattr(result, "pydantic", None)
    if isinstance(out, AvaResponse):
        out.source = "crew"
        return out

    raw = getattr(result, "json_dict", None) or {}
    return AvaResponse(
        speech=raw.get("speech") or str(result),
        highlight_selector=raw.get("highlight_selector"),
        next_step=raw.get("next_step"),
        source="crew",
    )
