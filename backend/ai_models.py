"""
AI / recommendation logic. All DB access goes through the session injected
by the caller; no module-level sessions or singletons hold state.
"""
import json
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from lifecycle import lifecycle_machine
from models import Exam, Topic, User


def _coerce_json(value, default):
    """
    Read JSON-typed columns defensively.

    Column(JSON) returns native Python (dict/list), but legacy rows in the
    repo's SQLite file were written via json.dumps() and come back as
    strings. Handle both transparently so an environment with mixed data
    doesn't crash.
    """
    if value is None or value == "":
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            return default
    return default


class CareerRecommender:
    """AI-powered career path recommender based on user profile and performance."""

    CAREER_MAPPINGS = {
        "engineering": {
            "jee_score_ranges": [(0, 50), (50, 100), (100, 150), (150, 200), (200, 300)],
            "colleges": [
                "Tier 3: State colleges",
                "Tier 2: NITs, IIITs",
                "Tier 2: BITS Pilani, VIT",
                "Tier 1: IITs, IIIT Hyderabad",
                "Tier 1: IIT Bombay, IIT Delhi",
            ],
            "next_steps": [
                "Consider diploma + lateral entry",
                "Focus on state CET exams",
                "Apply to private universities",
                "Secure IIT seat",
                "Top IITs - research opportunities",
            ],
        },
        "medical": {
            "neet_score_ranges": [(0, 200), (200, 400), (400, 500), (500, 600), (600, 720)],
            "colleges": [
                "Private medical colleges",
                "State government colleges",
                "AIIMS, JIPMER",
                "Top AIIMS institutes",
                "AIIMS Delhi, PGIMER",
            ],
        },
    }

    @staticmethod
    def recommend_career_path(user_profile: Dict, exam_scores: Dict) -> Dict:
        interests = user_profile.get("interests", [])
        budget = user_profile.get("budget", "medium")
        location = user_profile.get("location", "any")

        recommendations: List[Dict] = []

        if "engineering" in interests or "technology" in interests:
            jee_score = exam_scores.get("jee_main", 0)
            recommendations.append(
                CareerRecommender._get_engineering_recommendation(jee_score, budget, location)
            )

        if "medical" in interests or "biology" in interests:
            neet_score = exam_scores.get("neet", 0)
            recommendations.append(
                CareerRecommender._get_medical_recommendation(neet_score, budget, location)
            )

        if "commerce" in interests or "business" in interests:
            recommendations.append({
                "career_path": "commerce",
                "recommended_exams": ["cat", "mat", "cuet"],
                "colleges": ["Delhi University", "SRCC", "LBSIM"],
                "reasoning": "Strong foundation in commerce subjects, good analytical skills",
            })

        return {
            "primary_recommendation": recommendations[0] if recommendations else None,
            "alternative_paths": recommendations[1:] if len(recommendations) > 1 else [],
            "confidence_score": 0.85,
        }

    @staticmethod
    def _get_engineering_recommendation(jee_score: int, budget: str, location: str) -> Dict:
        percentile = min(jee_score / 3, 100)
        tier_index = min(int(percentile / 20), 4)
        return {
            "career_path": "engineering",
            "jee_percentile": percentile,
            "recommended_tier": CareerRecommender.CAREER_MAPPINGS["engineering"]["colleges"][tier_index],
            "next_steps": CareerRecommender.CAREER_MAPPINGS["engineering"]["next_steps"][tier_index],
            "budget_alignment": "high" if percentile > 80 else "medium" if percentile > 50 else "low",
            "timeline": "4 years undergraduate + 2 years masters" if percentile > 90 else "4 years undergraduate",
        }

    @staticmethod
    def _get_medical_recommendation(neet_score: int, budget: str, location: str) -> Dict:
        percentile = min(neet_score / 7.2, 100)
        tier_index = min(int(percentile / 20), 4)
        return {
            "career_path": "medical",
            "neet_percentile": percentile,
            "recommended_tier": CareerRecommender.CAREER_MAPPINGS["medical"]["colleges"][tier_index],
            "specializations": ["General Medicine", "Surgery", "Pediatrics", "Gynecology"][: tier_index + 1],
            "timeline": "5.5 years MBBS + 3 years MD/MS",
        }


