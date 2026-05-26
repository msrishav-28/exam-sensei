"""
Tests for the pluggable LLM provider layer.

We don't make real network calls — providers are exercised via NullProvider
(which is the default when no API key is set) and via a fake provider that
records what `chat_with_tools` was called with.
"""
import asyncio
from typing import List

import pytest
from fastapi import status

from chatbot import ExamSenseiChatbot
from llm_providers import (
    LLMProvider, Message, NullProvider, ToolCall, ToolCallOrText, ToolSpec,
    _build_provider, get_provider, reset_provider,
)


class FakeProvider:
    """In-memory provider that records calls and returns scripted responses."""
    name = "fake"

    def __init__(self, scripted: List[ToolCallOrText]):
        self._scripted = list(scripted)
        self.calls: List[dict] = []

    async def chat(self, system: str, messages: List[Message]) -> str:
        self.calls.append({"mode": "chat", "system": system, "messages": messages})
        if not self._scripted:
            return "FAKE_RESPONSE"
        scripted = self._scripted.pop(0)
        return scripted.text or ""

    async def chat_with_tools(
        self, system: str, messages: List[Message], tools: List[ToolSpec]
    ) -> ToolCallOrText:
        self.calls.append({"mode": "tools", "messages": messages, "tools": tools})
        if not self._scripted:
            return ToolCallOrText(text="FAKE_FALLBACK")
        return self._scripted.pop(0)


# ---- Provider selection ---------------------------------------------------

def test_null_provider_returns_canned_text():
    """NullProvider must always be safe to await without keys."""
    p = NullProvider()
    text = asyncio.run(p.chat("system", [Message(role="user", content="hi")]))
    assert text and isinstance(text, str)


def test_build_provider_falls_back_to_null_without_keys(monkeypatch):
    """No API keys configured → NullProvider."""
    from config import settings
    monkeypatch.setattr(settings, "anthropic_api_key", "")
    monkeypatch.setattr(settings, "openai_api_key", "")
    monkeypatch.setattr(settings, "groq_api_key", "")
    monkeypatch.setattr(settings, "google_api_key", "")
    monkeypatch.setattr(settings, "llm_provider", "auto")
    reset_provider()
    assert _build_provider().name == "null"


def test_build_provider_respects_pinned_none(monkeypatch):
    """llm_provider='none' → NullProvider regardless of keys."""
    from config import settings
    monkeypatch.setattr(settings, "llm_provider", "none")
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-test")
    reset_provider()
    assert _build_provider().name == "null"


# ---- Chatbot integration with fake provider ------------------------------

@pytest.mark.asyncio
async def test_chatbot_routes_obvious_intent_to_layer1(db_session, test_user):
    """A confident 'study planning' query stays on Layer 1 — no LLM call."""
    fake = FakeProvider(scripted=[])  # if this gets called, test should fail loudly
    chatbot = ExamSenseiChatbot(db_session, provider=fake)
    result = await chatbot.process_message(
        test_user.id, "Help me plan my study schedule for the next 60 days"
    )
    assert result["intent"] == "study_planning"
    assert result["response"]
    assert fake.calls == []  # Layer 1 handled it entirely


@pytest.mark.asyncio
async def test_chatbot_routes_open_query_to_llm(db_session, test_user):
    """An open-ended question with no high-confidence intent goes to the LLM."""
    fake = FakeProvider(scripted=[ToolCallOrText(text="Here's my reasoning.")])
    chatbot = ExamSenseiChatbot(db_session, provider=fake)
    result = await chatbot.process_message(
        test_user.id, "Why does discipline matter for long-term success?"
    )
    assert result["response"] == "Here's my reasoning."
    assert len(fake.calls) == 1
    assert fake.calls[0]["mode"] == "tools"


@pytest.mark.asyncio
async def test_chatbot_resolves_tool_calls(db_session, test_user, test_exam):
    """
    First LLM turn requests a tool call → backend executes it →
    second LLM turn returns final text.
    """
    fake = FakeProvider(scripted=[
        ToolCallOrText(tool_calls=[
            ToolCall(id="c1", name="get_exam_details", arguments={"code": "jee_main_2025"})
        ]),
        ToolCallOrText(text="JEE Main is conducted by NTA."),
    ])
    chatbot = ExamSenseiChatbot(db_session, provider=fake)
    result = await chatbot.process_message(
        test_user.id, "Tell me about the upcoming science entrance"
    )
    assert result["response"] == "JEE Main is conducted by NTA."
    # Two turns: initial tool-call, then follow-up with tool result fed back
    assert len(fake.calls) == 2


@pytest.mark.asyncio
async def test_chatbot_gracefully_handles_provider_error(db_session, test_user):
    """If the LLM raises, we still return a usable response (no 500)."""
    class BrokenProvider:
        name = "broken"
        async def chat(self, *a, **kw): raise RuntimeError("upstream down")
        async def chat_with_tools(self, *a, **kw): raise RuntimeError("upstream down")
    chatbot = ExamSenseiChatbot(db_session, provider=BrokenProvider())
    result = await chatbot.process_message(test_user.id, "anything weird")
    assert result["response"]  # non-empty fallback text


# ---- End-to-end via the FastAPI client ----------------------------------

def test_chat_endpoint_uses_null_provider_by_default(client, auth_headers, test_user):
    """With no API keys set, chat must still return 200 with canned text."""
    reset_provider()  # ensure we pick the default for this process
    r = client.post(
        f"/api/v1/users/{test_user.id}/chat",
        headers=auth_headers,
        json={"message": "I need general life advice for next year"},
    )
    assert r.status_code == status.HTTP_200_OK
    payload = r.json()
    assert payload["response"]
    assert payload["provider"] in ("null", "fake")
