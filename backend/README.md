# ExamSensei — Backend

FastAPI app + scraper pipeline for the Indian competitive-exam mentor. Verifies Supabase-issued JWTs, persists user / exam / chat / gamification state in Supabase Postgres, and answers chat through a pluggable LLM provider layer (Gemini → Groq → OpenAI → Anthropic → canned fallback).

This README covers everything you need to develop, test, and configure the backend. For production deployment, see [`../docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md).

---

## Requirements

- Python **3.11** (pinned in `runtime.txt` so Render uses the same)
- A Supabase project (for auth + Postgres). Free tier is enough.
- *(Optional)* an LLM API key — without one, the chat endpoint returns canned text but the rest of the app still works.

---

## Local setup

```bash
# from repo root
cd backend
python -m venv venv
venv\Scripts\activate              # Windows; use `source venv/bin/activate` elsewhere
pip install -r requirements.txt

# Copy + edit the env file
copy .env.example .env             # Windows; `cp` on Unix

# (Optional) Seed JEE/NEET demo data into the local SQLite DB.
# Idempotent — safe to re-run.
python seed_data.py

# Start the server with auto-reload
uvicorn app_v2:app --reload
```

The API will be at <http://localhost:8000>. Interactive docs at <http://localhost:8000/api/v1/docs>.

Defaults (no env file) point at a local SQLite file `examsensei.db` and disable LLM calls — so you can boot the API with zero configuration to inspect routes and run tests. Auth-protected endpoints will return 401 until you set `SUPABASE_JWT_SECRET`.

---

## Environment variables

All settings live in [`config.py`](config.py) and are loaded by pydantic-settings. See [`.env.example`](.env.example) for the canonical list and inline comments. The important ones:

| Variable | Purpose | Required? |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string. SQLite locally, Supabase Postgres in prod. | Prod only |
| `SUPABASE_URL` | Supabase project URL. | Prod |
| `SUPABASE_JWT_SECRET` | Used to verify JWTs the frontend gets from Supabase Auth. | Always (default rejects in prod) |
| `SUPABASE_SERVICE_ROLE_KEY` | Server-side admin key (only needed for the scraper). | Scraper only |
| `LLM_PROVIDER` | `auto` (default) picks the first configured key in the order anthropic → openai → groq → gemini. Pin a specific one with `gemini` / `groq` / `openai` / `anthropic` / `none`. | No |
| `GOOGLE_API_KEY` | Gemini Flash. Free tier. | No |
| `GROQ_API_KEY` | Groq (Llama). Free tier. | No |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | Paid plug-ins. | No |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins. | Prod |
| `ENVIRONMENT` | `development` / `staging` / `production`. Production enforces non-default JWT secret. | No |
| `SENTRY_DSN` | Optional error tracking. | No |

---

## Running tests

```bash
venv\Scripts\python -m pytest        # all 44 tests
venv\Scripts\python -m pytest -k security        # just the auth/IDOR tests
venv\Scripts\python -m pytest tests/test_llm_providers.py -v
```

The test suite is fully self-contained — it uses in-memory SQLite, mints Supabase-shaped JWTs locally, and exercises the LLM provider layer with a fake provider. **No network calls, no external services required.**

Current status: **44 passed, 1 skipped, 0 failed**.

---

## What lives where

| File | Responsibility |
|---|---|
| `app_v2.py` | FastAPI app, all HTTP routes, middleware, exception handlers, rate limiting |
| `auth.py` | Single dependency that verifies the Supabase JWT in `Authorization: Bearer …` and loads the matching `User` row |
| `models.py` | SQLAlchemy models. `User.id` is UUID and matches `auth.users.id` directly. Cross-dialect `UUIDType` handles SQLite for tests + Postgres for prod |
| `database.py` | Engine + session factory. Postgres pool tuned for Supabase free tier (`pool_pre_ping=True`, `pool_recycle=1800`) |
| `config.py` | All env vars + production invariants (e.g. rejects default JWT secret in prod) |
| `chatbot.py` | Hybrid mentor. **Layer 1**: regex intent → instant deterministic handler. **Layer 2**: LLM with tool calls for open-ended queries. Picks Layer based on intent + confidence |
| `chatbot_tools.py` | Tool functions the LLM may call: `get_user_profile`, `get_exam_details`, `generate_study_plan` |
| `llm_providers.py` | `LLMProvider` protocol + Gemini / Groq / OpenAI / Anthropic / Null implementations. `get_provider()` picks one from configured API keys |
| `lifecycle.py` | Stateless lifecycle state machine — stage progression + milestone reminders. Operates on the caller's `Session` |
| `ai_models.py` | `TopicPrioritizer`, `ExamClashDetector`, `AdaptiveMentor`, `CareerRecommender` |
| `exceptions.py` | HTTP error helpers, all returning the same `{"detail": {"message", "details"}}` envelope |
| `logger.py` | JSON logger in prod, human-readable in dev; `request_id` carried via ContextVar |
| `seed_data.py` | Idempotent JEE/NEET demo seed |
| `migrations/001_supabase_profile_trigger.sql` | One-time SQL to install the `auth.users` → `public.users` trigger in Supabase |
| `scripts/refresh_exam_data.py` | Standalone script driven by `data/exam_sources.yaml`; fetches + extracts + upserts |
| `data/exam_sources.yaml` | Curated list of 22 Indian exam bodies (NTA, UPSC, SSC, IBPS, state PSCs, etc.) |

---

## API surface

```
GET    /                                    Root info
GET    /api/v1/health                       Liveness check
GET    /api/v1/docs                         Swagger UI
GET    /api/v1/auth/me                      Current user (requires Supabase JWT)
GET    /api/v1/exams                        List exams (public, paginated)
GET    /api/v1/exams/{exam_id}              Exam detail
GET    /api/v1/users/{uuid}                 User profile (own only)
PUT    /api/v1/users/{uuid}/profile         Update profile (own only)
POST   /api/v1/users/{uuid}/chat            Chat with mentor (own only)
GET    /api/v1/users/{uuid}/recommendations Personalized recommendations
POST   /api/v1/users/{uuid}/study-plan      Generate a study plan
GET    /api/v1/users/{uuid}/gamification    XP / level / streak
```

All `/users/{uuid}/*` endpoints enforce ownership: `current_user.id == uuid` or 403. There are no `register` / `login` / `refresh` endpoints — Supabase Auth on the frontend issues the JWT directly.

---

## Auth: how the JWT flows

```
Browser → supabase.auth.signUp / signIn → Supabase issues HS256 JWT
                                              ↓
Browser stores session → adds `Authorization: Bearer <jwt>` to every API call
                                              ↓
FastAPI auth dependency (auth.get_current_user):
  1. Pull the bearer token
  2. Verify HS256 signature + audience="authenticated" using SUPABASE_JWT_SECRET
  3. Read `sub` (UUID) → look up users.id
  4. Return the User row → reachable as Depends(get_current_active_user)
```

On the Supabase side, the trigger in `migrations/001_supabase_profile_trigger.sql` automatically creates the `public.users` row from `auth.users` on signup, copying `raw_user_meta_data` fields (`name`, `education_level`, `state`, `category`, `budget`).

---

## Chatbot routing decision

```
user message → _analyze_intent()  (cheap regex)
                  │
                  ├── confidence ≥ 0.85 AND intent ∈
                  │   {career, study_planning, performance_analysis,
                  │    motivational_support, exam_information}
                  │      → Layer 1: deterministic Python handler, instant, free
                  │
                  └── otherwise
                         → Layer 2: LLM provider with tool calling
                                    (up to 3 tool-call turns)
```

The LLM may call `get_user_profile`, `get_exam_details(code)`, or `generate_study_plan(exam_code, days)`. Each tool call returns JSON, which is fed back into the next LLM turn until the model returns plain text. If the LLM provider fails or no API key is configured, the endpoint still returns 200 with canned text — chat never 500s on missing config.

---

## Exam-data refresh (out-of-band)

The scraper does **not** run on the Render dyno. It runs on **GitHub Actions cron** (`.github/workflows/refresh_exam_data.yml`, Sundays 04:00 UTC + manual trigger). It reads `data/exam_sources.yaml`, fetches each page through Jina Reader (free, 100 RPM) with Crawl4AI as fallback, asks Gemini Flash to extract structured `Exam` + `Topic` data, validates with Pydantic, and upserts into Supabase by `exam.code`.

Scraper-only dependencies live in `requirements-scraper.txt` so the Render API slug stays small.

To trigger a manual refresh: GitHub → Actions → "Refresh exam data" → "Run workflow".

---

## Troubleshooting

- **`SUPABASE_JWT_SECRET is still the default value in production`** on boot → set the env var to your real Supabase JWT secret (Dashboard → Project Settings → API → JWT Secret).
- **401 on every protected endpoint** → check that the frontend includes `Authorization: Bearer <access_token>` and that the secret in your backend env matches the Supabase project.
- **`User profile not found` on `/auth/me`** → run [`migrations/001_supabase_profile_trigger.sql`](migrations/001_supabase_profile_trigger.sql) in the Supabase SQL Editor.
- **Tests pass locally but Render fails to boot** → check `DATABASE_URL` has `?sslmode=require` (Supabase requires SSL).
- **Chat returns canned text** → no LLM API key is configured. Set `GOOGLE_API_KEY` (Gemini free tier) or `GROQ_API_KEY` to get real responses.

---

## License

MIT.
