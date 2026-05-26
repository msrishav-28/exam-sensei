# ExamSensei

AI-powered mentor for Indian competitive exam preparation. The product gives students a single place to track exam information, plan their study, and chat with a context-aware AI mentor about their preparation.

> **Status**: backend production-ready, frontend in development. Designed to run end-to-end on free tiers (Render + Supabase + Vercel + Google Gemini API + GitHub Actions) until ~100 active users.

---

## Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 15 + React 19 + TailwindCSS (on Vercel) |
| Backend API | FastAPI + SQLAlchemy 2 + python-jose (on Render's Python runtime) |
| Database | Supabase Postgres (free tier) |
| Auth | Supabase Auth — backend verifies JWTs, no custom password handling |
| LLM | Pluggable: Gemini Flash (default, free) → Groq → OpenAI → Anthropic, with a canned-text fallback when no key is configured |
| Exam data refresh | Crawl4AI + Jina Reader → Gemini structured extraction → Supabase upsert, run weekly on GitHub Actions cron |

---

## Repository layout

```
backend/                       FastAPI app + tests + scraper pipeline
  app_v2.py                    Routes (health, /auth/me, /exams, /users/* )
  auth.py                      Supabase JWT verifier dependency
  models.py                    SQLAlchemy models (UUID PK on User = auth.users.id)
  database.py, config.py       Engine, settings (pydantic-settings)
  chatbot.py                   Hybrid intent → LLM tool-calling mentor
  llm_providers.py             Pluggable Gemini / Groq / OpenAI / Anthropic
  chatbot_tools.py             Tool functions the LLM may call
  lifecycle.py, ai_models.py   Recommendation / clash / prioritization logic
  migrations/                  One-time Supabase SQL (auth.users → public.users trigger)
  scripts/                     Standalone scripts (exam-data refresh)
  data/exam_sources.yaml       Curated list of 22 Indian exam bodies
  tests/                       44 pytest tests (security, integration, LLM, scraper)
frontend/                      Next.js app (untouched in the recent backend pass)
docs/DEPLOYMENT.md             Step-by-step deploy guide
render.yaml                    Render Blueprint (Python runtime, no Docker)
.github/workflows/             GitHub Actions for the weekly exam-data refresh
```

---

## Quickstart (local dev)

```bash
# Backend (Python 3.11)
cd backend
python -m venv venv
venv\Scripts\activate                # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
copy .env.example .env               # fill in SUPABASE_* if you want auth to work
python seed_data.py                  # optional: seed JEE/NEET demo data into the local SQLite
uvicorn app_v2:app --reload

# Frontend
cd ../frontend
npm install --legacy-peer-deps
npm run dev
```

- Backend: http://localhost:8000
- Swagger UI: http://localhost:8000/api/v1/docs
- Frontend: http://localhost:3000

For full backend dev docs (env vars, testing, LLM provider selection, etc.) see **[backend/README.md](backend/README.md)**.

For deploying to Supabase + Render + Vercel see **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**.

---

## Tests

```bash
cd backend
venv\Scripts\python -m pytest
```

Current: **44 passing, 1 skipped**. Covers Supabase JWT semantics (8), IDOR + ownership, gamification race, profile updates, LLM provider routing (8), tool-call resolution, scraper extraction + upsert idempotency (5), and the existing exam / integration flows.

---

## License

MIT.
