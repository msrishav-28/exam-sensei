import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import User, Exam, Topic, Recommendation
from lifecycle import lifecycle_machine

class CareerRecommender:
    """
    AI-powered career path recommender based on user profile and performance
    """

    CAREER_MAPPINGS = {
        "engineering": {
            "jee_score_ranges": [(0, 50), (50, 100), (100, 150), (150, 200), (200, 300)],
            "colleges": [
                "Tier 3: State colleges",
                "Tier 2: NITs, IIITs",
                "Tier 2: BITS Pilani, VIT",
                "Tier 1: IITs, IIIT Hyderabad",
                "Tier 1: IIT Bombay, IIT Delhi"
            ],
            "next_steps": [
                "Consider diploma + lateral entry",
                "Focus on state CET exams",
                "Apply to private universities",
                "Secure IIT seat",
                "Top IITs - research opportunities"
            ]
        },
        "medical": {
            "neet_score_ranges": [(0, 200), (200, 400), (400, 500), (500, 600), (600, 720)],
            "colleges": [
                "Private medical colleges",
                "State government colleges",
                "AIIMS, JIPMER",
                "Top AIIMS institutes",
                "AIIMS Delhi, PGIMER"
            ]
        }
    }

    @staticmethod
    def recommend_career_path(user_profile: Dict, exam_scores: Dict) -> Dict:
        """
        Recommend career path based on user profile and exam performance
        """
        interests = user_profile.get("interests", [])
        budget = user_profile.get("budget", "medium")
        location = user_profile.get("location", "any")

        recommendations = []

        # Engineering recommendations
        if "engineering" in interests or "technology" in interests:
            jee_score = exam_scores.get("jee_main", 0)
            eng_rec = CareerRecommender._get_engineering_recommendation(jee_score, budget, location)
            recommendations.append(eng_rec)

        # Medical recommendations
        if "medical" in interests or "biology" in interests:
            neet_score = exam_scores.get("neet", 0)
            med_rec = CareerRecommender._get_medical_recommendation(neet_score, budget, location)
            recommendations.append(med_rec)

        # Commerce recommendations
        if "commerce" in interests or "business" in interests:
            commerce_rec = {
                "career_path": "commerce",
                "recommended_exams": ["cat", "mat", "cuet"],
                "colleges": ["Delhi University", "SRCC", "LBSIM"],
                "reasoning": "Strong foundation in commerce subjects, good analytical skills"
            }
            recommendations.append(commerce_rec)

        return {
            "primary_recommendation": recommendations[0] if recommendations else None,
            "alternative_paths": recommendations[1:] if len(recommendations) > 1 else [],
            "confidence_score": 0.85
        }

    @staticmethod
    def _get_engineering_recommendation(jee_score: int, budget: str, location: str) -> Dict:
        """Get engineering career recommendation"""
        percentile = min(jee_score / 3, 100)  # Rough percentile calculation

        tier_index = min(int(percentile / 20), 4)  # 0-4 tiers

        return {
            "career_path": "engineering",
            "jee_percentile": percentile,
            "recommended_tier": CareerRecommender.CAREER_MAPPINGS["engineering"]["colleges"][tier_index],
            "next_steps": CareerRecommender.CAREER_MAPPINGS["engineering"]["next_steps"][tier_index],
            "budget_alignment": "high" if percentile > 80 else "medium" if percentile > 50 else "low",
            "timeline": "4 years undergraduate + 2 years masters" if percentile > 90 else "4 years undergraduate"
        }

    @staticmethod
    def _get_medical_recommendation(neet_score: int, budget: str, location: str) -> Dict:
        """Get medical career recommendation"""
        percentile = min(neet_score / 7.2, 100)  # Rough percentile calculation

        tier_index = min(int(percentile / 20), 4)

        return {
            "career_path": "medical",
            "neet_percentile": percentile,
            "recommended_tier": CareerRecommender.CAREER_MAPPINGS["medical"]["colleges"][tier_index],
            "specializations": ["General Medicine", "Surgery", "Pediatrics", "Gynecology"][:tier_index+1],
            "timeline": "5.5 years MBBS + 3 years MD/MS"
        }

