"""The Ava runtime crew: Perception ∥ Knowledge → Guide.

Perception and Knowledge run in parallel (async tasks); Guide reconciles them
into the strict structured response Ava speaks.
"""
from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from .dom import analyze_dom
from .llm import get_llm
from .schemas import AskRequest, AvaResponse
from .tools import make_doc_search_tool


def _build_crew(req: AskRequest, deep: bool) -> Crew:
    llm = get_llm(deep=deep)
    state_summary = analyze_dom(req.dom)
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
        role="Coach",
        goal="Guider l'utilisateur pas à pas, en français, clairement et brièvement.",
        backstory=(
            "Assistant de support qui explique le POURQUOI et désigne l'élément à corriger "
            "— sans jamais cliquer à la place de l'utilisateur."
        ),
        llm=llm, verbose=False, allow_delegation=False,
    )

    t_perception = Task(
        description=(
            f"Question de l'utilisateur: {req.question}\n\n"
            f"État de l'interface:\n{state_summary}\n\n"
            "Identifie l'élément concerné et explique précisément pourquoi il est bloqué "
            "(ou ce qu'il faut faire). Donne le sélecteur CSS de l'élément concerné s'il existe."
        ),
        expected_output="Diagnostic court: élément concerné, son sélecteur, et la raison du blocage.",
        agent=perception, async_execution=True,
    )
    t_knowledge = Task(
        description=(
            f"Question de l'utilisateur: {req.question}\n\n"
            f"Contexte d'interface:\n{state_summary}\n\n"
            "Utilise l'outil doc_search pour trouver les étapes/règles de la doc produit "
            "qui répondent à la question. Résume les points pertinents."
        ),
        expected_output="Les étapes/règles pertinentes extraites de la documentation.",
        agent=knowledge, async_execution=True,
    )
    t_guide = Task(
        description=(
            f"Question de l'utilisateur: {req.question}\n\n"
            "À partir du diagnostic d'interface et de la documentation, produis la réponse d'Ava:\n"
            "- speech: explication courte et naturelle en français (1-2 phrases) qui dit le POURQUOI.\n"
            "- highlight_selector: le sélecteur CSS de l'élément à surligner, ou null.\n"
            "- next_step: la prochaine action concrète pour l'utilisateur, ou null.\n"
            "Ne propose jamais de cliquer à la place de l'utilisateur."
        ),
        expected_output="Objet structuré: speech / highlight_selector / next_step.",
        agent=guide, context=[t_perception, t_knowledge], output_pydantic=AvaResponse,
    )

    return Crew(
        agents=[perception, knowledge, guide],
        tasks=[t_perception, t_knowledge, t_guide],
        process=Process.sequential,
        verbose=False,
    )


def run_ava(req: AskRequest, deep: bool = False) -> AvaResponse:
    result = _build_crew(req, deep=deep).kickoff()

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