class TopicPrioritizer:
    """Personalized topic prioritization using weightage and user profile."""

    def __init__(self, db: Session):
        self.db = db

    def generate_study_plan(self, user_id: UUID, exam_code: str, days_available: int) -> Dict:
        user = self.db.query(User).filter(User.id == user_id).first()
        exam = self.db.query(Exam).filter(Exam.code == exam_code).first()
        if not user or not exam:
            return {"error": "User or exam not found"}

        profile = _coerce_json(user.preparation_profile, {})
        strengths = profile.get("strengths", []) if isinstance(profile, dict) else []
        weaknesses = profile.get("weaknesses", []) if isinstance(profile, dict) else []

        topics = self.db.query(Topic).filter(Topic.exam_id == exam.id).all()

        prioritized_topics = []
        for topic in topics:
            weightage_history = _coerce_json(topic.weightage_history, [])
            latest_weightage = weightage_history[-1] if weightage_history else 0
            prioritized_topics.append({
                "topic": topic,
                "priority_score": self._calculate_priority_score(
                    topic, strengths, weaknesses, days_available
                ),
                "estimated_days": self._estimate_study_days(topic, profile),
                "difficulty": self._get_topic_difficulty(topic),
                "weightage": latest_weightage,
            })

        prioritized_topics.sort(key=lambda x: x["priority_score"], reverse=True)
        study_plan = self._create_weekly_plan(prioritized_topics, days_available)

        return {
            "exam_code": exam_code,
            "total_days": days_available,
            "prioritized_topics": [
                {
                    "name": t["topic"].name,
                    "subject": t["topic"].subject,
                    "priority_score": t["priority_score"],
                    "estimated_days": t["estimated_days"],
                    "difficulty": t["difficulty"],
                    "weightage": t["weightage"],
                }
                for t in prioritized_topics[:10]
            ],
            "weekly_plan": study_plan,
            "estimated_completion": f"{days_available} days from now",
            "success_probability": self._calculate_success_probability(prioritized_topics, profile),
        }

    def _calculate_priority_score(
        self, topic: Topic, strengths: List, weaknesses: List, days_available: int
    ) -> float:
        weightage_history = _coerce_json(topic.weightage_history, [])
        weightage = weightage_history[-1] if weightage_history else 10

        gap_multiplier = 2.0 if topic.name in weaknesses else 1.0
        if topic.name in strengths:
            gap_multiplier = 0.5

        # Guard against avg_questions being None or 0 — would otherwise divide by zero.
        avg_questions = topic.avg_questions or 1
        time_required = max(avg_questions * 2, 1)
        time_pressure = max(1, days_available / 90)

        priority_score = (weightage * gap_multiplier * time_pressure) / time_required
        return round(priority_score, 2)

    def _estimate_study_days(self, topic: Topic, profile: Dict) -> int:
        avg_questions = topic.avg_questions or 1
        base_days = avg_questions // 2
        study_hours_per_day = profile.get("study_hours_per_day", 6) if isinstance(profile, dict) else 6
        difficulty_multiplier = 1.5 if topic.name in ("modern_physics", "organic_chemistry") else 1.0
        return max(1, int(base_days * difficulty_multiplier / max(study_hours_per_day, 1)))

    def _get_topic_difficulty(self, topic: Topic) -> str:
        distribution = _coerce_json(topic.difficulty_distribution, {})
        hard_pct = distribution.get("hard", 0) if isinstance(distribution, dict) else 0
        if hard_pct > 20:
            return "hard"
        if hard_pct > 10:
            return "medium"
        return "easy"

    def _create_weekly_plan(self, prioritized_topics: List, total_days: int) -> Dict:
        weeks = max(total_days // 7, 1)
        plan: Dict = {}
        topic_index = 0
        for week in range(1, weeks + 1):
            weekly_topics = []
            week_days = 7
            for day in range(1, week_days + 1):
                if topic_index >= len(prioritized_topics):
                    break
                topic_data = prioritized_topics[topic_index]
                weekly_topics.append({
                    "day": f"Week {week}, Day {day}",
                    "topic": topic_data["topic"].name,
                    "focus_area": f"High-weightage ({topic_data['weightage']}%)",
                    "estimated_hours": 6,
                    "difficulty": topic_data["difficulty"],
                })
                topic_index += 1
            plan[f"week_{week}"] = weekly_topics
        return plan

    def _calculate_success_probability(self, topics: List, profile: Dict) -> float:
        total_weightage_covered = sum(t["weightage"] for t in topics[:20])
        study_consistency = profile.get("study_consistency", 0.7) if isinstance(profile, dict) else 0.7
        base_probability = min(total_weightage_covered / 100, 1.0)
        return round(base_probability * study_consistency * 0.9, 2)


class ExamClashDetector:
    """Detect and resolve exam date conflicts."""

    def detect_clashes(self, user_exams: List[str], db: Session) -> Dict:
        exam_dates: Dict[str, List[str]] = {}
        for exam_code in user_exams:
            exam = db.query(Exam).filter(Exam.code == exam_code).first()
            if exam and exam.important_dates:
                dates = _coerce_json(exam.important_dates, {})
                if isinstance(dates, dict):
                    exam_dates[exam_code] = list(dates.get("exam_dates", []) or [])

        clashes: List[Dict] = []
        items = list(exam_dates.items())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                exam1, dates1 = items[i]
                exam2, dates2 = items[j]
                overlapping = set(dates1) & set(dates2)
                if overlapping:
                    clashes.append({
                        "exams": [exam1, exam2],
                        "conflicting_dates": list(overlapping),
                        "severity": "high" if len(overlapping) > 1 else "medium",
                    })

        return {
            "has_clashes": bool(clashes),
            "clashes": clashes,
            "recommendations": self._generate_clash_resolutions(clashes, user_exams),
        }

    def _generate_clash_resolutions(self, clashes: List, user_exams: List) -> List[str]:
        if not clashes:
            return ["No clashes detected. You can prepare for all exams simultaneously."]
        out: List[str] = []
        for clash in clashes:
            exam1, exam2 = clash["exams"]
            out.append(
                f"Consider prioritizing {exam1} over {exam2} if your career goals align more closely with {exam1}."
            )
            out.append("Look for rescheduled dates or consider taking one exam in the next session.")
        return out


class AdaptiveMentor:
    """High-level mentor: combines lifecycle, prioritization, clash detection."""

    def __init__(self, db: Session):
        self.db = db
        self.topic_prioritizer = TopicPrioritizer(db)
        self.clash_detector = ExamClashDetector()

    def get_personalized_recommendations(self, user_id: UUID) -> Dict:
        """
        Pure read. We do NOT persist a Recommendation row per call here —
        that would let every GET pollute the table with duplicates. Persistence
        belongs in a deliberate write endpoint when we add one.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}

        rec_items: List[Dict] = []

        for rec in lifecycle_machine.recommend_next_exams(self.db, user_id):
            exam_id = self._get_exam_id_by_code(rec["exam"])
            exam_name = None
            if exam_id is not None:
                exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
                exam_name = exam.name if exam else None
            rec_items.append({
                "type": "career_path",
                "exam": exam_name or rec["exam"],
                "score": 0.9 if rec.get("priority") == "high" else 0.7,
                "reasoning": rec["reason"],
            })

        active_exams = user.active_exams or []
        if len(active_exams) > 1:
            clashes = self.clash_detector.detect_clashes(active_exams, self.db)
            if clashes["has_clashes"]:
                for clash in clashes["clashes"]:
                    rec_items.append({
                        "type": "clash_alert",
                        "exam": None,
                        "score": 0.95,
                        "reasoning": (
                            f"Exam clash detected between {', '.join(clash['exams'])}. "
                            f"{clashes['recommendations'][0] if clashes['recommendations'] else ''}"
                        ).strip(),
                    })

        return {
            "user_stage": user.current_stage,
            "career_paths": user.career_paths,
            "recommendations": rec_items,
            "next_actions": self._generate_next_actions(user),
        }

    def _get_exam_id_by_code(self, exam_code: str) -> Optional[int]:
        exam = self.db.query(Exam).filter(Exam.code == exam_code).first()
        return exam.id if exam else None

    def _generate_next_actions(self, user: User) -> List[str]:
        actions: List[str] = []
        if user.current_stage == "class_12_completed":
            actions.extend([
                "Take mock tests for target exams",
                "Finalize college preferences based on rank",
                "Prepare for counseling/admission process",
            ])
        elif user.current_stage == "undergraduate_started":
            career_paths = user.career_paths or []
            if "engineering" in career_paths:
                actions.extend([
                    "Start building projects for resume",
                    "Plan for GATE preparation (2 years ahead)",
                    "Look for internship opportunities",
                ])
        actions.extend([
            "Complete daily study goals",
            "Review weak topics regularly",
        ])
        return actions
