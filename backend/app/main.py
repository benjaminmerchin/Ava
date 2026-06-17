from __future__ import annotations

import os
import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import settings
from .dom import blocked_elements
from .rag import retrieve
from .schemas import AskRequest, AvaResponse

app = FastAPI(title="Ava", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_HERE = os.path.dirname(__file__)
_WIDGET = os.path.normpath(os.path.join(_HERE, "..", "..", "widget", "ava-widget.js"))
_DEMO = os.path.normpath(os.path.join(_HERE, "..", "..", "demo", "lyvica.html"))
_FACE = os.path.normpath(os.path.join(_HERE, "..", "..", "widget", "ava-face.jpg"))


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": "crew" if settings.has_llm else "mock"}


@app.get("/widget.js")
def widget() -> FileResponse:
    return FileResponse(_WIDGET, media_type="application/javascript")


@app.get("/demo")
def demo() -> FileResponse:
    return FileResponse(_DEMO, media_type="text/html")


@app.get("/ava-face.jpg")
def ava_face() -> FileResponse:
    return FileResponse(_FACE, media_type="image/jpeg")


@app.post("/ask", response_model=AvaResponse)
def ask(req: AskRequest) -> AvaResponse:
    if settings.has_llm:
        try:
            from .ava_crew import run_ava

            return run_ava(req, deep=settings.deep_mode)
        except Exception as exc:  # never let the live demo 500
            print(f"[ava] crew failed, falling back to mock: {exc}")
    return _mock(req)


def _best_blocked(req: AskRequest):
    """Pick the blocked element most relevant to the question (stem match),
    falling back to the first blocked element."""
    blocked = blocked_elements(req.dom)
    if not blocked:
        return None
    qwords = [
        w
        for w in re.findall(r"[a-zàâçéèêëîïôûùü0-9]+", req.question.lower())
        if len(w) > 2
    ]
    best_score, best = 0, blocked[0]
    for e in blocked:
        hay = f"{e.label or ''} {e.selector} {e.text or ''}".lower()
        score = sum(1 for w in qwords if w[:5] in hay)
        if score > best_score:
            best_score, best = score, e
    return best


def _mock(req: AskRequest) -> AvaResponse:
    """Deterministic, no-LLM answer so the widget loop works before any creds.
    Also the live fallback if the crew errors. Combines DOM analysis + doc retrieval."""
    docs = retrieve(req.tenant_id, req.question, k=1)
    hint = f" (see: {docs[0].title})" if docs else ""
    target = _best_blocked(req)
    if target is not None:
        name = target.label or target.text or "this element"
        reason = target.error or "it stays disabled until a condition is met"
        return AvaResponse(
            speech=f"“{name}” is blocked because {reason}.{hint}",
            highlight_selector=target.selector,
            next_step=f"Fix “{name}” and it will enable.",
            source="mock",
        )
    return AvaResponse(
        speech="I don't see anything blocked here. Tell me what you want to do and I'll guide you."
        + hint,
        highlight_selector=None,
        next_step=docs[0].title if docs else None,
        source="mock",
    )
