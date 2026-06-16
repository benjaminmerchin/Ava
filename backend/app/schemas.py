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


class AvaResponse(BaseModel):
    """The strict contract Ava speaks. highlight_selector/next_step may be null."""

    speech: str
    highlight_selector: Optional[str] = None
    next_step: Optional[str] = None
    source: str = "crew"  # "crew" | "mock" | "fallback"
