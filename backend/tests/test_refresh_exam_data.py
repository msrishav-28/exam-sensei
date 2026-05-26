"""
Tests for the scraper pipeline. We don't make real network calls or hit
Supabase — Gemini extraction is verified via a hand-built dict piped through
the Pydantic schema, and upsert behavior is verified against an in-memory
fake supabase client.
"""
import sys
from pathlib import Path

import pytest

# Make `scripts/` importable.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from refresh_exam_data import ExtractedExam, ExtractedTopic, load_sources, upsert_exam  # noqa: E402


# ---- Schema validation --------------------------------------------------

def test_extracted_exam_minimal_round_trip():
    """A minimal payload validates and round-trips through model_dump()."""
    payload = {
        "name": "JEE Main 2025",
        "code": "jee_main_2025",
        "body": "NTA",
        "exam_type": "engineering_entrance",
    }
    exam = ExtractedExam.model_validate(payload)
    dumped = exam.model_dump()
    assert dumped["code"] == "jee_main_2025"
    assert dumped["topics"] == []
    assert dumped["eligibility"] == {}


def test_extracted_exam_with_topics():
    payload = {
        "name": "JEE Main 2025",
        "code": "jee_main_2025",
        "body": "NTA",
        "exam_type": "engineering_entrance",
        "important_dates": {"exam_dates": ["2025-01-24", "2025-01-25"]},
        "topics": [
            {
                "subject": "physics", "name": "mechanics",
                "weightage_history": [25, 24, 26], "avg_questions": 8.0,
                "difficulty_distribution": {"easy": 40, "medium": 45, "hard": 15},
                "marks_per_hour": 1.8,
            },
        ],
    }
    exam = ExtractedExam.model_validate(payload)
    assert len(exam.topics) == 1
    assert isinstance(exam.topics[0], ExtractedTopic)


# ---- YAML loading -------------------------------------------------------

def test_load_sources_yaml(tmp_path):
    f = tmp_path / "src.yaml"
    f.write_text(
        "- code: jee_main_2025\n"
        "  body: NTA\n"
        "  name: JEE Main 2025\n"
        "  exam_type: engineering_entrance\n"
        "  pages:\n"
        "    notification: https://example.com\n",
        encoding="utf-8",
    )
    sources = load_sources(f)
    assert len(sources) == 1
    assert sources[0]["code"] == "jee_main_2025"
    assert sources[0]["pages"]["notification"] == "https://example.com"


def test_bundled_exam_sources_yaml_parses():
    """The shipped YAML must be valid and reference 15+ exams."""
    src = Path(__file__).resolve().parent.parent / "data" / "exam_sources.yaml"
    sources = load_sources(src)
    assert len(sources) >= 15, f"Expected 15+ exam sources, got {len(sources)}"
    for s in sources:
        assert {"code", "name", "body", "exam_type", "pages"} <= s.keys(), s
        assert isinstance(s["pages"], dict) and s["pages"], s


# ---- Upsert against fake supabase ---------------------------------------

class _FakeResp:
    def __init__(self, data):
        self.data = data


class _FakeFilter:
    def __init__(self, table):
        self._table = table

    def execute(self):
        # delete is the only path that flows through here. Mutate the store's
        # list in place — rebinding `_rows` only changes our local view.
        rows = self._table._rows
        kept = [row for row in rows if row.get("exam_id") != self._table._filter_value]
        deleted = len(rows) - len(kept)
        rows[:] = kept
        return _FakeResp([{"deleted": deleted}])

    def eq(self, field, value):
        self._table._filter_value = value
        return self


class _FakeTable:
    def __init__(self, name, store):
        self.name = name
        self._store = store
        self._rows = store.setdefault(name, [])
        self._filter_value = None
        self._pending_upsert = None
        self._pending_insert = None
        self._on_conflict = None

    def upsert(self, row, on_conflict=None):
        self._pending_upsert = row
        self._on_conflict = on_conflict
        return self

    def insert(self, rows):
        self._pending_insert = rows
        return self

    def delete(self):
        return _FakeFilter(self)

    def execute(self):
        if self._pending_upsert is not None:
            row = dict(self._pending_upsert)
            conflict_key = self._on_conflict or "id"
            for i, existing in enumerate(self._rows):
                if existing.get(conflict_key) == row.get(conflict_key):
                    new_id = existing["id"]
                    self._rows[i] = {**row, "id": new_id}
                    return _FakeResp([self._rows[i]])
            row["id"] = len(self._rows) + 1
            self._rows.append(row)
            return _FakeResp([row])
        if self._pending_insert is not None:
            inserted = []
            for r in self._pending_insert:
                r = dict(r)
                r["id"] = len(self._rows) + 1
                self._rows.append(r)
                inserted.append(r)
            return _FakeResp(inserted)
        raise RuntimeError("execute() called with no pending operation")


class _FakeSupabase:
    def __init__(self):
        self._store = {}

    def table(self, name):
        return _FakeTable(name, self._store)


def test_upsert_exam_creates_then_updates_row():
    fake = _FakeSupabase()
    exam = ExtractedExam.model_validate({
        "name": "JEE Main 2025",
        "code": "jee_main_2025",
        "body": "NTA",
        "exam_type": "engineering_entrance",
        "topics": [
            {"subject": "physics", "name": "mechanics",
             "weightage_history": [25], "avg_questions": 8.0,
             "difficulty_distribution": {"easy": 40}, "marks_per_hour": 1.8},
        ],
    })

    summary = upsert_exam(fake, exam)
    assert summary["code"] == "jee_main_2025"
    assert summary["topic_count"] == 1
    assert len(fake._store["exams"]) == 1
    assert len(fake._store["topics"]) == 1

    # Re-run: upsert should hit the same exam row (idempotent),
    # and topics should be replaced (not duplicated).
    summary2 = upsert_exam(fake, exam)
    assert summary2["exam_id"] == summary["exam_id"]
    assert len(fake._store["exams"]) == 1
    assert len(fake._store["topics"]) == 1