class TopicPrioritizer:
    """
    AI-powered topic prioritization based on exam weightage and user performance
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_study_plan(self, user_id: int, exam_code: str, days_available: int) -> Dict:
        """
        Generate personalized study plan using topic prioritization algorithm
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        exam = self.db.query(Exam).filter(Exam.code == exam_code).first()

        if not user or not exam:
            return {"error": "User or exam not found"}

        # Get user's preparation profile
        profile = user.preparation_profile or {}
        strengths = profile.get("strengths", [])
        weaknesses = profile.get("weaknesses", [])

        # Get exam topics
        topics = self.db.query(Topic).filter(Topic.exam_id == exam.id).all()

        # Calculate priority scores for each topic
        prioritized_topics = []
        for topic in topics:
            priority_score = self._calculate_priority_score(topic, strengths, weaknesses, days_available)
            prioritized_topics.append({
                "topic": topic,
                "priority_score": priority_score,
                "estimated_days": self._estimate_study_days(topic, profile),
                "difficulty": self._get_topic_difficulty(topic),
                "weightage": json.loads(topic.weightage_history)[-1] if topic.weightage_history else 0
            })

        # Sort by priority score
        prioritized_topics.sort(key=lambda x: x["priority_score"], reverse=True)

        # Generate weekly plan
        study_plan = self._create_weekly_plan(prioritized_topics, days_available)

        return {
            "exam_code": exam_code,
            "total_days": days_available,
            "prioritized_topics": prioritized_topics[:10],  # Top 10
            "weekly_plan": study_plan,
            "estimated_completion": f"{days_available} days from now",
            "success_probability": self._calculate_success_probability(prioritized_topics, profile)
        }

    def _calculate_priority_score(self, topic: Topic, strengths: List, weaknesses: List, days_available: int) -> float:
        """
        Calculate priority score: (weightage × gap_from_target) / time_required
        """
        weightage = json.loads(topic.weightage_history)[-1] if topic.weightage_history else 10

        # Gap from target (higher if it's a weakness)
        gap_multiplier = 2.0 if topic.name in weaknesses else 1.0
        if topic.name in strengths:
            gap_multiplier = 0.5

        # Time required (based on difficulty and questions)
        time_required = topic.avg_questions * 2  # Rough estimate: 2 hours per question

        # Adjust for available time
        time_pressure = max(1, days_available / 90)  # Normalize to 3 months

        priority_score = (weightage * gap_multiplier * time_pressure) / time_required

        return round(priority_score, 2)

    def _estimate_study_days(self, topic: Topic, profile: Dict) -> int:
        """Estimate days needed to master a topic"""
        base_days = topic.avg_questions // 2  # 2 questions per day
        study_hours_per_day = profile.get("study_hours_per_day", 6)

        # Adjust based on difficulty
        difficulty_multiplier = 1.5 if topic.name in ["modern_physics", "organic_chemistry"] else 1.0

        return max(1, int(base_days * difficulty_multiplier / study_hours_per_day))

    def _get_topic_difficulty(self, topic: Topic) -> str:
        """Get topic difficulty level"""
        difficulty_dist = json.loads(topic.difficulty_distribution)
        hard_pct = difficulty_dist.get("hard", 0)

        if hard_pct > 20:
            return "hard"
        elif hard_pct > 10:
            return "medium"
        else:
            return "easy"

    def _create_weekly_plan(self, prioritized_topics: List, total_days: int) -> Dict:
        """Create weekly study plan"""
        weeks = total_days // 7
        plan = {}

        topic_index = 0
        for week in range(1, weeks + 1):
            weekly_topics = []
            week_days = 7 if week <= weeks else total_days % 7

            for day in range(1, week_days + 1):
                if topic_index < len(prioritized_topics):
                    topic_data = prioritized_topics[topic_index]
                    weekly_topics.append({
                        "day": f"Week {week}, Day {day}",
                        "topic": topic_data["topic"].name,
                        "focus_area": f"High-weightage ({topic_data['weightage']}%)",
                        "estimated_hours": 6,
                        "difficulty": topic_data["difficulty"]
                    })
                    topic_index += 1

            plan[f"week_{week}"] = weekly_topics

        return plan

    def _calculate_success_probability(self, topics: List, profile: Dict) -> float:
        """Calculate estimated success probability"""
        total_weightage_covered = sum(t["weightage"] for t in topics[:20])  # Top 20 topics
        study_consistency = profile.get("study_consistency", 0.7)

        # Rough formula: coverage * consistency * difficulty_factor
        base_probability = min(total_weightage_covered / 100, 1.0)
        adjusted_probability = base_probability * study_consistency * 0.9

        return round(adjusted_probability, 2)

