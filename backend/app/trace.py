"""Tiny in-memory store for the last crew run — powers the /inspect workflow view.
crewai-free so it can be read without importing the crew."""
from __future__ import annotations

LAST_RUN: dict = {}


def record(data: dict) -> None:
    global LAST_RUN
    LAST_RUN = data


def get() -> dict:
    return LAST_RUN
