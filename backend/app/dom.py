"""Pure, dependency-free DOM analysis. Shared by the mock path and the crew."""
from __future__ import annotations

from .schemas import DomSnapshot, InteractiveElement


def blocked_elements(dom: DomSnapshot) -> list[InteractiveElement]:
    return [e for e in dom.elements if e.visible and (e.disabled or e.error)]


def analyze_dom(dom: DomSnapshot) -> str:
    """Compact, human-readable summary of the interface state for the LLM / mock."""
    lines: list[str] = []
    if dom.url:
        lines.append(f"URL: {dom.url}")
    if dom.title:
        lines.append(f"Page: {dom.title}")

    blocked = blocked_elements(dom)
    if blocked:
        lines.append("Éléments bloqués / en erreur:")
        for e in blocked:
            why = []
            if e.disabled:
                why.append("désactivé")
            if e.error:
                why.append(f"erreur: {e.error}")
            name = e.label or e.text or e.selector
            lines.append(f"  - {name} ({e.selector}) — {', '.join(why)}")
    else:
        lines.append("Aucun élément bloqué détecté.")

    actionable = [e for e in dom.elements if e.visible and not e.disabled][:15]
    if actionable:
        lines.append("Éléments actionnables visibles:")
        for e in actionable:
            name = e.label or e.text or e.selector
            lines.append(f"  - {name} ({e.selector})")

    return "\n".join(lines)
