"""
Seed the exam knowledge base with a couple of canonical exams (JEE Main, NEET)
and their topic weightages.

Idempotent: if an exam with the same `code` already exists, we skip it so this
script is safe to re-run.
"""
from typing import Dict, List

from sqlalchemy.orm import sessionmaker

from database import engine
from models import Base, Exam, Topic


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _upsert_exam(db, payload: Dict, topics: List[Dict]) -> None:
    existing = db.query(Exam).filter(Exam.code == payload["code"]).first()
    if existing:
        return  # idempotent — keep existing data untouched

    exam = Exam(**payload)
    db.add(exam)
    db.flush()  # populate exam.id before inserting topics

    for t in topics:
        db.add(Topic(
            exam_id=exam.id,
            subject=t["subject"],
            name=t["name"],
            weightage_history=t["weightage_history"],
            avg_questions=t["avg_questions"],
            difficulty_distribution=t["difficulty_distribution"],
            marks_per_hour=t["marks_per_hour"],
            correlation_topics=t.get("correlation_topics", []),
            previous_patterns=t.get("previous_patterns", []),
        ))


def seed_exam_data() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _upsert_exam(
            db,
            payload={
                "name": "JEE Main 2025",
                "code": "jee_main_2025",
                "body": "NTA",
                "exam_type": "engineering_entrance",
                "eligibility": {
                    "education": "Class 12 pass",
                    "age_limit": "No upper age limit",
                    "attempts": "3 attempts",
                },
                "fees": {"general": 1000, "obc": 900, "sc_st": 500, "pwd": 500},
                "important_dates": {
                    "notification": "2024-11-01",
                    "application_start": "2024-11-01",
                    "application_end": "2024-11-30",
                    "exam_dates": [
                        "2025-01-24", "2025-01-25", "2025-01-29",
                        "2025-01-30", "2025-01-31", "2025-02-01",
                    ],
                    "result": "2025-02-12",
                },
                "syllabus": (
                    "Physics: Mechanics, Electromagnetism, Optics, Modern Physics. "
                    "Chemistry: Physical, Organic, Inorganic. "
                    "Mathematics: Calculus, Algebra, Coordinate Geometry, Trigonometry."
                ),
                "pattern": {
                    "total_questions": 90,
                    "marks_per_question": 4,
                    "negative_marking": -1,
                    "sections": ["Physics", "Chemistry", "Mathematics"],
                    "time": 180,
                },
                "centers": ["Delhi", "Mumbai", "Chennai", "Kolkata", "Bangalore"],
                "notification_url": "https://nta.ac.in/",
                "application_url": "https://nta.ac.in/",
                "result_url": "https://nta.ac.in/",
                "subjects": ["physics", "chemistry", "mathematics"],
            },
            topics=[
                {"subject": "physics", "name": "mechanics",
                 "weightage_history": [25, 24, 26, 23, 25], "avg_questions": 8,
                 "difficulty_distribution": {"easy": 40, "medium": 45, "hard": 15},
                 "marks_per_hour": 1.8,
                 "correlation_topics": ["mathematics_calculus", "mathematics_vectors"],
                 "previous_patterns": ["numerical_problems", "conceptual_questions", "graph_based"]},
                {"subject": "physics", "name": "electromagnetism",
                 "weightage_history": [20, 22, 18, 21, 20], "avg_questions": 6,
                 "difficulty_distribution": {"easy": 35, "medium": 50, "hard": 15},
                 "marks_per_hour": 1.5,
                 "correlation_topics": ["mathematics_calculus"],
                 "previous_patterns": ["numerical_problems", "conceptual_questions"]},
                {"subject": "physics", "name": "optics",
                 "weightage_history": [8, 10, 12, 9, 8], "avg_questions": 3,
                 "difficulty_distribution": {"easy": 50, "medium": 40, "hard": 10},
                 "marks_per_hour": 2.2,
                 "correlation_topics": [],
                 "previous_patterns": ["conceptual_questions"]},
                {"subject": "physics", "name": "modern_physics",
                 "weightage_history": [15, 14, 16, 13, 15], "avg_questions": 5,
                 "difficulty_distribution": {"easy": 30, "medium": 45, "hard": 25},
                 "marks_per_hour": 1.3,
                 "correlation_topics": [],
                 "previous_patterns": ["conceptual_questions"]},
                {"subject": "chemistry", "name": "physical_chemistry",
                 "weightage_history": [20, 18, 22, 19, 20], "avg_questions": 6,
                 "difficulty_distribution": {"easy": 45, "medium": 40, "hard": 15},
                 "marks_per_hour": 2.0,
                 "correlation_topics": ["physics_thermodynamics"]},
                {"subject": "chemistry", "name": "organic_chemistry",
                 "weightage_history": [18, 20, 16, 19, 18], "avg_questions": 5,
                 "difficulty_distribution": {"easy": 40, "medium": 45, "hard": 15},
                 "marks_per_hour": 1.8},
                {"subject": "chemistry", "name": "inorganic_chemistry",
                 "weightage_history": [12, 14, 10, 13, 12], "avg_questions": 4,
                 "difficulty_distribution": {"easy": 55, "medium": 35, "hard": 10},
                 "marks_per_hour": 2.5},
                {"subject": "mathematics", "name": "calculus",
                 "weightage_history": [18, 20, 16, 19, 18], "avg_questions": 6,
                 "difficulty_distribution": {"easy": 35, "medium": 45, "hard": 20},
                 "marks_per_hour": 1.7,
                 "correlation_topics": ["physics_mechanics", "physics_electromagnetism"]},
                {"subject": "mathematics", "name": "algebra",
                 "weightage_history": [15, 16, 14, 17, 15], "avg_questions": 5,
                 "difficulty_distribution": {"easy": 40, "medium": 40, "hard": 20},
                 "marks_per_hour": 1.9},
                {"subject": "mathematics", "name": "coordinate_geometry",
                 "weightage_history": [12, 10, 14, 11, 12], "avg_questions": 4,
                 "difficulty_distribution": {"easy": 45, "medium": 40, "hard": 15},
                 "marks_per_hour": 2.1, "correlation_topics": ["mathematics_vectors"]},
                {"subject": "mathematics", "name": "trigonometry",
                 "weightage_history": [8, 9, 7, 10, 8], "avg_questions": 3,
                 "difficulty_distribution": {"easy": 50, "medium": 35, "hard": 15},
                 "marks_per_hour": 2.3},
            ],
        )

        _upsert_exam(
            db,
            payload={
                "name": "NEET 2025",
                "code": "neet_2025",
                "body": "NTA",
                "exam_type": "medical_entrance",
                "eligibility": {
                    "education": "Class 12 pass with PCB",
                    "minimum_marks": "50% aggregate (40% for reserved)",
                    "age_limit": "17-25 years (relaxation for reserved)",
                },
                "fees": {"general": 1700, "obc": 1600, "sc_st": 1000},
                "important_dates": {
                    "notification": "2024-12-01",
                    "application_start": "2024-12-01",
                    "application_end": "2024-12-31",
                    "exam_dates": ["2025-05-04"],
                    "result": "2025-06-14",
                },
                "syllabus": (
                    "Physics, Chemistry, Biology (Botany + Zoology) — NCERT-aligned."
                ),
                "pattern": {
                    "total_questions": 200,
                    "marks_per_question": 4,
                    "negative_marking": -1,
                    "sections": ["Physics", "Chemistry", "Biology"],
                    "time": 200,
                },
                "centers": ["All major cities in India"],
                "notification_url": "https://nta.ac.in/",
                "application_url": "https://nta.ac.in/",
                "result_url": "https://nta.ac.in/",
                "subjects": ["physics", "chemistry", "biology"],
            },
            topics=[
                {"subject": "biology", "name": "human_physiology",
                 "weightage_history": [30, 28, 32, 29, 30], "avg_questions": 20,
                 "difficulty_distribution": {"easy": 40, "medium": 45, "hard": 15},
                 "marks_per_hour": 2.0},
                {"subject": "biology", "name": "genetics",
                 "weightage_history": [18, 20, 16, 19, 18], "avg_questions": 12,
                 "difficulty_distribution": {"easy": 35, "medium": 50, "hard": 15},
                 "marks_per_hour": 1.8},
                {"subject": "biology", "name": "ecology",
                 "weightage_history": [19, 17, 21, 18, 19], "avg_questions": 13,
                 "difficulty_distribution": {"easy": 45, "medium": 40, "hard": 15},
                 "marks_per_hour": 2.1},
                {"subject": "biology", "name": "plant_physiology",
                 "weightage_history": [15, 16, 14, 17, 15], "avg_questions": 10,
                 "difficulty_distribution": {"easy": 50, "medium": 35, "hard": 15},
                 "marks_per_hour": 2.2},
                {"subject": "biology", "name": "animal_kingdom",
                 "weightage_history": [12, 14, 10, 13, 12], "avg_questions": 8,
                 "difficulty_distribution": {"easy": 55, "medium": 35, "hard": 10},
                 "marks_per_hour": 2.5},
            ],
        )

        db.commit()
        print("Exam knowledge base seeded successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_exam_data()
