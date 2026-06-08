"""
Refresh Indian exam metadata into Supabase.

Pipeline (per source defined in backend/data/exam_sources.yaml):

    Crawl4AI / Jina Reader → clean markdown
        → Gemini Flash structured extraction (Pydantic schema)
            → supabase-py upsert (by Exam.code)

Runs on GitHub Actions cron (.github/workflows/refresh_exam_data.yml) so the
Render dyno isn't burning hours on scraping. Manual trigger also supported
via `workflow_dispatch`.

Designed to be import-safe: nothing executes at module load. Tests import
`extract_exam_data` and `upsert_exam` directly with mocked dependencies.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import httpx
import yaml
from pydantic import BaseModel, Field, ValidationError


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("refresh_exam_data")


# ---------------------------------------------------------------------------
# Schema the LLM must return
# ---------------------------------------------------------------------------

class ExtractedTopic(BaseModel):
    subject: str
    name: str
    weightage_history: List[int] = Field(default_factory=list)
    avg_questions: float = 0.0
    difficulty_distribution: Dict[str, int] = Field(default_factory=dict)
    marks_per_hour: float = 0.0
    correlation_topics: List[str] = Field(default_factory=list)
    previous_patterns: List[str] = Field(default_factory=list)


class ExtractedExam(BaseModel):
    name: str
    code: str
    body: str
    exam_type: str
    eligibility: Dict = Field(default_factory=dict)
    fees: Dict = Field(default_factory=dict)
    important_dates: Dict = Field(default_factory=dict)
    syllabus: str = ""
    pattern: Dict = Field(default_factory=dict)
    centers: List[str] = Field(default_factory=list)
    subjects: List[str] = Field(default_factory=list)
    notification_url: str = ""
    application_url: str = ""
    result_url: str = ""
    topics: List[ExtractedTopic] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------

async def fetch_via_jina(url: str, *, timeout: float = 30.0, no_cache: bool = False) -> str:
    """
    Jina Reader returns clean LLM-friendly markdown for any URL.
    Free, no auth required up to ~100 req/min.

    Set `no_cache=True` on retry — Jina occasionally caches a 422 from an
    aggressive origin (gov.in sites) and serves it back. X-No-Cache forces
    a re-fetch with a fresh upstream connection, which sometimes succeeds.
    """
    reader_url = f"https://r.jina.ai/{url}"
    headers = {"User-Agent": "ExamSensei-Bot/1.0"}
    if no_cache:
        headers["X-No-Cache"] = "true"
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.get(reader_url, headers=headers)
        r.raise_for_status()
        return r.text


async def fetch_via_crawl4ai(url: str, *, page_timeout_ms: int = 20_000) -> str:
    """
    Crawl4AI for full JS-rendered pages with built-in anti-bot.
    Lazy import so unit tests don't need the package installed.

    `page_timeout_ms` caps Playwright's navigation wait. Default lowered from
    Crawl4AI's built-in 60 s — gov.in sites that block headless browsers will
    timeout regardless, and the long wait wastes ~3 minutes of workflow runtime
    per failed source. 20 s is enough for any site that's going to succeed.
    """
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig  # type: ignore
    run_cfg = CrawlerRunConfig(page_timeout=page_timeout_ms)
    async with AsyncWebCrawler(verbose=False) as crawler:
        result = await crawler.arun(url=url, config=run_cfg)
        return result.markdown or ""


def _looks_like_real_content(text: str) -> bool:
    """Cheap heuristic: long enough and not just a Jina error envelope."""
    if not text or len(text) < 200:
        return False
    # Jina returns prose like "We've received your request. The URL was..."
    # for some 4xx responses — those slip past raise_for_status sometimes.
    lower = text.lower()
    if "unprocessable" in lower[:500] or "we couldn't process" in lower[:500]:
        return False
    return True


async def fetch_page(url: str, *, prefer_jina: bool = True) -> str:
    """Try Jina (twice if needed), fall back to Crawl4AI for stubborn pages."""
    if prefer_jina:
        for no_cache in (False, True):
            try:
                text = await fetch_via_jina(url, no_cache=no_cache)
                if _looks_like_real_content(text):
                    return text
            except Exception as e:  # noqa: BLE001
                log.warning(
                    f"Jina {'(no-cache retry) ' if no_cache else ''}failed for {url}: {e}"
                )
    try:
        return await fetch_via_crawl4ai(url)
    except Exception as e:  # noqa: BLE001
        log.warning(f"Crawl4AI failed for {url}: {e}")
        return ""


# ---------------------------------------------------------------------------
# LLM extraction
# ---------------------------------------------------------------------------

_EXTRACTION_PROMPT = """\
You are extracting structured exam metadata for an Indian competitive-exam
mentor app. Read the scraped text below and return a single JSON object
matching this schema exactly:

{schema}

Constraints:
- Output JSON only; no prose, no markdown fences.
- Use ISO date strings (YYYY-MM-DD) inside important_dates when possible.
- If a field isn't in the source, leave it as the schema default (empty list,
  empty dict, 0, or "").
- Preserve the `code` field exactly as: {code}
- Preserve the `body` field exactly as: {body}
- Preserve the `name` field exactly as: {name}
- Preserve the `exam_type` field exactly as: {exam_type}

