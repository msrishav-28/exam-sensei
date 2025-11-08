import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Conversation, Exam, Topic
from ai_models import AdaptiveMentor, TopicPrioritizer
from lifecycle import lifecycle_machine

class ExamSenseiChatbot:
    """
    Conversational AI mentor using Ollama for natural language understanding
    """

    def __init__(self, db: Session, ollama_url: str = "http://localhost:11434"):
        self.db = db
        self.ollama_url = ollama_url
        self.mentor = AdaptiveMentor(db)
        self.topic_prioritizer = TopicPrioritizer(db)

        # System prompt for the chatbot
        self.system_prompt = """
        You are ExamSensei, an intelligent AI mentor for competitive exam preparation in India.
        You help students through their entire exam journey from Class 12 to career advancement.

        Your capabilities:
        - Provide personalized study advice based on user's current stage and performance
        - Recommend career paths and exam strategies
        - Explain complex topics in simple terms
        - Motivate and provide emotional support
        - Track progress and suggest improvements
        - Answer questions about exams, syllabus, and preparation strategies

        Guidelines:
        - Be encouraging and supportive
        - Provide specific, actionable advice
        - Use simple language, avoid jargon unless explaining it
        - Focus on Indian competitive exams (JEE, NEET, GATE, UPSC, etc.)
        - Consider user's current lifecycle stage in your responses
        - If uncertain, ask clarifying questions
        - Always end responses with specific next steps when appropriate

        Current context will be provided with each query.
        """

    def process_message(self, user_id: int, message: str, session_id: str = None) -> Dict:
        """
        Process user message and generate response
        """
        if not session_id:
            session_id = f"session_{user_id}_{datetime.utcnow().timestamp()}"

        # Get user context
        user_context = self._get_user_context(user_id)

        # Analyze intent and extract entities
        intent_analysis = self._analyze_intent(message, user_context)

        # Generate response based on intent
        response = self._generate_response(intent_analysis, user_context, message)

        # Save conversation
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            message=message,
            response=response["text"],
            intent=intent_analysis["intent"],
            context=json.dumps(user_context),
            timestamp=datetime.utcnow()
        )
        self.db.add(conversation)
        self.db.commit()

        # Add actions if any
        if "actions" in response:
            response["suggested_actions"] = response["actions"]

        return {
            "response": response["text"],
            "intent": intent_analysis["intent"],
            "confidence": intent_analysis["confidence"],
            "suggested_actions": response.get("actions", []),
            "session_id": session_id
        }

    def _get_user_context(self, user_id: int) -> Dict:
        """Get comprehensive user context for personalization"""
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return {"error": "User not found"}

        context = {
            "user_id": user_id,
            "current_stage": user.current_stage,
            "career_paths": user.career_paths or [],
            "active_exams": user.active_exams or [],
            "preparation_profile": user.preparation_profile or {},
            "education_level": user.education_level,
            "state": user.state,
            "category": user.category,
            "budget": user.budget
        }

        # Add recent activities
        recent_activities = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.timestamp.desc()).limit(5).all()

        context["recent_conversations"] = [
            {"message": conv.message, "intent": conv.intent, "timestamp": conv.timestamp.isoformat()}
            for conv in recent_activities
        ]

        return context

    def _analyze_intent(self, message: str, context: Dict) -> Dict:
        """Analyze user intent using pattern matching and context"""
        message_lower = message.lower()

        # Career guidance intents
        if any(word in message_lower for word in ["career", "future", "become", "job", "profession"]):
            return {"intent": "career_guidance", "confidence": 0.9, "entities": self._extract_career_entities(message)}

        # Study planning intents
        elif any(word in message_lower for word in ["study", "prepare", "plan", "schedule", "timetable"]):
            return {"intent": "study_planning", "confidence": 0.9, "entities": self._extract_study_entities(message)}

        # Topic explanation intents
        elif any(word in message_lower for word in ["explain", "understand", "help with", "confused about"]):
            return {"intent": "topic_explanation", "confidence": 0.8, "entities": self._extract_topic_entities(message)}

        # Performance analysis intents
        elif any(word in message_lower for word in ["score", "performance", "weak", "strong", "improve"]):
            return {"intent": "performance_analysis", "confidence": 0.85, "entities": {}}

        # Motivational support intents
        elif any(word in message_lower for word in ["motivate", "tired", "stressed", "difficult", "can't"]):
            return {"intent": "motivational_support", "confidence": 0.9, "entities": {}}

        # Exam information intents
        elif any(word in message_lower for word in ["exam", "jee", "neet", "gate", "dates", "syllabus", "pattern"]):
            return {"intent": "exam_information", "confidence": 0.9, "entities": self._extract_exam_entities(message)}

        # General query - use Ollama for deeper analysis
        else:
            ollama_intent = self._ollama_intent_analysis(message, context)
            return ollama_intent

    def _ollama_intent_analysis(self, message: str, context: Dict) -> Dict:
        """Use Ollama for intent analysis when pattern matching fails"""
        try:
            prompt = f"""
            Analyze this user message in the context of competitive exam preparation:

            User Context: {json.dumps(context, indent=2)}
            Message: "{message}"

            Classify the intent into one of these categories:
            - career_guidance
            - study_planning
            - topic_explanation
            - performance_analysis
            - motivational_support
            - exam_information
            - general_query

            Return JSON format:
            {{"intent": "category", "confidence": 0.8, "reasoning": "brief explanation", "entities": {{"key": "value"}}}}
            """

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama2",  # or whichever model you have
                    "prompt": prompt,
                    "format": "json",
                    "stream": False
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                return json.loads(result.get("response", "{}"))
            else:
                return {"intent": "general_query", "confidence": 0.5, "entities": {}}

        except Exception as e:
            print(f"Ollama intent analysis failed: {e}")
            return {"intent": "general_query", "confidence": 0.5, "entities": {}}

    def _generate_response(self, intent_analysis: Dict, context: Dict, original_message: str) -> Dict:
        """Generate appropriate response based on intent"""
        intent = intent_analysis["intent"]
        entities = intent_analysis.get("entities", {})

        if intent == "career_guidance":
            return self._handle_career_guidance(context, entities)

        elif intent == "study_planning":
            return self._handle_study_planning(context, entities)

        elif intent == "topic_explanation":
            return self._handle_topic_explanation(context, entities, original_message)

        elif intent == "performance_analysis":
            return self._handle_performance_analysis(context)

        elif intent == "motivational_support":
            return self._handle_motivational_support(context)

        elif intent == "exam_information":
            return self._handle_exam_information(context, entities)

        else:
            return self._handle_general_query(context, original_message)

    def _handle_career_guidance(self, context: Dict, entities: Dict) -> Dict:
        """Handle career guidance queries"""
        career_paths = context.get("career_paths", [])
        current_stage = context.get("current_stage", "")

        if not career_paths:
            return {
                "text": "I'd love to help you with career guidance! To give you the best advice, could you tell me what subjects you're interested in? For example: engineering, medical, commerce, science research, or civil services?",
                "actions": ["Share your interests", "Tell me about your strengths"]
            }

        # Get personalized recommendations
        recommendations = self.mentor.get_personalized_recommendations(context["user_id"])

        response_text = f"Based on your current stage ({current_stage}) and interests in {', '.join(career_paths)}, here's my recommendation:\n\n"

        if recommendations.get("primary_recommendation"):
            rec = recommendations["primary_recommendation"]
            response_text += f"**Primary Path**: {rec.get('career_path', '').title()}\n"
            if 'jee_percentile' in rec:
                response_text += f"- Your JEE percentile suggests: {rec['recommended_tier']}\n"
            if 'next_steps' in rec:
                response_text += f"- Next steps: {rec['next_steps']}\n"

        response_text += "\nRemember, this is just a starting point. Your hard work and consistency will determine your success!"

        return {
            "text": response_text,
            "actions": recommendations.get("next_actions", [])
        }

    def _handle_study_planning(self, context: Dict, entities: Dict) -> Dict:
        """Handle study planning queries"""
        active_exams = context.get("active_exams", [])

        if not active_exams:
            return {
                "text": "I'd be happy to help you create a study plan! Which exam are you preparing for? JEE Main, NEET, GATE, or something else?",
                "actions": ["Tell me your target exam", "Share how many hours you study daily"]
            }

        # Generate study plan for primary exam
        exam_code = active_exams[0]
        days_available = entities.get("days", 90)  # Default 3 months

        try:
            plan = self.topic_prioritizer.generate_study_plan(context["user_id"], exam_code, days_available)

            response_text = f"Here's your personalized {days_available}-day study plan for {exam_code.upper()}:\n\n"

            # Show top 3 priorities
            priorities = plan.get("prioritized_topics", [])[:3]
            for i, topic_data in enumerate(priorities, 1):
                topic = topic_data["topic"]
                response_text += f"{i}. **{topic.name.title()}** (Weightage: {topic_data['weightage']}%, Difficulty: {topic_data['difficulty']})\n"

            response_text += f"\nEstimated success probability: {plan.get('success_probability', 0)*100:.0f}%\n\n"
            response_text += "Focus on your weak areas while maintaining strengths. Consistency is key! 💪"

            return {
                "text": response_text,
                "actions": ["Start with the highest priority topic", "Set daily study goals", "Take weekly mock tests"]
            }

        except Exception as e:
            return {
                "text": f"I encountered an issue generating your study plan. Could you provide more details about your target exam and available time?",
                "actions": ["Specify your exam", "Tell me your available study time"]
            }

    def _handle_topic_explanation(self, context: Dict, entities: Dict, message: str) -> Dict:
        """Handle topic explanation requests"""
        # Extract topic from message
        topic_keywords = ["physics", "chemistry", "math", "biology", "calculus", "mechanics", "organic", "inorganic"]
        mentioned_topic = None

        for keyword in topic_keywords:
            if keyword in message.lower():
                mentioned_topic = keyword
                break

        if not mentioned_topic:
            return {
                "text": "I'd love to help explain a topic! Which subject or specific topic are you struggling with? For example: 'Explain calculus' or 'Help with organic chemistry'",
                "actions": ["Specify the topic", "Tell me what you already understand"]
            }

        # Generate explanation using Ollama
        explanation = self._generate_topic_explanation(mentioned_topic, context)

        return {
            "text": explanation,
            "actions": ["Practice related problems", "Watch video tutorials", "Ask specific questions about this topic"]
        }

    def _handle_performance_analysis(self, context: Dict) -> Dict:
        """Handle performance analysis queries"""
        profile = context.get("preparation_profile", {})

        response_text = "Let's analyze your current performance:\n\n"

        strengths = profile.get("strengths", [])
        weaknesses = profile.get("weaknesses", [])

        if strengths:
            response_text += f"**Strengths**: {', '.join(strengths)}\n"
        if weaknesses:
            response_text += f"**Areas to improve**: {', '.join(weaknesses)}\n"

        study_hours = profile.get("study_hours_per_day", 0)
        response_text += f"**Daily study hours**: {study_hours}\n\n"

        if weaknesses:
            response_text += "Focus on your weak areas - they're your biggest opportunity for score improvement!\n"
            response_text += "Spend 60% of your time on weaknesses, 40% on maintaining strengths."

        return {
            "text": response_text,
            "actions": ["Take a diagnostic test", "Focus on weak topics", "Track your daily progress"]
        }

    def _handle_motivational_support(self, context: Dict) -> Dict:
        """Handle motivational support"""
        stage = context.get("current_stage", "")

        motivation_messages = {
            "class_12_completed": "Congratulations on completing Class 12! This is a crucial turning point. Your JEE/NEET preparation will shape your future. Stay consistent - success comes from daily effort, not motivation bursts.",
            "entrance_exams_preparing": "Exam preparation is a marathon, not a sprint. Every day you study brings you closer to your goals. Remember why you started - your dreams are worth the effort!",
            "undergraduate_started": "College life + competitive exams is challenging, but you're building incredible skills. Your future self will thank you for this discipline. Keep pushing!"
        }

        message = motivation_messages.get(stage, "You're capable of amazing things! Every expert was once a beginner. Your consistent effort will compound into success. Stay focused on your goals!")

        message += "\n\n💪 Remember: Progress > Perfection\n📚 One chapter at a time\n🎯 Consistency beats intensity"

        return {
            "text": message,
            "actions": ["Write down your goals", "Celebrate small wins", "Connect with study buddies"]
        }

    def _handle_exam_information(self, context: Dict, entities: Dict) -> Dict:
        """Handle exam information queries"""
        exam_name = entities.get("exam", "").lower()

        if not exam_name:
            return {
                "text": "Which exam would you like information about? I can help with JEE Main, NEET, GATE, CAT, UPSC, and many more Indian competitive exams.",
                "actions": ["Specify the exam name", "Ask about dates, syllabus, or pattern"]
            }

        # Query exam information
        exam = self.db.query(Exam).filter(Exam.name.ilike(f"%{exam_name}%")).first()

        if exam:
            dates = json.loads(exam.important_dates) if exam.important_dates else {}
            pattern = json.loads(exam.pattern) if exam.pattern else {}

            response_text = f"**{exam.name}**\n\n"
            response_text += f"**Body**: {exam.body}\n"
            response_text += f"**Type**: {exam.exam_type.title()}\n\n"

            if dates.get("exam_dates"):
                response_text += f"**Exam Dates**: {', '.join(dates['exam_dates'])}\n"

            if pattern:
                response_text += f"**Pattern**: {pattern.get('total_questions', 'N/A')} questions, {pattern.get('marks_per_question', 'N/A')} marks each\n"

            response_text += f"\nFor detailed syllabus and preparation tips, I can create a personalized study plan!"

            return {
                "text": response_text,
                "actions": ["Create study plan", "Get syllabus breakdown", "Check eligibility"]
            }
        else:
            return {
                "text": f"I don't have specific information about {exam_name}. Could you provide more details or check our supported exams: JEE, NEET, GATE, CAT, UPSC, Banking, Railways, Defense.",
                "actions": ["Try a different exam name", "Ask general questions"]
            }

    def _handle_general_query(self, context: Dict, message: str) -> Dict:
        """Handle general queries using Ollama"""
        try:
            prompt = f"""
            You are ExamSensei, an AI mentor for competitive exam preparation.

            User Context: {json.dumps(context, indent=2)}
            User Question: "{message}"

            Provide a helpful, personalized response. Keep it concise but informative.
            Focus on Indian competitive exams and practical advice.
            """

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                ollama_response = result.get("response", "").strip()
                return {
                    "text": ollama_response,
                    "actions": ["Ask follow-up questions", "Request specific study tips"]
                }
            else:
                return {
                    "text": "I'm here to help with your exam preparation! Could you be more specific about what you'd like to know?",
                    "actions": ["Ask about study planning", "Inquire about career guidance", "Get exam information"]
                }

        except Exception as e:
            print(f"Ollama query failed: {e}")
            return {
                "text": "I'm experiencing some technical difficulties, but I'm here to help! Try asking about study planning, career guidance, or specific exam information.",
                "actions": ["Rephrase your question", "Ask about specific topics"]
            }

    def _generate_topic_explanation(self, topic: str, context: Dict) -> str:
        """Generate topic explanation using Ollama"""
        try:
            prompt = f"""
            Explain the topic "{topic}" in the context of competitive exam preparation (JEE/NEET).

            User Context: Current stage - {context.get('current_stage', 'unknown')}

            Provide:
            1. Simple definition
            2. Key concepts to understand
            3. Common mistakes to avoid
            4. 2-3 practice tips

            Keep it concise and student-friendly.
            """

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", f"Here's a basic explanation of {topic}. For deeper understanding, I recommend textbook study and practice problems.")
            else:
                return f"Here's a basic overview of {topic}: It's a fundamental concept in competitive exams. Focus on understanding the core principles and practice regularly."

        except Exception as e:
            return f"Here's what you need to know about {topic}: It's an important topic for your exams. Study the fundamentals thoroughly and practice solving problems regularly."

    # Helper methods for entity extraction
    def _extract_career_entities(self, message: str) -> Dict:
        careers = ["engineering", "medical", "commerce", "science", "civil services", "defense"]
        mentioned = [c for c in careers if c in message.lower()]
        return {"careers": mentioned}

    def _extract_study_entities(self, message: str) -> Dict:
        days_match = [int(s) for s in message.split() if s.isdigit() and int(s) < 365]
        days = days_match[0] if days_match else 90
        return {"days": days}

    def _extract_topic_entities(self, message: str) -> Dict:
        topics = ["physics", "chemistry", "math", "biology", "calculus", "mechanics", "thermodynamics"]
        mentioned = [t for t in topics if t in message.lower()]
        return {"topics": mentioned}

    def _extract_exam_entities(self, message: str) -> Dict:
        exams = ["jee", "neet", "gate", "cat", "upsc", "banking", "railway"]
        mentioned = [e for e in exams if e in message.lower()]
        return {"exam": mentioned[0] if mentioned else None}
