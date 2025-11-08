import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models import User, Exam, UserActivity, Notification
from database import SessionLocal

class LifecycleStateMachine:
    """
    Manages user lifecycle progression through exam preparation stages
    """

    STAGES = [
        "class_10_completed",
        "class_11_started",
        "class_12_started",
        "class_12_completed",
        "entrance_exams_preparing",
        "undergraduate_started",
        "competitive_exams_preparing",
        "post_graduation",
        "career_started"
    ]

    CAREER_PATHS = {
        "engineering": ["jee_main", "jee_advanced", "bitsat", "viteee"],
        "medical": ["neet", "aiims", "jipmer"],
        "commerce": ["cat", "mat", "xat"],
        "science": ["iisc", "tifr", "ncbs"],
        "civil_services": ["upsc_prelims", "upsc_mains"],
        "defense": ["nda", "cds", "afcat"]
    }

    def __init__(self):
        self.db = SessionLocal()

    def check_stage_progression(self, user_id: int) -> Optional[str]:
        """
        Check if user should progress to next stage based on activities and exam dates
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        current_stage = user.current_stage
        current_time = datetime.utcnow()

        # Check for milestone triggers
        milestone_triggers = user.milestone_triggers or {}

        # Class 12 completion check
        if current_stage == "class_12_started":
            board_exam_date = milestone_triggers.get("board_exam_date")
            if board_exam_date and datetime.fromisoformat(board_exam_date) < current_time:
                return "class_12_completed"

        # Entrance exam results check
        if current_stage == "entrance_exams_preparing":
            jee_result_date = milestone_triggers.get("jee_result_date")
            neet_result_date = milestone_triggers.get("neet_result_date")

            if jee_result_date and datetime.fromisoformat(jee_result_date) < current_time:
                return "college_admission_phase"
            if neet_result_date and datetime.fromisoformat(neet_result_date) < current_time:
                return "college_admission_phase"

        # College start check
        if current_stage == "college_admission_phase":
            college_start_date = milestone_triggers.get("college_start_date")
            if college_start_date and datetime.fromisoformat(college_start_date) < current_time:
                return "undergraduate_started"

        return None

    def progress_user_stage(self, user_id: int, new_stage: str) -> bool:
        """
        Progress user to new stage and update related data
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        # Update user stage
        user.current_stage = new_stage
        user.updated_at = datetime.utcnow()

        # Generate new milestone triggers based on stage
        self._generate_milestone_triggers(user, new_stage)

        # Create notification for stage change
        notification = Notification(
            user_id=user_id,
            notification_type="stage_progression",
            message=f"Congratulations! You've progressed to {new_stage.replace('_', ' ').title()} stage.",
            scheduled_at=datetime.utcnow(),
            channel="push"
        )
        self.db.add(notification)

        # Log activity
        activity = UserActivity(
            user_id=user_id,
            activity_type="stage_progression",
            details=json.dumps({"from_stage": user.current_stage, "to_stage": new_stage}),
            timestamp=datetime.utcnow()
        )
        self.db.add(activity)

        self.db.commit()
        return True

    def _generate_milestone_triggers(self, user: User, new_stage: str):
        """
        Generate appropriate milestone triggers for the new stage
        """
        triggers = {}

        if new_stage == "class_12_completed":
            # Set entrance exam preparation triggers
            triggers.update({
                "jee_application_start": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "neet_application_start": (datetime.utcnow() + timedelta(days=60)).isoformat(),
                "jee_exam_date": (datetime.utcnow() + timedelta(days=120)).isoformat(),
                "neet_exam_date": (datetime.utcnow() + timedelta(days=150)).isoformat()
            })

        elif new_stage == "college_admission_phase":
            triggers.update({
                "college_start_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
                "semester_exam_date": (datetime.utcnow() + timedelta(days=120)).isoformat()
            })

        elif new_stage == "undergraduate_started":
            career_paths = user.career_paths or []
            if "engineering" in career_paths:
                triggers.update({
                    "gate_preparation_start": (datetime.utcnow() + timedelta(days=365*2)).isoformat(),
                    "internship_season": (datetime.utcnow() + timedelta(days=365*2 + 180)).isoformat()
                })

        user.milestone_triggers = json.dumps(triggers)

    def recommend_next_exams(self, user_id: int) -> List[Dict]:
        """
        Recommend next exams based on user stage and career path
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        career_paths = user.career_paths or []
        current_stage = user.current_stage

        recommendations = []

        # Stage-based recommendations
        if current_stage in ["class_12_started", "class_12_completed"]:
            if "engineering" in career_paths:
                recommendations.extend([
                    {"exam": "jee_main", "priority": "high", "reason": "Primary engineering entrance exam"},
                    {"exam": "bitsat", "priority": "medium", "reason": "Alternative private engineering option"},
                    {"exam": "viteee", "priority": "medium", "reason": "VIT engineering entrance"}
                ])
            if "medical" in career_paths:
                recommendations.append({
                    "exam": "neet", "priority": "high", "reason": "Medical entrance exam"
                })

        elif current_stage == "undergraduate_started":
            if "engineering" in career_paths:
                recommendations.extend([
                    {"exam": "gate", "priority": "high", "reason": "Postgraduate engineering studies"},
                    {"exam": "cat", "priority": "medium", "reason": "MBA preparation"}
                ])

        return recommendations

    def update_user_profile(self, user_id: int, profile_data: Dict):
        """
        Update user preparation profile based on activities
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        current_profile = user.preparation_profile or {}

        # Update study hours, strengths, weaknesses
        if "study_hours" in profile_data:
            current_profile["study_hours_per_day"] = profile_data["study_hours"]

        if "topic_performance" in profile_data:
            strengths = current_profile.get("strengths", [])
            weaknesses = current_profile.get("weaknesses", [])

            for topic, score in profile_data["topic_performance"].items():
                if score >= 80:
                    if topic not in strengths:
                        strengths.append(topic)
                    if topic in weaknesses:
                        weaknesses.remove(topic)
                elif score <= 40:
                    if topic not in weaknesses:
                        weaknesses.append(topic)

            current_profile["strengths"] = strengths
            current_profile["weaknesses"] = weaknesses

        user.preparation_profile = json.dumps(current_profile)
        user.updated_at = datetime.utcnow()
        self.db.commit()

    def run_daily_checks(self):
        """
        Run daily lifecycle checks for all users
        """
        users = self.db.query(User).all()

        for user in users:
            # Check for stage progression
            new_stage = self.check_stage_progression(user.id)
            if new_stage:
                self.progress_user_stage(user.id, new_stage)

            # Check milestone triggers
            self._check_milestone_triggers(user)

    def _check_milestone_triggers(self, user: User):
        """
        Check and trigger milestone-based notifications
        """
        triggers = user.milestone_triggers or {}
        current_time = datetime.utcnow()

        for trigger_name, trigger_date_str in triggers.items():
            trigger_date = datetime.fromisoformat(trigger_date_str)

            # Trigger notification 7 days before milestone
            notification_date = trigger_date - timedelta(days=7)

            if current_time >= notification_date:
                # Check if notification already exists
                existing = self.db.query(Notification).filter(
                    Notification.user_id == user.id,
                    Notification.notification_type == "milestone_reminder",
                    Notification.message.contains(trigger_name)
                ).first()

                if not existing:
                    message = self._generate_milestone_message(trigger_name, trigger_date)
                    notification = Notification(
                        user_id=user.id,
                        notification_type="milestone_reminder",
                        message=message,
                        scheduled_at=current_time,
                        channel="push"
                    )
                    self.db.add(notification)

        self.db.commit()

    def _generate_milestone_message(self, trigger_name: str, trigger_date: datetime) -> str:
        """
        Generate appropriate milestone reminder message
        """
        messages = {
            "jee_application_start": f"JEE Main applications open in 7 days ({trigger_date.strftime('%B %d')}). Start preparing your documents!",
            "neet_application_start": f"NEET applications open in 7 days ({trigger_date.strftime('%B %d')}). Ensure you have all required certificates!",
            "jee_exam_date": f"JEE Main exam in 7 days ({trigger_date.strftime('%B %d')}). Final revision phase begins now!",
            "neet_exam_date": f"NEET exam in 7 days ({trigger_date.strftime('%B %d')}). Focus on high-weightage topics!",
            "college_start_date": f"College starts in 7 days ({trigger_date.strftime('%B %d')}). Get ready for your academic journey!",
            "gate_preparation_start": f"Time to start GATE preparation! Exam is in 2 years.",
            "internship_season": "Internship season approaching. Start building your resume and projects!"
        }

        return messages.get(trigger_name, f"Milestone approaching: {trigger_name.replace('_', ' ').title()}")

# Global instance
lifecycle_machine = LifecycleStateMachine()
