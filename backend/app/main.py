from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import settings
from .dom import analyze_dom, blocked_elements
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

_WIDGET = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "widget", "ava-widget.js")
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": "crew" if settings.has_llm else "mock"}


@app.get("/widget.js")
def widget() -> FileResponse:
    return FileResponse(_WIDGET, media_type="application/javascript")


@app.post("/ask", response_model=AvaResponse)
def ask(req: AskRequest) -> AvaResponse:
    if settings.has_llm:
        try:
            from .ava_crew import run_ava

            return run_ava(req, deep=settings.deep_mode)
        except Exception as exc:  # never let the live demo 500
            print(f"[ava] crew failed, falling back to mock: {exc}")
    return _mock(req)


def _mock(req: AskRequest) -> AvaResponse:
    """Deterministic, no-LLM answer so the widget loop works before any creds.
    Still 'smart': combines DOM analysis with doc retrieval."""
    docs = retrieve(req.tenant_id, req.question, k=1)
    hint = f" (voir : {docs[0].title})" if docs else ""
    blocked = blocked_elements(req.dom)
    if blocked:
        e = blocked[0]
        name = e.label or e.text or "cet élément"
        reason = e.error or "il est désactivé tant qu'une condition n'est pas remplie"
        return AvaResponse(
            speech=f"« {name} » est bloqué parce que {reason}.{hint}",
            highlight_selector=e.selector,
            next_step=f"Corrige « {name} » et il s'activera.",
            source="mock",
        )
    return AvaResponse(
        speech="Je ne détecte pas de blocage ici. Dis-moi ce que tu veux faire et je te guide." + hint,
        highlight_selector=None,
        next_step=docs[0].title if docs else None,
        source="mock",
    )
