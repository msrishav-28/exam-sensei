"""
ExamSenseiChatbot — hybrid intent + LLM mentor.

Routing:
  Layer 1: pattern-matched intents (career_guidance, study_planning,
           performance_analysis, motivational_support, exam_information).
           Free, instant, deterministic. Handles the obvious cases.
  Layer 2: LLM with tool calling. Used when intent confidence is low or
           when the regex doesn't match. The model can call
           `get_user_profile`, `get_exam_details`, `generate_study_plan`
           to fetch fresh data — we don't dump everything into the prompt.

The active LLM provider is picked by `llm_providers.get_provider()` based on
which API keys are configured (priority: Anthropic > OpenAI > Groq > Gemini >
Null). With no keys set, NullProvider returns canned text and the endpoint
still returns 200.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ai_models import AdaptiveMentor, TopicPrioritizer, _coerce_json
from chatbot_tools import TOOL_SPECS, execute_tool
from llm_providers import LLMProvider, Message, ToolCallOrText, get_provider
from logger import logger
from models import Conversation, Exam, User


_SYSTEM_PROMPT = (
    "You are ExamSensei, an intelligent AI mentor for Indian competitive "
    "exam preparation (JEE, NEET, GATE, UPSC, CAT, etc.). "
    "Be encouraging, give specific actionable advice, and consider the user's "
    "lifecycle stage. Use the provided tools to fetch the user's profile, "
    "exam details, or generate a study plan — do not invent specifics you "
    "don't have. Keep responses concise and student-friendly."
)


# Intents handled deterministically by Layer 1 — confident enough that we
# don't need an LLM round trip.
_LAYER1_INTENTS = {
    "career_guidance",
    "study_planning",
    "performance_analysis",
    "motivational_support",
    "exam_information",
}

# Confidence cutoff: below this we defer to the LLM regardless of intent.
_LAYER1_CONFIDENCE_THRESHOLD = 0.85


class ExamSenseiChatbot:
    """Async conversational mentor backed by a pluggable LLM provider."""

    def __init__(self, db: Session, provider: Optional[LLMProvider] = None):
        self.db = db
        self.provider = provider or get_provider()
        self.mentor = AdaptiveMentor(db)
        self.topic_prioritizer = TopicPrioritizer(db)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    async def process_message(
        self, user_id: UUID, message: str, session_id: Optional[str] = None
    ) -> Dict:
        if not session_id:
            session_id = f"session_{user_id}_{datetime.utcnow().timestamp()}"

        user_context = self._get_user_context(user_id)
        intent_analysis = self._analyze_intent(message)
        response = await self._route(intent_analysis, user_context, user_id, message)

        # Persist a minimal slice of context so rows don't snowball.
        persisted_context = {
            k: user_context.get(k)
            for k in ("current_stage", "career_paths", "active_exams", "education_level")
        }
        self.db.add(Conversation(
            user_id=user_id,
            session_id=session_id,
            message=message,
            response=response["text"],
            intent=intent_analysis["intent"],
            context=persisted_context,
            timestamp=datetime.utcnow(),
        ))
        self.db.commit()

        return {
            "response": response["text"],
            "intent": intent_analysis["intent"],
            "confidence": intent_analysis["confidence"],
            "suggested_actions": response.get("actions", []),
            "session_id": session_id,
            "provider": self.provider.name,
        }

    # ------------------------------------------------------------------
    # Context loading
    # ------------------------------------------------------------------

    def _get_user_context(self, user_id: UUID) -> Dict:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}

        recent = (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.timestamp.desc())
            .limit(5)
            .all()
        )
        return {
            "user_id": str(user_id),
            "current_stage": user.current_stage,
            "career_paths": user.career_paths or [],
            "active_exams": user.active_exams or [],
            "preparation_profile": _coerce_json(user.preparation_profile, {}),
            "education_level": user.education_level,
            "state": user.state,
            "category": user.category,
            "budget": user.budget,
            "recent_conversations": [
                {"message": c.message, "intent": c.intent,
                 "timestamp": c.timestamp.isoformat()}
                for c in recent
            ],
        }

    # ------------------------------------------------------------------
    # Layer 1: regex intent classifier
    # ------------------------------------------------------------------

    def _analyze_intent(self, message: str) -> Dict:
        m = message.lower()
        if any(w in m for w in ("career", "future", "become", "job", "profession")):
            return {"intent": "career_guidance", "confidence": 0.9,
                    "entities": self._extract_career_entities(message)}
        if any(w in m for w in ("study", "prepare", "plan", "schedule", "timetable")):
            return {"intent": "study_planning", "confidence": 0.9,
                    "entities": self._extract_study_entities(message)}
        if any(w in m for w in ("explain", "understand", "help with", "confused about")):
            # Topic explanation is open-ended — defer to LLM.
            return {"intent": "topic_explanation", "confidence": 0.6,
                    "entities": self._extract_topic_entities(message)}
        if any(w in m for w in ("score", "performance", "weak", "strong", "improve")):
            return {"intent": "performance_analysis", "confidence": 0.85, "entities": {}}
        if any(w in m for w in ("motivate", "tired", "stressed", "difficult", "can't")):
            return {"intent": "motivational_support", "confidence": 0.9, "entities": {}}
        if any(w in m for w in ("exam", "jee", "neet", "gate", "dates", "syllabus", "pattern")):
            return {"intent": "exam_information", "confidence": 0.85,
                    "entities": self._extract_exam_entities(message)}
        return {"intent": "general_query", "confidence": 0.3, "entities": {}}

    # ------------------------------------------------------------------
    # Routing decision
    # ------------------------------------------------------------------

    async def _route(self, intent_analysis: Dict, context: Dict,
                     user_id: UUID, message: str) -> Dict:
        intent = intent_analysis["intent"]
        confidence = intent_analysis.get("confidence", 0.0)
        entities = intent_analysis.get("entities", {})

        # Layer 1: confident regex match for a supported intent → handle locally.
        if intent in _LAYER1_INTENTS and confidence >= _LAYER1_CONFIDENCE_THRESHOLD:
            return self._handle_layer1(intent, context, entities, message)

        # Layer 2: anything else → LLM with tool calling.
        return await self._handle_with_llm(user_id, context, message)

    # ------------------------------------------------------------------
    # Layer 1 handlers (unchanged behavior from previous pass)
    # ------------------------------------------------------------------

    def _handle_layer1(self, intent: str, context: Dict, entities: Dict, message: str) -> Dict:
        if intent == "career_guidance":
            return self._handle_career_guidance(context, entities)
        if intent == "study_planning":
            return self._handle_study_planning(context, entities)
        if intent == "performance_analysis":
            return self._handle_performance_analysis(context)
        if intent == "motivational_support":
            return self._handle_motivational_support(context)
        if intent == "exam_information":
            return self._handle_exam_information(context, entities)
        # Unreachable given _LAYER1_INTENTS membership, but be defensive.
        return {"text": "How can I help with your exam prep?", "actions": []}

    def _handle_career_guidance(self, context: Dict, entities: Dict) -> Dict:
        career_paths = context.get("career_paths", []) or []
        if not career_paths:
            return {
                "text": "I'd love to help with career guidance! What subjects are you interested in? "
                        "For example: engineering, medical, commerce, science research, or civil services?",
                "actions": ["Share your interests", "Tell me about your strengths"],
            }
        try:
            recs = self.mentor.get_personalized_recommendations(UUID(context["user_id"]))
        except Exception:  # noqa: BLE001
            recs = {"recommendations": [], "next_actions": []}

        text = (
            f"Based on your current stage ({context.get('current_stage', '?')}) "
            f"and interests in {', '.join(career_paths)}, here's my recommendation:\n\n"
        )
        rec_items = recs.get("recommendations", [])
        if rec_items:
            top = rec_items[0]
            text += f"**Primary suggestion**: {top.get('exam') or top.get('type')}\n"
            text += f"- Reasoning: {top.get('reasoning', '')}\n"
        text += "\nConsistency beats intensity — work the highest-impact area first."
        return {"text": text, "actions": recs.get("next_actions", [])}

    def _handle_study_planning(self, context: Dict, entities: Dict) -> Dict:
        active_exams = context.get("active_exams", []) or []
        if not active_exams:
            return {
                "text": "I'd be happy to help you create a study plan! "
                        "Which exam are you preparing for? JEE Main, NEET, GATE, or something else?",
                "actions": ["Tell me your target exam", "Share how many hours you study daily"],
            }
        exam_code = active_exams[0]
        days_available = entities.get("days", 90)
        try:
            plan = self.topic_prioritizer.generate_study_plan(
                UUID(context["user_id"]), exam_code, days_available
            )
        except Exception:  # noqa: BLE001
            return {
                "text": "I had trouble building your study plan. Try specifying the exam code "
                        "(e.g. 'jee_main_2025') and how many days you have.",
                "actions": ["Specify the exam", "Tell me your timeline"],
            }
        if "error" in plan:
            return {"text": plan["error"], "actions": ["Specify a valid exam code"]}
        text = f"Here's your personalized {days_available}-day study plan for {exam_code.upper()}:\n\n"
        for i, t in enumerate(plan.get("prioritized_topics", [])[:3], 1):
            text += f"{i}. **{t['name'].title()}** (Weightage: {t['weightage']}%, Difficulty: {t['difficulty']})\n"
        text += f"\nEstimated success probability: {plan.get('success_probability', 0) * 100:.0f}%\n\n"
        text += "Focus on weak areas first; keep strengths warm with weekly mock tests."
        return {
            "text": text,
            "actions": ["Start with the top priority", "Set daily study goals", "Take weekly mocks"],
        }

    def _handle_performance_analysis(self, context: Dict) -> Dict:
        profile = context.get("preparation_profile", {}) or {}
        text = "Let's analyze your current performance:\n\n"
        strengths = profile.get("strengths", [])
        weaknesses = profile.get("weaknesses", [])
        if strengths:
            text += f"**Strengths**: {', '.join(strengths)}\n"
        if weaknesses:
            text += f"**Areas to improve**: {', '.join(weaknesses)}\n"
        text += f"**Daily study hours**: {profile.get('study_hours_per_day', 0)}\n\n"
        if weaknesses:
            text += ("Focus on your weak areas — that's your biggest score-improvement lever.\n"
                     "Spend ~60% on weaknesses, ~40% maintaining strengths.")
        return {
            "text": text,
            "actions": ["Take a diagnostic test", "Focus on weak topics", "Track daily progress"],
        }

    def _handle_motivational_support(self, context: Dict) -> Dict:
        stage = context.get("current_stage", "")
        messages = {
            "class_12_completed": (
                "Congratulations on finishing Class 12! This is a crucial turning point. "
                "Your JEE/NEET preparation will shape your future. Stay consistent — daily effort beats motivation bursts."
            ),
            "entrance_exams_preparing": (
                "Exam prep is a marathon. Every day you study brings you closer to your goal. Remember why you started."
            ),
            "undergraduate_started": (
                "College life + competitive exams is hard, but you're building real skills. "
                "Your future self will thank you for this discipline."
            ),
        }
        text = messages.get(stage, (
            "You're capable of amazing things. Every expert was once a beginner. "
            "Your consistent effort will compound into success."
        ))
        text += "\n\nProgress > perfection. One chapter at a time. Consistency beats intensity."
        return {
            "text": text,
            "actions": ["Write down your goals", "Celebrate small wins", "Connect with study buddies"],
        }

    def _handle_exam_information(self, context: Dict, entities: Dict) -> Dict:
        exam_name = entities.get("exam") or ""
        if isinstance(exam_name, list):
            exam_name = exam_name[0] if exam_name else ""
        exam_name = (exam_name or "").lower()
        if not exam_name:
            return {
                "text": "Which exam would you like information about? "
                        "I cover JEE, NEET, GATE, CAT, UPSC, banking, railways, and more.",
                "actions": ["Specify the exam name"],
            }
        exam = self.db.query(Exam).filter(Exam.name.ilike(f"%{exam_name}%")).first()
        if not exam:
            return {
                "text": f"I don't have specific information about {exam_name} yet. "
                        "Try JEE, NEET, GATE, CAT, or UPSC.",
                "actions": ["Try a different exam name"],
            }
        dates = _coerce_json(exam.important_dates, {}) or {}
        pattern = _coerce_json(exam.pattern, {}) or {}
        text = f"**{exam.name}**\n\n**Body**: {exam.body}\n**Type**: {exam.exam_type.title()}\n\n"
        if isinstance(dates, dict) and dates.get("exam_dates"):
            text += f"**Exam Dates**: {', '.join(dates['exam_dates'])}\n"
        if isinstance(pattern, dict) and pattern:
            text += (f"**Pattern**: {pattern.get('total_questions', 'N/A')} questions, "
                     f"{pattern.get('marks_per_question', 'N/A')} marks each\n")
        text += "\nWant a study plan? Just ask."
        return {
            "text": text,
            "actions": ["Create study plan", "Check eligibility", "Get syllabus breakdown"],
        }

    # ------------------------------------------------------------------
    # Layer 2: LLM with tool calling
    # ------------------------------------------------------------------

    async def _handle_with_llm(self, user_id: UUID, context: Dict, message: str) -> Dict:
        """LLM picks the response — possibly via tool calls — for open-ended queries."""
        # Build the conversation: system prompt + brief context summary + the
        # user's message. We deliberately don't dump the full profile; the
        # LLM can call get_user_profile if it needs to.
        primer = (
            f"User is at lifecycle stage: {context.get('current_stage', '?')}. "
            f"Career interests: {context.get('career_paths') or 'unset'}. "
            f"Active exams: {context.get('active_exams') or 'unset'}."
        )
        messages: List[Message] = [
            Message(role="user", content=f"[Context] {primer}"),
            Message(role="assistant", content="Got it. What's your question?"),
            Message(role="user", content=message),
        ]

        try:
            result = await self.provider.chat_with_tools(_SYSTEM_PROMPT, messages, TOOL_SPECS)
            text = await self._resolve_tool_calls(user_id, messages, result, max_turns=3)
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"LLM provider {self.provider.name} failed: {exc}")
            text = ("I'm here to help with your exam prep. Try asking about a specific "
                    "exam (e.g. 'tell me about JEE Main 2025'), study planning, or career "
                    "guidance.")

        return {
            "text": text or "I couldn't generate a response right now. Could you rephrase?",
            "actions": ["Ask a follow-up", "Request a study plan", "Get exam information"],
        }

    async def _resolve_tool_calls(
        self,
        user_id: UUID,
        messages: List[Message],
        result: ToolCallOrText,
        *,
        max_turns: int,
    ) -> str:
        """Run any requested tool calls, feed results back, repeat until text."""
        turns_left = max_turns
        while result.tool_calls and turns_left > 0:
            turns_left -= 1
            # Record the model's tool-call decision as an assistant message so
            # the next turn sees consistent history.
            messages.append(Message(
                role="assistant",
                content=json.dumps([{"name": tc.name, "arguments": tc.arguments}
                                    for tc in result.tool_calls]),
            ))
            for tc in result.tool_calls:
                tool_output = execute_tool(tc.name, self.db, user_id, tc.arguments)
                messages.append(Message(
                    role="tool",
                    content=tool_output,
                    tool_call_id=tc.id,
                    name=tc.name,
                ))
            try:
                result = await self.provider.chat_with_tools(
                    _SYSTEM_PROMPT, messages, TOOL_SPECS
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"LLM tool follow-up failed: {exc}")
                break
        return (result.text or "").strip()

    # ------------------------------------------------------------------
    # Entity extraction helpers
    # ------------------------------------------------------------------

    def _extract_career_entities(self, message: str) -> Dict:
        careers = ("engineering", "medical", "commerce", "science", "civil services", "defense")
        return {"careers": [c for c in careers if c in message.lower()]}

    def _extract_study_entities(self, message: str) -> Dict:
        nums = [int(s) for s in message.split() if s.isdigit() and int(s) < 365]
        return {"days": nums[0] if nums else 90}

    def _extract_topic_entities(self, message: str) -> Dict:
        topics = ("physics", "chemistry", "math", "biology", "calculus", "mechanics", "thermodynamics")
        return {"topics": [t for t in topics if t in message.lower()]}

    def _extract_exam_entities(self, message: str) -> Dict:
        exams = ("jee", "neet", "gate", "cat", "upsc", "banking", "railway")
        mentioned = [e for e in exams if e in message.lower()]
        return {"exam": mentioned[0] if mentioned else None}