class ExamClashDetector:
    """
    Detect and resolve exam date conflicts
    """

    def detect_clashes(self, user_exams: List[str], db: Session) -> Dict:
        """
        Detect conflicting exam dates
        """
        exam_dates = {}
        for exam_code in user_exams:
            exam = db.query(Exam).filter(Exam.code == exam_code).first()
            if exam and exam.important_dates:
                dates = json.loads(exam.important_dates)
                exam_dates[exam_code] = dates.get("exam_dates", [])

        clashes = []
        for i, (exam1, dates1) in enumerate(exam_dates.items()):
            for j, (exam2, dates2) in enumerate(exam_dates.items()):
                if i < j:  # Avoid duplicate comparisons
                    overlapping_dates = set(dates1) & set(dates2)
                    if overlapping_dates:
                        clashes.append({
                            "exams": [exam1, exam2],
                            "conflicting_dates": list(overlapping_dates),
                            "severity": "high" if len(overlapping_dates) > 1 else "medium"
                        })

        return {
            "has_clashes": len(clashes) > 0,
            "clashes": clashes,
            "recommendations": self._generate_clash_resolutions(clashes, user_exams)
        }

    def _generate_clash_resolutions(self, clashes: List, user_exams: List) -> List:
        """Generate resolution recommendations"""
        if not clashes:
            return ["No clashes detected. You can prepare for all exams simultaneously."]

        recommendations = []

        for clash in clashes:
            exam1, exam2 = clash["exams"]
            recommendations.append(
                f"Consider prioritizing {exam1} over {exam2} if your career goals align more closely with {exam1}."
            )
            recommendations.append(
                f"Look for rescheduled dates or consider taking one exam in the next session."
            )

        return recommendations

class AdaptiveMentor:
    """
    Main AI mentor that combines all components
    """

    def __init__(self, db: Session):
        self.db = db
        self.topic_prioritizer = TopicPrioritizer(db)
        self.clash_detector = ExamClashDetector()

    def get_personalized_recommendations(self, user_id: int) -> Dict:
        """
        Get comprehensive personalized recommendations
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}

        recommendations = []

        # Stage-based exam recommendations
        exam_recs = lifecycle_machine.recommend_next_exams(user_id)
        for rec in exam_recs:
            recommendation = Recommendation(
                user_id=user_id,
                exam_id=self._get_exam_id_by_code(rec["exam"]),
                recommendation_type="career_path",
                score=0.9 if rec["priority"] == "high" else 0.7,
                reasoning=rec["reason"],
                expires_at=datetime.utcnow() + timedelta(days=90)
            )
            recommendations.append(recommendation)

        # Clash detection
        active_exams = user.active_exams or []
        if len(active_exams) > 1:
            clashes = self.clash_detector.detect_clashes(active_exams, self.db)
            if clashes["has_clashes"]:
                for clash in clashes["clashes"]:
                    recommendation = Recommendation(
                        user_id=user_id,
                        recommendation_type="clash_alert",
                        score=0.95,
                        reasoning=f"Exam clash detected between {', '.join(clash['exams'])}. {clashes['recommendations'][0]}",
                        expires_at=datetime.utcnow() + timedelta(days=30)
                    )
                    recommendations.append(recommendation)

        # Save recommendations
        for rec in recommendations:
            self.db.add(rec)
        self.db.commit()

        return {
            "user_stage": user.current_stage,
            "career_paths": user.career_paths,
            "recommendations": [
                {
                    "type": rec.recommendation_type,
                    "exam": rec.exam.name if rec.exam else None,
                    "score": rec.score,
                    "reasoning": rec.reasoning
                } for rec in recommendations
            ],
            "next_actions": self._generate_next_actions(user)
        }

    def _get_exam_id_by_code(self, exam_code: str) -> Optional[int]:
        """Get exam ID by code"""
        exam = self.db.query(Exam).filter(Exam.code == exam_code).first()
        return exam.id if exam else None

    def _generate_next_actions(self, user: User) -> List[str]:
        """Generate next action items"""
        actions = []

        if user.current_stage == "class_12_completed":
            actions.append("Take mock tests for target exams")
            actions.append("Finalize college preferences based on rank")
            actions.append("Prepare for counseling/admission process")

        elif user.current_stage == "undergraduate_started":
            career_paths = user.career_paths or []
            if "engineering" in career_paths:
                actions.append("Start building projects for resume")
                actions.append("Plan for GATE preparation (2 years ahead)")
                actions.append("Look for internship opportunities")

        actions.append("Complete daily study goals")
        actions.append("Review weak topics regularly")

        return actions
