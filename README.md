# Ava

**Agent de support embarqué dans un SaaS** qui comprend *l'état de l'interface* (le DOM, pas les pixels) et guide l'utilisateur pas à pas — par la voix (avatar) et le texte.

Différenciateur : Ava sait *pourquoi* un élément est bloqué (« le bouton Publier est grisé parce qu'aucun domaine n'est connecté »), grâce à la lecture du DOM + un RAG sur la doc produit.

Ava est une **plateforme** : un seul déploiement sert plusieurs *tenants*. Lyvica est le premier tenant — il colle un `<script>` et Ava tourne en prod chez lui.

## Architecture

```
        ┌──────────────────────────────────────────┐
        │  Ava (plateforme, déployée TrueFoundry)   │
        │                                            │
        │   POST /ask  ──►  Crew CrewAI              │
        │                   ┌─ Perception ─┐         │
        │                   │ (DOM state)  ├─► Guide │──► {speech, highlight_selector, next_step}
        │                   └─ Knowledge ──┘         │
        │                     (RAG doc)              │
        │   Tous les LLM via le TrueFoundry Gateway  │
        └────────────────────▲───────────────────────┘
                             │  widget.js (vanilla)
        ┌────────────────────┴───────────────────────┐
        │  Lyvica (tenant) — <script data-tenant>     │
        └──────────────────────────────────────────────┘
```

- **Plan runtime (hot path)** : crew CrewAI à 3 agents. Perception ∥ Knowledge en parallèle, puis Guide. ~2 appels de latence.
- **Plan production** : crew d'ingestion (RAG) + crew d'éval (`backend/eval/`). Déploiement + observabilité via TrueFoundry.
- **Mode mock** : si aucune clé LLM n'est configurée, `/ask` répond de façon déterministe (DOM + doc) — la boucle widget marche sans creds.

## Structure

```
backend/        FastAPI + crew CrewAI
  app/
    main.py       POST /ask, /health, /widget.js  (+ fallback mock)
    schemas.py    contrat structuré (AskRequest, AvaResponse)
    ava_crew.py   crew runtime: Perception ∥ Knowledge → Guide
    tools.py      tools CrewAI (doc_search / RAG)
    dom.py        analyse DOM déterministe (état bloqué)
    rag.py        retriever doc par tenant (TODO: pgvector)
    llm.py        LLM via TrueFoundry Gateway
    tenants.py    config par tenant
  eval/           crew d'éval (le "production")
widget/
  ava-widget.js   widget injectable (capture DOM, /ask, surlignage, hook voix)
docs/lyvica/      doc produit du tenant (corpus RAG)
```

## Lancer en local

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # laisser vide => mode mock
uvicorn app.main:app --reload --port 8000
```

Tester :
```bash
curl -s localhost:8000/ask -H 'content-type: application/json' -d '{
  "tenant_id":"lyvica","question":"Pourquoi je ne peux pas publier ?",
  "dom":{"url":"/publish","elements":[
    {"selector":"[data-ava=publish-btn]","label":"Publier","disabled":true},
    {"selector":"[data-ava=domain-input]","label":"Domaine","error":"Aucun domaine connecté"}]}}'
```

## Embed (côté Lyvica)

```html
<script src="https://AVA_HOST/widget.js" data-tenant="lyvica" data-endpoint="https://AVA_HOST"></script>
```

Poser des `data-ava="..."` sur les éléments clés (boutons, champs) pour des sélecteurs stables.

## Config (`.env`)

| Var | Rôle |
|-----|------|
| `TFY_BASE_URL` | endpoint TrueFoundry AI Gateway (OpenAI-compatible) |
| `TFY_API_KEY`  | TrueFoundry PAT / service-account token |
| `MODEL_PRIMARY` | modèle primaire (ex. `aws-bedrock/us.anthropic.claude-sonnet-4-5-...`) |
| `MODEL_FALLBACK_1` / `MODEL_FALLBACK_2` | chaîne de fallback (Sonnet → Opus → Nova) |
| `AVA_DEEP_MODE`    | `true` = crew complet, `false` = lean |

Sans `TFY_API_KEY`+`MODEL_PRIMARY` → **mode mock** automatique. Même convention que `lyvica-resilient-agent`.

## Milestones (hackathon)

1. ✅ `/ask` structuré (mock + crew) — DOM mocké
2. ⬜ Widget : capture DOM + question → réponse + surlignage
3. ⬜ Crew d'éval (reliability / iteration)
4. ⬜ Avatar voix (réutiliser le POC) — hook `window.AvaSpeak`
5. ⬜ RAG réel + polish flows + fallbacks pré-enregistrés
