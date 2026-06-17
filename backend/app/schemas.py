from typing import Any, Optional

from pydantic import BaseModel, Field


class InteractiveElement(BaseModel):
    selector: str
    tag: Optional[str] = None
    label: Optional[str] = None
    text: Optional[str] = None
    disabled: bool = False
    visible: bool = True
    error: Optional[str] = None
    aria: dict[str, Any] = Field(default_factory=dict)


class DomSnapshot(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    elements: list[InteractiveElement] = Field(default_factory=list)


class AskRequest(BaseModel):
    tenant_id: str = "lyvica"
    url: Optional[str] = None
    question: str
    dom: DomSnapshot = Field(default_factory=DomSnapshot)
    history: list[dict[str, str]] = Field(default_factory=list)
    screenshot: Optional[str] = None  # base64, vision fallback (optional)
    inject_fail: bool = False  # demo: force the primary model to fail (show the fallback live)
    deep: Optional[bool] = None  # force the 3-agent crew for this request (else AVA_DEEP_MODE)


class AvaResponse(BaseModel):
    """The strict contract Ava speaks. highlight_selector/next_step may be null."""

    speech: str
    highlight_selector: Optional[str] = None
    next_step: Optional[str] = None
    source: str = "crew"  # "crew" | "mock" | "fallback"
    model: Optional[str] = None  # which gateway model answered
    fell_back: bool = False  # true if the primary model failed and we failed over


class TtsRequest(BaseModel):
    text: str
