"""CrewAI tools. Only imported when the real crew runs (keeps boot light)."""
from __future__ import annotations

from crewai.tools import tool

from .rag import retrieve


def make_doc_search_tool(tenant_id: str):
    """Builds a doc_search tool bound to a tenant's corpus (closure over tenant_id)."""

    @tool("doc_search")
    def doc_search(query: str) -> str:
        """Recherche dans la documentation produit du tenant les sections
        pertinentes (étapes d'un flow, raisons de blocage)."""
        sections = retrieve(tenant_id, query, k=3)
        if not sections:
            return "Aucune section de documentation pertinente trouvée."
        return "\n\n---\n\n".join(
            f"[{s.source} · {s.title}]\n{s.text}" for s in sections
        )

    return doc_search
