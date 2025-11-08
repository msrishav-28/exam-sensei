from sqlalchemy.orm import sessionmaker
from models import Exam, Topic, Base
from database import engine
import json

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_exam_data():
    # Create tables first
    Base.metadata.create_all(bind=engine)

    # JEE Main Exam
    jee_main = Exam(
        name="JEE Main 2025",
        code="jee_main_2025",
        body="NTA",
        exam_type="engineering_entrance",
        eligibility=json.dumps({
            "education": "Class 12 pass",
            "age_limit": "No upper age limit",
            "attempts": "3 attempts"
        }),
        fees=json.dumps({
            "general": 1000,
            "obc": 900,
            "sc_st": 500,
            "pwd": 500
        }),
        important_dates=json.dumps({
            "notification": "2024-11-01",
            "application_start": "2024-11-01",
            "application_end": "2024-11-30",
            "exam_dates": ["2025-01-24", "2025-01-25", "2025-01-29", "2025-01-30", "2025-01-31", "2025-02-01"],
            "result": "2025-02-12"
        }),
        syllabus=json.dumps({
            "physics": ["Mechanics", "Electromagnetism", "Optics", "Modern Physics"],
            "chemistry": ["Physical Chemistry", "Organic Chemistry", "Inorganic Chemistry"],
            "mathematics": ["Calculus", "Algebra", "Coordinate Geometry", "Trigonometry"]
        }),
        pattern=json.dumps({
            "total_questions": 90,
            "marks_per_question": 4,
            "negative_marking": -1,
            "sections": ["Physics", "Chemistry", "Mathematics"],
            "time": 180
        }),
        centers=json.dumps(["Delhi", "Mumbai", "Chennai", "Kolkata", "Bangalore"]),
        notification_url="https://nta.ac.in/",
        application_url="https://nta.ac.in/",
        result_url="https://nta.ac.in/",
        subjects=json.dumps(["physics", "chemistry", "mathematics"])
    )

    db.add(jee_main)
    db.commit()
    db.refresh(jee_main)

    # JEE Main Topics with weightage
    jee_topics = [
        # Physics
        {"subject": "physics", "name": "mechanics", "weightage_history": [25, 24, 26, 23, 25], "avg_questions": 8, "difficulty_distribution": {"easy": 40, "medium": 45, "hard": 15}, "marks_per_hour": 1.8, "correlation_topics": ["mathematics_calculus", "mathematics_vectors"]},
        {"subject": "physics", "name": "electromagnetism", "weightage_history": [20, 22, 18, 21, 20], "avg_questions": 6, "difficulty_distribution": {"easy": 35, "medium": 50, "hard": 15}, "marks_per_hour": 1.5, "correlation_topics": ["mathematics_calculus"]},
        {"subject": "physics", "name": "optics", "weightage_history": [8, 10, 12, 9, 8], "avg_questions": 3, "difficulty_distribution": {"easy": 50, "medium": 40, "hard": 10}, "marks_per_hour": 2.2, "correlation_topics": []},
        {"subject": "physics", "name": "modern_physics", "weightage_history": [15, 14, 16, 13, 15], "avg_questions": 5, "difficulty_distribution": {"easy": 30, "medium": 45, "hard": 25}, "marks_per_hour": 1.3, "correlation_topics": []},

        # Chemistry
        {"subject": "chemistry", "name": "physical_chemistry", "weightage_history": [20, 18, 22, 19, 20], "avg_questions": 6, "difficulty_distribution": {"easy": 45, "medium": 40, "hard": 15}, "marks_per_hour": 2.0, "correlation_topics": ["physics_thermodynamics"]},
        {"subject": "chemistry", "name": "organic_chemistry", "weightage_history": [18, 20, 16, 19, 18], "avg_questions": 5, "difficulty_distribution": {"easy": 40, "medium": 45, "hard": 15}, "marks_per_hour": 1.8, "correlation_topics": []},
        {"subject": "chemistry", "name": "inorganic_chemistry", "weightage_history": [12, 14, 10, 13, 12], "avg_questions": 4, "difficulty_distribution": {"easy": 55, "medium": 35, "hard": 10}, "marks_per_hour": 2.5, "correlation_topics": []},

        # Mathematics
        {"subject": "mathematics", "name": "calculus", "weightage_history": [18, 20, 16, 19, 18], "avg_questions": 6, "difficulty_distribution": {"easy": 35, "medium": 45, "hard": 20}, "marks_per_hour": 1.7, "correlation_topics": ["physics_mechanics", "physics_electromagnetism"]},
        {"subject": "mathematics", "name": "algebra", "weightage_history": [15, 16, 14, 17, 15], "avg_questions": 5, "difficulty_distribution": {"easy": 40, "medium": 40, "hard": 20}, "marks_per_hour": 1.9, "correlation_topics": []},
        {"subject": "mathematics", "name": "coordinate_geometry", "weightage_history": [12, 10, 14, 11, 12], "avg_questions": 4, "difficulty_distribution": {"easy": 45, "medium": 40, "hard": 15}, "marks_per_hour": 2.1, "correlation_topics": ["mathematics_vectors"]},
        {"subject": "mathematics", "name": "trigonometry", "weightage_history": [8, 9, 7, 10, 8], "avg_questions": 3, "difficulty_distribution": {"easy": 50, "medium": 35, "hard": 15}, "marks_per_hour": 2.3, "correlation_topics": []}
    ]

    for topic_data in jee_topics:
        topic = Topic(
            exam_id=jee_main.id,
            subject=topic_data["subject"],
            name=topic_data["name"],
            weightage_history=json.dumps(topic_data["weightage_history"]),
            avg_questions=topic_data["avg_questions"],
            difficulty_distribution=json.dumps(topic_data["difficulty_distribution"]),
            marks_per_hour=topic_data["marks_per_hour"],
            correlation_topics=json.dumps(topic_data["correlation_topics"]),
            previous_patterns=json.dumps(["numerical_problems", "conceptual_questions", "graph_based"])
        )
        db.add(topic)

    # NEET Exam
    neet = Exam(
        name="NEET 2025",
        code="neet_2025",
        body="NTA",
        exam_type="medical_entrance",
        eligibility=json.dumps({
            "education": "Class 12 pass with PCB",
            "minimum_marks": "50% aggregate (40% for reserved)",
            "age_limit": "17-25 years (relaxation for reserved)"
        }),
        fees=json.dumps({
            "general": 1700,
            "obc": 1600,
            "sc_st": 1000
        }),
        important_dates=json.dumps({
            "notification": "2024-12-01",
            "application_start": "2024-12-01",
            "application_end": "2024-12-31",
            "exam_date": "2025-05-04",
            "result": "2025-06-14"
        }),
        syllabus=json.dumps({
            "physics": ["Mechanics", "Electromagnetism", "Optics", "Modern Physics"],
            "chemistry": ["Physical Chemistry", "Organic Chemistry", "Inorganic Chemistry"],
            "biology": ["Botany", "Zoology"]
        }),
        pattern=json.dumps({
            "total_questions": 200,
            "marks_per_question": 4,
            "negative_marking": -1,
            "sections": ["Physics", "Chemistry", "Biology"],
            "time": 200
        }),
        centers=json.dumps(["All major cities in India"]),
        notification_url="https://nta.ac.in/",
        application_url="https://nta.ac.in/",
        result_url="https://nta.ac.in/",
        subjects=json.dumps(["physics", "chemistry", "biology"])
    )

    db.add(neet)
    db.commit()
    db.refresh(neet)

    # NEET Topics
    neet_topics = [
        # Biology
        {"subject": "biology", "name": "human_physiology", "weightage_history": [30, 28, 32, 29, 30], "avg_questions": 20, "difficulty_distribution": {"easy": 40, "medium": 45, "hard": 15}, "marks_per_hour": 2.0, "correlation_topics": []},
        {"subject": "biology", "name": "genetics", "weightage_history": [18, 20, 16, 19, 18], "avg_questions": 12, "difficulty_distribution": {"easy": 35, "medium": 50, "hard": 15}, "marks_per_hour": 1.8, "correlation_topics": []},
        {"subject": "biology", "name": "ecology", "weightage_history": [19, 17, 21, 18, 19], "avg_questions": 13, "difficulty_distribution": {"easy": 45, "medium": 40, "hard": 15}, "marks_per_hour": 2.1, "correlation_topics": []},
        {"subject": "biology", "name": "plant_physiology", "weightage_history": [15, 16, 14, 17, 15], "avg_questions": 10, "difficulty_distribution": {"easy": 50, "medium": 35, "hard": 15}, "marks_per_hour": 2.2, "correlation_topics": []},
        {"subject": "biology", "name": "animal_kingdom", "weightage_history": [12, 14, 10, 13, 12], "avg_questions": 8, "difficulty_distribution": {"easy": 55, "medium": 35, "hard": 10}, "marks_per_hour": 2.5, "correlation_topics": []}
    ]

    for topic_data in neet_topics:
        topic = Topic(
            exam_id=neet.id,
            subject=topic_data["subject"],
            name=topic_data["name"],
            weightage_history=json.dumps(topic_data["weightage_history"]),
            avg_questions=topic_data["avg_questions"],
            difficulty_distribution=json.dumps(topic_data["difficulty_distribution"]),
            marks_per_hour=topic_data["marks_per_hour"],
            correlation_topics=json.dumps(topic_data["correlation_topics"]),
            previous_patterns=json.dumps(["fact_based", "diagram_based", "application_questions"])
        )
        db.add(topic)

    db.commit()
    print("Exam knowledge base seeded successfully!")

if __name__ == "__main__":
    seed_exam_data()
