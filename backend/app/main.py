from __future__ import annotations

import os
import re

import httpx
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import trace
from .config import settings
from .dom import blocked_elements
from .rag import retrieve
from .schemas import AskRequest, AvaResponse, TtsRequest

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
_AVATAR_HTML = os.path.normpath(os.path.join(_HERE, "..", "..", "widget", "avatar.html"))
_AVATAR_GLB = os.path.normpath(os.path.join(_HERE, "..", "..", "widget", "ava-avatar.glb"))
_INSPECT = os.path.normpath(os.path.join(_HERE, "..", "..", "widget", "inspect.html"))
_SLIDES = os.path.normpath(os.path.join(_HERE, "..", "..", "slides"))

if os.path.isdir(_SLIDES):
    app.mount("/slides", StaticFiles(directory=_SLIDES, html=True), name="slides")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "mode": "crew" if settings.has_llm else "mock",
        "tts": settings.has_tts,
        "model": settings.model_primary,
    }


@app.get("/widget.js")
def widget() -> FileResponse:
    return FileResponse(_WIDGET, media_type="application/javascript")


@app.get("/demo")
def demo() -> FileResponse:
    return FileResponse(_DEMO, media_type="text/html")


@app.get("/ava-face.jpg")
def ava_face() -> FileResponse:
    return FileResponse(_FACE, media_type="image/jpeg")


@app.get("/avatar")
def avatar() -> FileResponse:
    return FileResponse(_AVATAR_HTML, media_type="text/html")


@app.get("/ava-avatar.glb")
def avatar_glb() -> FileResponse:
    return FileResponse(_AVATAR_GLB, media_type="model/gltf-binary")


@app.get("/inspect")
def inspect() -> FileResponse:
    """Live view of the last multi-agent crew run."""
    return FileResponse(_INSPECT, media_type="text/html")


@app.get("/last-run")
def last_run() -> dict:
    return trace.get()


@app.post("/tts")
def tts(req: TtsRequest) -> Response:
    """ElevenLabs TTS (direct — the TF gateway has no audio). Returns MP3 audio."""
    if not settings.has_tts or not req.text.strip():
        return Response(status_code=204)
    try:
        r = httpx.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{settings.eleven_voice_id}",
            headers={"xi-api-key": settings.eleven_api_key, "accept": "audio/mpeg"},
            json={
                "text": req.text,
                "model_id": settings.eleven_model,
                "voice_settings": {"stability": 0.45, "similarity_boost": 0.8},
            },
            timeout=30,
        )
    except Exception as exc:  # network error
        print(f"[ava] tts error: {exc}")
        return Response(status_code=502)
    if r.status_code != 200:
        print(f"[ava] tts {r.status_code}: {r.text[:200]}")
        return Response(status_code=502)
    return Response(content=r.content, media_type="audio/mpeg")


@app.post("/ask", response_model=AvaResponse)
def ask(req: AskRequest) -> AvaResponse:
    if settings.has_llm:
        try:
            from .ava_crew import run_ava

            deep = req.deep if req.deep is not None else settings.deep_mode
            return run_ava(req, deep=deep)
        except Exception as exc:  # never let the live demo 500
            print(f"[ava] crew failed, falling back to mock: {exc}")
    return _mock(req)


def _best_blocked(req: AskRequest):
    """Pick the blocked element most relevant to the question (stem match)."""
    blocked = blocked_elements(req.dom)
    if not blocked:
        return None
    qwords = [
        w for w in re.findall(r"[a-zàâçéèêëîïôûùü0-9]+", req.question.lower()) if len(w) > 2
    ]
    best_score, best = 0, blocked[0]
    for e in blocked:
        hay = f"{e.label or ''} {e.selector} {e.text or ''}".lower()
        score = sum(1 for w in qwords if w[:5] in hay)
        if score > best_score:
            best_score, best = score, e
    return best


def _mock(req: AskRequest) -> AvaResponse:
    """Deterministic fallback (no LLM) — also the live safety net if the crew errors."""
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
