# Ava

> **The support agent that understands your app's _state_ — not just its pixels.**
> Ava is embedded in a SaaS, reads the live DOM, knows _why_ an element is blocked,
> and guides the user by voice + text — step by step.

_Built for the **Capgemini AIE × TrueFoundry × CrewAI** hackathon — "From Prototype to Production: Real-World AI Agents."_

---

## The problem

Generic support chatbots don't know your app. They see text, not state. They can't tell a
user that **Publish** is greyed out _because no domain is connected_. Ava can — it reads the
interface state, maps it to your product docs, and answers the real question: **why is this blocked?**

## What it does

The user asks (voice or text) → Ava reads the page's interactive state (disabled buttons,
validation errors, ARIA) → a **CrewAI** crew reasons over the state + a RAG retrieval of the
product docs → Ava returns a strict structured answer and **highlights the element to fix**:

```json
{ "speech": "« Publier » est désactivé car le format du domaine est invalide.",
  "highlight_selector": "[data-ava=domain-input]",
  "next_step": "Corrige le domaine (sans espaces, ex. monsite.com) et il s'activera." }
```

Note: it highlights the **root cause** (the domain field), not just the disabled button — that's the multi-agent reasoning.

## Try it (local, ~30s)

```bash
# backend (FastAPI + CrewAI)
cd backend && uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env        # add TrueFoundry gateway creds, or leave empty for mock mode
.venv/bin/uvicorn app.main:app --port 8000
# open the demo
open http://localhost:8000/demo     # mock "Lyvica" with blocked states + the Ava widget
```

Ask _"pourquoi je ne peux pas publier ?"_ → watch Ava explain and highlight.

## How it works

```
        ┌──────────────────────── Ava (FastAPI) ─────────────────────────┐
 DOM  ──►│  /ask  →  CrewAI crew                                          │──►  { speech,
 state  │           lean: 1 agent (~2-5s, live demo)                      │      highlight_selector,
 +Q     │           deep: Perception ∥ Knowledge → Guide (orchestration)  │      next_step }
        │           every LLM call → TrueFoundry AI Gateway → Bedrock     │
        │           deterministic mock fallback (never 500s live)         │
        └─────────────────────────────────────────────────────────────────┘
              ▲ widget.js (vanilla, injectable)         ▲ RAG over product docs
```

- **Lean mode** (default): DOM analysis + doc retrieval done in Python, injected into one agent → fast for the live demo.
- **Deep mode** (`AVA_DEEP_MODE=true`): a real 3-agent crew (Perception ∥ Knowledge → Guide) showcasing CrewAI orchestration.

## Built on TrueFoundry + CrewAI

- **CrewAI** runs the agent crew (lean + deep). Strict structured output via `output_pydantic`.
- **TrueFoundry AI Gateway** — _every_ LLM call routes through it (OpenAI-compatible → AWS Bedrock),
  so cost/latency/traces are observable in the TF dashboard, with model fallbacks and guardrails.
  Same gateway + fallback convention as our `lyvica-resilient-agent`. Currently serving **Amazon Nova**
  (Anthropic Claude is the configured fallback but gated on the demo Bedrock account — the exact
  "resilience" scenario the gateway is built for).

## Reliability & evaluation

`backend/eval/` replays fixed Lyvica scenarios against `/ask` and scores every answer
(answered · correct highlight · grounded in the right reason). Runs against mock, the live crew,
or prod (`AVA_URL=...`):

```
  Ava reliability eval — http://localhost:8000  (4 scenarios)   mode: crew
  answered 4/4 (100%)   selector 4/4 (100%)   grounded 4/4 (100%)   overall 12/12 (100%)
```

## How it maps to the judging criteria

| Criterion | In Ava |
|---|---|
| **Real-world use case** | Embedded SaaS support — a real product (Lyvica), a real failure (users stuck on blocked states). |
| **Reliability / eval / iteration** | Scored eval harness (12/12), deterministic mock fallback, lean/deep modes to iterate latency vs depth. |
| **Governance / safe deployment** | All LLM calls governed by the TF gateway (fallbacks, traces); Ava **highlights & explains, never clicks** for the user. |
| **Multi-agent orchestration** | CrewAI crew: Perception ∥ Knowledge → Guide, with tool-using RAG. |

## Project structure

```
backend/   FastAPI + CrewAI  (app/ = ask, crew, dom, rag, llm, tools; eval/ = scoreboard; Dockerfile)
widget/    ava-widget.js     vanilla injectable widget (DOM capture, highlight, voice hook)
docs/      per-tenant RAG corpus (markdown)
demo/      lyvica.html       self-contained mock app to demo the loop locally
web/       Next.js landing    (Tailwind + shadcn + Magic UI)
```

## Config (`backend/.env`)

| Var | Role |
|-----|------|
| `TFY_BASE_URL` / `TFY_API_KEY` | TrueFoundry AI Gateway endpoint + token |
| `MODEL_PRIMARY` · `MODEL_FALLBACK_1/2` | model + fallback chain (e.g. `aws-bedrock/us.amazon.nova-pro-v1-0`) |
| `AVA_DEEP_MODE` | `true` = 3-agent crew, `false` = lean (default) |

Empty creds → **mock mode** (deterministic, runs with no LLM).

## Status

✅ Crew live through the TrueFoundry gateway · ✅ eval 12/12 · ✅ landing · ✅ local demo
⬜ Deploy backend on TrueFoundry · ⬜ embed in production Lyvica · ⬜ voice avatar
