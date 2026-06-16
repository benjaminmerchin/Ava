"""Tiny dependency-free retriever over per-tenant markdown docs.

Good enough for the demo corpus (5-6 pages). TODO(prod): swap for pgvector
embeddings namespaced by tenant_id, fed by the offline ingestion crew.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

from .config import settings

_STOP = set(
    "le la les un une des de du et a à en pour que qui est se ne pas sur dans "
    "je tu il elle on nous vous ils mon ma mes ton ta tes son sa ses ce cette".split()
)


@dataclass
class Section:
    title: str
    text: str
    source: str


def _tokenize(s: str) -> list[str]:
    words = re.findall(r"[a-zàâçéèêëîïôûùüÿñæœ0-9]+", s.lower())
    return [w for w in words if w not in _STOP and len(w) > 2]


def _load_sections(tenant_id: str) -> list[Section]:
    base = os.path.normpath(os.path.join(settings.docs_root, tenant_id))
    sections: list[Section] = []
    if not os.path.isdir(base):
        return sections
    for fn in sorted(os.listdir(base)):
        if not fn.endswith(".md"):
            continue
        with open(os.path.join(base, fn), encoding="utf-8") as f:
            content = f.read()
        for part in re.split(r"(?m)^#{1,3}\s+", content):
            part = part.strip()
            if not part:
                continue
            title = part.splitlines()[0].strip()
            sections.append(Section(title=title, text=part, source=fn))
    return sections


def retrieve(tenant_id: str, query: str, k: int = 3) -> list[Section]:
    sections = _load_sections(tenant_id)
    if not sections:
        return []
    q = set(_tokenize(query))
    scored: list[tuple[int, Section]] = []
    for s in sections:
        toks = _tokenize(s.title) * 2 + _tokenize(s.text)
        score = sum(toks.count(w) for w in q)
        scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [s for score, s in scored[:k] if score > 0]
    return top or [scored[0][1]]
