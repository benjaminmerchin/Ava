"""Pure, dependency-free DOM analysis. Shared by the mock path and the crew."""
from __future__ import annotations

import re

from .schemas import DomSnapshot, InteractiveElement


def blocked_elements(dom: DomSnapshot) -> list[InteractiveElement]:
    return [e for e in dom.elements if e.visible and (e.disabled or e.error)]


def _name(e: InteractiveElement) -> str:
    return e.label or e.text or e.selector


def analyze_dom(dom: DomSnapshot, query: str = "") -> str:
    """Compact summary of the interface state. When a query is given, actionable
    elements are ranked by relevance to it (so the right one — e.g. 'See all plans'
    for a pricing question — surfaces instead of a generic one)."""
    lines: list[str] = []
    if dom.url:
        lines.append(f"URL: {dom.url}")
    if dom.title:
        lines.append(f"Page: {dom.title}")

    blocked = blocked_elements(dom)
    if blocked:
        lines.append("Blocked / invalid elements:")
        for e in blocked:
            why = []
            if e.disabled:
                why.append("disabled")
            if e.error:
                why.append(f"error: {e.error}")
            lines.append(f"  - {_name(e)} ({e.selector}) — {', '.join(why)}")
    else:
        lines.append("No blocked element detected.")

    actionable = [e for e in dom.elements if e.visible and not e.disabled]
    qw = [w for w in re.findall(r"[a-zàâçéèêëîïôûùü0-9]+", (query or "").lower()) if len(w) > 2]
    if qw:
        def score(e: InteractiveElement) -> int:
            hay = f"{e.label or ''} {e.text or ''} {e.selector}".lower()
            return sum(1 for w in qw if w[:4] in hay)
        actionable = sorted(actionable, key=score, reverse=True)
    actionable = actionable[:30]

    if actionable:
        lines.append("Visible actionable elements (most relevant first):")
        for e in actionable:
            lines.append(f"  - {_name(e)} ({e.selector})")

    return "\n".join(lines)
