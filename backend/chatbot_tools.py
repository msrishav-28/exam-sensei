"""
Tools the chatbot's LLM layer can call.

Each tool is a Python function bound to (db, user_id) by the chatbot. The
LLM sees the schema in `TOOL_SPECS`; when it issues a tool call we look up
the function in `TOOL_REGISTRY`, execute it, JSON-serialize the result, and
feed it back as a tool message in the next turn.
"""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, List
from uuid import UUID

from sqlalchemy.orm import Session

from ai_models import TopicPrioritizer, _coerce_json
from llm_providers import ToolSpec
from models import Exam, User


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def get_user_profile(db: Session, user_id: UUID, **_: Any) -> Dict:
    """Return the user's current stage, career paths, active exams, profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    return {
        "current_stage": user.current_stage,
        "career_paths": user.career_paths or [],
        "active_exams": user.active_exams or [],
        "preparation_profile": _coerce_json(user.preparation_profile, {}),
        "education_level": user.education_level,
        "state": user.state,
    }


def get_exam_details(db: Session, user_id: UUID, *, code: str, **_: Any) -> Dict:
    """Return name, body, dates, pattern, eligibility for an exam by code."""
    exam = db.query(Exam).filter(Exam.code == code).first()
    if not exam:
        # Be helpful: surface a few available codes so the LLM can retry.
        sample = [c for (c,) in db.query(Exam.code).limit(10).all()]
        return {"error": f"Exam '{code}' not found", "available_codes": sample}
    return {
        "code": exam.code,
        "name": exam.name,
        "body": exam.body,
        "exam_type": exam.exam_type,
        "important_dates": _coerce_json(exam.important_dates, {}),
        "pattern": _coerce_json(exam.pattern, {}),
        "eligibility": _coerce_json(exam.eligibility, {}),
        "subjects": _coerce_json(exam.subjects, []),
    }


def generate_study_plan(
    db: Session,
    user_id: UUID,
    *,
    exam_code: str,
    days_available: int = 90,
    **_: Any,
) -> Dict:
    """Generate a prioritized study plan for the given exam."""
    return TopicPrioritizer(db).generate_study_plan(user_id, exam_code, days_available)


# ---------------------------------------------------------------------------
# Tool specs (what the LLM sees) + registry (what we call)
# ---------------------------------------------------------------------------

TOOL_SPECS: List[ToolSpec] = [
    ToolSpec(
        name="get_user_profile",
        description=(
            "Return the current user's exam-prep profile: current_stage, "
            "career_paths, active_exams, strengths, weaknesses, study hours. "
            "Call this when you need user-specific context before answering."
        ),
        parameters={"type": "object", "properties": {}, "required": []},
    ),
    ToolSpec(
        name="get_exam_details",
        description=(
            "Return details about a specific Indian competitive exam by its "
            "code (e.g. 'jee_main_2025', 'neet_2025'): name, body, dates, "
            "pattern, eligibility, subjects."
        ),
        parameters={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Exam code, e.g. 'jee_main_2025'"},
            },
            "required": ["code"],
        },
    ),
    ToolSpec(
        name="generate_study_plan",
        description=(
            "Build a prioritized, time-allocated study plan for the given exam "
            "based on the user's strengths and weaknesses."
        ),
        parameters={
            "type": "object",
            "properties": {
                "exam_code": {"type": "string"},
                "days_available": {"type": "integer", "minimum": 1, "maximum": 365, "default": 90},
            },
            "required": ["exam_code"],
        },
    ),
]


TOOL_REGISTRY: Dict[str, Callable[..., Dict]] = {
    "get_user_profile": get_user_profile,
    "get_exam_details": get_exam_details,
    "generate_study_plan": generate_study_plan,
}


def execute_tool(name: str, db: Session, user_id: UUID, arguments: Dict) -> str:
    """Run a tool call and return the JSON-encoded result for the LLM."""
    fn = TOOL_REGISTRY.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = fn(db, user_id, **(arguments or {}))
    except TypeError as e:
        return json.dumps({"error": f"Bad arguments for {name}: {e}"})
    except Exception as e:  # noqa: BLE001
        return json.dumps({"error": f"{name} failed: {e}"})
    return json.dumps(result, default=str)