Scraped text:
---
{text}
---
"""


async def extract_exam_data(
    *,
    code: str,
    name: str,
    body: str,
    exam_type: str,
    scraped_text: str,
    api_key: str,
    model: str = "gemini-2.5-flash",
) -> Optional[ExtractedExam]:
    """Ask Gemini to structure scraped text into ExtractedExam. Returns None on failure."""
    if not scraped_text.strip():
        log.warning(f"[{code}] empty scraped text — skipping extraction")
        return None

    from google import genai  # lazy import
    from google.genai import types as gtypes

    client = genai.Client(api_key=api_key)
    schema_json = json.dumps(ExtractedExam.model_json_schema(), indent=2)
    prompt = _EXTRACTION_PROMPT.format(
        schema=schema_json,
        code=code, name=name, body=body, exam_type=exam_type,
        text=scraped_text[:30_000],   # rough cap for token budget
    )

    # NOTE: do NOT pass `response_schema=ExtractedExam`. The google-genai SDK
    # converts Pydantic models to a JSON schema that includes
    # `additionalProperties: false`, which the Gemini Developer API (free
    # tier) rejects with:
    #     "additionalProperties is only supported in Gemini Enterprise
    #      Agent Platform mode, not in Gemini Developer API mode."
    # The schema is already embedded in the prompt text and Pydantic
    # validates the response on the way back (model_validate below), so
    # `response_mime_type` alone is enough to keep output JSON-shaped.
    try:
        resp = await client.aio.models.generate_content(
            model=model,
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            config=gtypes.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
    except Exception as e:  # noqa: BLE001
        log.warning(f"[{code}] Gemini call failed: {e}")
        return None

    raw = (resp.text or "").strip()
    if not raw:
        log.warning(f"[{code}] Gemini returned empty response")
        return None

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        log.warning(f"[{code}] Gemini returned non-JSON: {e}")
        return None

    # Force the fields we asked Gemini to preserve, defensively
    data["code"] = code
    data["name"] = name
    data["body"] = body
    data["exam_type"] = exam_type

    try:
        return ExtractedExam.model_validate(data)
    except ValidationError as e:
        log.warning(f"[{code}] Gemini output failed schema validation: {e}")
        return None


# ---------------------------------------------------------------------------
# Supabase upsert
# ---------------------------------------------------------------------------

def upsert_exam(supabase, extracted: ExtractedExam) -> Dict:
    """
    Upsert an exam + its topics. Returns a summary dict for logging.

    `supabase` is a supabase.Client; passed in so tests can inject a fake.
    """
    exam_row = extracted.model_dump(exclude={"topics"})

    # Upsert by code (uniqueness constraint).
    exam_resp = (
        supabase.table("exams")
        .upsert(exam_row, on_conflict="code")
        .execute()
    )

    if not getattr(exam_resp, "data", None):
        raise RuntimeError(f"Upsert of exam {extracted.code} returned no rows")
    exam_id = exam_resp.data[0]["id"]

    # Topics: blow away & re-insert this exam's topics. Simpler than diffing
    # and the table is exam-scoped, so no cross-cutting effects.
    supabase.table("topics").delete().eq("exam_id", exam_id).execute()
    if extracted.topics:
        topic_rows = [
            {**t.model_dump(), "exam_id": exam_id}
            for t in extracted.topics
        ]
        supabase.table("topics").insert(topic_rows).execute()

    return {
        "code": extracted.code,
        "exam_id": exam_id,
        "topic_count": len(extracted.topics),
    }


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def load_sources(path: Path) -> List[Dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or []


async def refresh_one(source: Dict, *, gemini_api_key: str) -> Optional[ExtractedExam]:
    code = source["code"]
    name = source["name"]
    body = source["body"]
    exam_type = source["exam_type"]

    log.info(f"[{code}] fetching {len(source.get('pages', {}))} page(s)")
    pages: Dict[str, str] = source.get("pages", {})
    chunks: List[str] = []
    for label, url in pages.items():
        text = await fetch_page(url)
        if text:
            chunks.append(f"### Section: {label}\nSource: {url}\n\n{text}")

    if not chunks:
        log.warning(f"[{code}] all pages failed to fetch — skipping")
        return None

    combined = "\n\n".join(chunks)
    extracted = await extract_exam_data(
        code=code, name=name, body=body, exam_type=exam_type,
        scraped_text=combined, api_key=gemini_api_key,
    )
    return extracted


async def main() -> int:
    gemini_api_key = os.environ.get("GOOGLE_API_KEY")
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not (gemini_api_key and supabase_url and supabase_key):
        log.error("Missing required env: GOOGLE_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY")
        return 1

    from supabase import create_client  # lazy import

    supabase = create_client(supabase_url, supabase_key)
    sources_path = Path(__file__).resolve().parent.parent / "data" / "exam_sources.yaml"
    sources = load_sources(sources_path)
    log.info(f"Refreshing {len(sources)} exam sources")

    succeeded = 0
    failed: List[str] = []

    for source in sources:
        code = source.get("code", "?")
        try:
            extracted = await refresh_one(source, gemini_api_key=gemini_api_key)
            if extracted is None:
                failed.append(code)
                continue
            summary = upsert_exam(supabase, extracted)
            log.info(f"[{code}] upserted: {summary}")
            succeeded += 1
        except Exception as e:  # noqa: BLE001
            log.exception(f"[{code}] unexpected error: {e}")
            failed.append(code)

    log.info(f"Done. Succeeded: {succeeded} / {len(sources)}. Failed: {failed}")
    # Exit non-zero so GitHub Actions surfaces it visibly when most sources fail.
    return 0 if succeeded >= max(1, len(sources) // 2) else 2


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
