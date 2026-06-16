"""Ava's runtime crew, two modes:

- LEAN (default, live demo): one agent, one LLM call. DOM analysis + doc retrieval
  are done deterministically in Python and injected — fast (~one round-trip).
- DEEP (AVA_DEEP_MODE=true): Perception ∥ Knowledge → Guide, a real 3-agent crew
  showcasing CrewAI orchestration (for the pitch / eval comparison).

Both return the strict structured response Ava speaks.
"""
from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from .dom import analyze_dom
from .llm import get_llm
from .rag import retrieve
from .schemas import AskRequest, AvaResponse
from .tools import make_doc_search_tool

_GUIDE_BACKSTORY = (
    "Assistant de support qui explique le POURQUOI et désigne l'élément à corriger "
    "(la cause racine) — sans jamais cliquer à la place de l'utilisateur."
)

_OUTPUT_SPEC = (
    "Produis la réponse d'Ava, en français:\n"
    "- speech: explication courte et naturelle (1-2 phrases) qui dit le POURQUOI.\n"
    "- highlight_selector: le sélecteur CSS de l'élément à corriger (la CAUSE racine), ou null.\n"
    "- next_step: la prochaine action concrète pour l'utilisateur, ou null.\n"
    "Ne propose jamais de cliquer à la place de l'utilisateur."
)


def _lean_crew(req: AskRequest) -> Crew:
    """One agent, one LLM call — context injected for low latency."""
    llm = get_llm()
    state = analyze_dom(req.dom)
    docs = retrieve(req.tenant_id, req.question, k=3)
    doc_text = (
        "\n\n".join(f"[{s.source} · {s.title}]\n{s.text}" for s in docs)
        or "(aucune documentation pertinente)"
    )

    ava = Agent(
        role="Ava",
        goal="Guider l'utilisateur pas à pas, en français, clairement et brièvement.",
        backstory=_GUIDE_BACKSTORY,
        llm=llm, verbose=False, allow_delegation=False,
    )
    task = Task(
        description=(
            f"Question de l'utilisateur: {req.question}\n\n"
            f"État de l'interface:\n{state}\n\n"
            f"Documentation produit pertinente:\n{doc_text}\n\n"
            f"{_OUTPUT_SPEC}"
        ),
        expected_output="Objet structuré: speech / highlight_selector / next_step.",
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
        goal="Diagnostiquer l'état de l'interface et pourquoi un élément est bloqué.",
        backstory="Expert qui lit l'état du DOM pour comprendre la logique métier de l'app.",
        llm=llm, verbose=False, allow_delegation=False,
    )
    knowledge = Agent(
        role="Doc Expert",
        goal="Retrouver dans la doc produit les étapes et règles utiles à la question.",
        backstory="Connaît la documentation du produit et sait quelle section répond à chaque situation.",
        llm=llm, tools=[doc_tool], verbose=False, allow_delegation=False,
    )
    guide = Agent(
        role="Coach", goal="Guider l'utilisateur pas à pas, en français.",
        backstory=_GUIDE_BACKSTORY, llm=llm, verbose=False, allow_delegation=False,
    )

    t_perception = Task(
        description=(
            f"Question: {req.question}\n\nÉtat de l'interface:\n{state}\n\n"
            "Identifie l'élément concerné et explique pourquoi il est bloqué. "
            "Donne le sélecteur CSS de la cause racine s'il existe."
        ),
        expected_output="Diagnostic court: élément, sélecteur, raison du blocage.",
        agent=perception, async_execution=True,
    )
    t_knowledge = Task(
        description=(
            f"Question: {req.question}\n\nContexte:\n{state}\n\n"
            "Utilise doc_search pour trouver les étapes/règles pertinentes. Résume-les."
        ),
        expected_output="Étapes/règles pertinentes de la documentation.",
        agent=knowledge, async_execution=True,
    )
    t_guide = Task(
        description=f"Question: {req.question}\n\n{_OUTPUT_SPEC}",
        expected_output="Objet structuré: speech / highlight_selector / next_step.",
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
