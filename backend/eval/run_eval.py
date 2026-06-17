"""Ava eval harness — replays fixed scenarios against /ask, scores the structured
answers, and prints a reliability scoreboard.

Deterministic metrics (no creds needed): does Ava answer, highlight the right element,
and ground the answer in the expected reason? Runs against mock OR the live crew, and
against prod once deployed:

    python -m eval.run_eval                       # http://localhost:8000
    AVA_URL=https://ava.../  python -m eval.run_eval
"""
from __future__ import annotations

import json
import os
import urllib.request

from eval.scenarios import SCENARIOS

AVA_URL = os.getenv("AVA_URL", "http://localhost:8000").rstrip("/")
_METRICS = ("answered", "selector", "grounded")


def _ask(scenario: dict) -> dict:
    body = json.dumps(
        {"tenant_id": "lyvica", "question": scenario["question"], "dom": scenario["dom"]}
    ).encode()
    req = urllib.request.Request(
        AVA_URL + "/ask", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def _score(scenario: dict, resp: dict) -> dict:
    speech = (resp.get("speech") or "").lower()
    return {
        "answered": bool(speech.strip()),
        "selector": resp.get("highlight_selector") in scenario["expect_selectors"],
        "grounded": (not scenario["expect_keywords"])
        or any(k in speech for k in scenario["expect_keywords"]),
    }


def _mark(b: bool) -> str:
    return "✓" if b else "✗"


def main() -> None:
    n = len(SCENARIOS)
    totals = {m: 0 for m in _METRICS}
    src = None
    print(f"\n  Ava reliability eval — {AVA_URL}  ({n} scenarios)\n")
    for s in SCENARIOS:
        try:
            resp = _ask(s)
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {s['name']:<28} request failed: {e}")
            continue
        src = resp.get("source")
        checks = _score(s, resp)
        for m in _METRICS:
            totals[m] += int(checks[m])
        print(
            f"  {_mark(all(checks.values()))} {s['name']:<28} "
            f"answered:{_mark(checks['answered'])} "
            f"selector:{_mark(checks['selector'])} "
            f"grounded:{_mark(checks['grounded'])}"
        )
        print(f"      → {resp.get('speech')}")
    print(f"\n  mode: {src}")
    for m in _METRICS:
        print(f"  {m:<10} {totals[m]}/{n}  ({100 * totals[m] // n}%)")
    overall = sum(totals.values())
    print(f"  overall    {overall}/{n * 3}  ({100 * overall // (n * 3)}%)\n")


if __name__ == "__main__":
    main()
