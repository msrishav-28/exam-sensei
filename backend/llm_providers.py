"""
Pluggable LLM providers.

Production default: Gemini 2.5 Flash (free tier — 10 RPM, 250 RPD).
Optional fallbacks: Groq (free, fast), OpenAI, Anthropic (both paid).
If no API key is configured, NullProvider returns canned text so the chat
endpoint always responds without 500-ing.

All providers expose the same two methods so callers don't care which is
behind them:

    async chat(system, messages) -> str
    async chat_with_tools(system, messages, tools) -> ToolCallOrText

Each implementation is a thin wrapper around the vendor SDK; there's no
provider-specific business logic outside this module.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Union

from config import settings
from logger import logger


# ---------------------------------------------------------------------------
# Wire types
# ---------------------------------------------------------------------------

@dataclass
class Message:
    role: str       # "system" | "user" | "assistant" | "tool"
    content: str
    tool_call_id: Optional[str] = None   # for role="tool" replies
    name: Optional[str] = None           # for role="tool" replies


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=lambda: {"type": "object", "properties": {}})


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolCallOrText:
    """The LLM either calls one or more tools, or returns plain text."""
    text: Optional[str] = None
    tool_calls: List[ToolCall] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Provider protocol
# ---------------------------------------------------------------------------

class LLMProvider(Protocol):
    name: str

    async def chat(self, system: str, messages: List[Message]) -> str: ...
    async def chat_with_tools(
        self, system: str, messages: List[Message], tools: List[ToolSpec]
    ) -> ToolCallOrText: ...


# ---------------------------------------------------------------------------
# NullProvider — always-available canned response
# ---------------------------------------------------------------------------

class NullProvider:
    """Used when no API key is configured. Returns honest canned text."""

    name = "null"

    _FALLBACK = (
        "I can answer based on your profile and exam data, but the deeper "
        "free-form mode isn't configured yet. Try asking about a specific "
        "exam, your study plan, or which topics to prioritize."
    )

    async def chat(self, system: str, messages: List[Message]) -> str:
        return self._FALLBACK

    async def chat_with_tools(
        self, system: str, messages: List[Message], tools: List[ToolSpec]
    ) -> ToolCallOrText:
        return ToolCallOrText(text=self._FALLBACK)


# ---------------------------------------------------------------------------
# GeminiProvider (free tier default)
# ---------------------------------------------------------------------------

class GeminiProvider:
    name = "gemini"
    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(self, api_key: str, model: Optional[str] = None):
        # Imported lazily so the package isn't required if the user never
        # configures GOOGLE_API_KEY.
        from google import genai
        self._client = genai.Client(api_key=api_key)
        self._model = model or self.DEFAULT_MODEL

    @staticmethod
    def _convert_messages(system: str, messages: List[Message]) -> List[Dict]:
        """Gemini uses {role: user|model, parts: [{text}]} contents."""
        contents: List[Dict] = []
        if system:
            contents.append({"role": "user", "parts": [{"text": f"[System]\n{system}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        for m in messages:
            role = "model" if m.role == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m.content}]})
        return contents

    async def chat(self, system: str, messages: List[Message]) -> str:
        contents = self._convert_messages(system, messages)
        resp = await self._client.aio.models.generate_content(
            model=self._model,
            contents=contents,
        )
        return (resp.text or "").strip()

    async def chat_with_tools(
        self, system: str, messages: List[Message], tools: List[ToolSpec]
    ) -> ToolCallOrText:
        from google.genai import types as gtypes

        contents = self._convert_messages(system, messages)
        gemini_tools = [
            gtypes.Tool(function_declarations=[
                gtypes.FunctionDeclaration(
                    name=t.name,
                    description=t.description,
                    parameters=t.parameters,
                )
                for t in tools
            ])
        ]
        resp = await self._client.aio.models.generate_content(
            model=self._model,
            contents=contents,
            config=gtypes.GenerateContentConfig(tools=gemini_tools),
        )

        # Gemini returns function calls in response.candidates[0].content.parts
        tool_calls: List[ToolCall] = []
        try:
            for part in resp.candidates[0].content.parts:
                fc = getattr(part, "function_call", None)
                if fc and fc.name:
                    tool_calls.append(ToolCall(
                        id=f"call_{len(tool_calls)}",
                        name=fc.name,
                        arguments=dict(fc.args or {}),
                    ))
        except (AttributeError, IndexError):
            pass

        return ToolCallOrText(text=(resp.text or "").strip() or None, tool_calls=tool_calls)


# ---------------------------------------------------------------------------
# GroqProvider (free tier fallback)
# ---------------------------------------------------------------------------

class GroqProvider:
    name = "groq"
    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    def __init__(self, api_key: str, model: Optional[str] = None):
        from groq import AsyncGroq
        self._client = AsyncGroq(api_key=api_key)
        self._model = model or self.DEFAULT_MODEL

    @staticmethod
    def _convert_messages(system: str, messages: List[Message]) -> List[Dict]:
        out: List[Dict] = []
        if system:
            out.append({"role": "system", "content": system})
        for m in messages:
            out.append({"role": m.role, "content": m.content})
        return out

    async def chat(self, system: str, messages: List[Message]) -> str:
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=self._convert_messages(system, messages),
        )
        return (resp.choices[0].message.content or "").strip()

    async def chat_with_tools(
        self, system: str, messages: List[Message], tools: List[ToolSpec]
    ) -> ToolCallOrText:
        openai_tools = [{
            "type": "function",
            "function": {"name": t.name, "description": t.description, "parameters": t.parameters},
        } for t in tools]
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=self._convert_messages(system, messages),
            tools=openai_tools,
        )
        msg = resp.choices[0].message
        tool_calls: List[ToolCall] = []
        for tc in (msg.tool_calls or []):
            try:
                args = json.loads(tc.function.arguments or "{}")
            except (ValueError, TypeError):
                args = {}
            tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args))
        return ToolCallOrText(text=(msg.content or "").strip() or None, tool_calls=tool_calls)


# ---------------------------------------------------------------------------
# OpenAIProvider (paid; same wire format as Groq)
# ---------------------------------------------------------------------------

class OpenAIProvider:
    name = "openai"
    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, api_key: str, model: Optional[str] = None):
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model or self.DEFAULT_MODEL

    @staticmethod
    def _convert_messages(system: str, messages: List[Message]) -> List[Dict]:
        out: List[Dict] = []
        if system:
            out.append({"role": "system", "content": system})
        for m in messages:
            out.append({"role": m.role, "content": m.content})
        return out

    async def chat(self, system: str, messages: List[Message]) -> str:
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=self._convert_messages(system, messages),
        )
        return (resp.choices[0].message.content or "").strip()

    async def chat_with_tools(
        self, system: str, messages: List[Message], tools: List[ToolSpec]
    ) -> ToolCallOrText:
        openai_tools = [{
            "type": "function",
            "function": {"name": t.name, "description": t.description, "parameters": t.parameters},
        } for t in tools]
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=self._convert_messages(system, messages),
            tools=openai_tools,
        )
        msg = resp.choices[0].message
        tool_calls: List[ToolCall] = []
        for tc in (msg.tool_calls or []):
            try:
                args = json.loads(tc.function.arguments or "{}")
            except (ValueError, TypeError):
                args = {}
            tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args))
        return ToolCallOrText(text=(msg.content or "").strip() or None, tool_calls=tool_calls)


# ---------------------------------------------------------------------------
# AnthropicProvider (paid)
# ---------------------------------------------------------------------------

class AnthropicProvider:
    name = "anthropic"
    DEFAULT_MODEL = "claude-3-5-haiku-latest"

    def __init__(self, api_key: str, model: Optional[str] = None):
        from anthropic import AsyncAnthropic
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model or self.DEFAULT_MODEL

    @staticmethod
    def _convert_messages(messages: List[Message]) -> List[Dict]:
        out: List[Dict] = []
        for m in messages:
            role = "assistant" if m.role == "assistant" else "user"
            out.append({"role": role, "content": m.content})
        return out

    async def chat(self, system: str, messages: List[Message]) -> str:
        resp = await self._client.messages.create(
            model=self._model,
            system=system or "",
            messages=self._convert_messages(messages),
            max_tokens=1024,
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()

    async def chat_with_tools(
        self, system: str, messages: List[Message], tools: List[ToolSpec]
    ) -> ToolCallOrText:
        anthropic_tools = [{
            "name": t.name,
            "description": t.description,
            "input_schema": t.parameters,
        } for t in tools]
        resp = await self._client.messages.create(
            model=self._model,
            system=system or "",
            messages=self._convert_messages(messages),
            tools=anthropic_tools,
            max_tokens=1024,
        )
        tool_calls: List[ToolCall] = []
        text_parts: List[str] = []
        for block in resp.content:
            btype = getattr(block, "type", None)
            if btype == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=dict(block.input or {}),
                ))
            elif btype == "text":
                text_parts.append(block.text)
        text = "".join(text_parts).strip() or None
        return ToolCallOrText(text=text, tool_calls=tool_calls)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_PROVIDER_CACHE: Optional[LLMProvider] = None


def _build_provider() -> LLMProvider:
    """Pick a provider based on settings.llm_provider + which API keys are set."""
    pinned = (settings.llm_provider or "auto").lower()

    def try_anthropic() -> Optional[LLMProvider]:
        if settings.anthropic_api_key:
            try:
                return AnthropicProvider(settings.anthropic_api_key)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Anthropic provider init failed: {e}")
        return None

    def try_openai() -> Optional[LLMProvider]:
        if settings.openai_api_key:
            try:
                return OpenAIProvider(settings.openai_api_key)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"OpenAI provider init failed: {e}")
        return None

    def try_groq() -> Optional[LLMProvider]:
        if settings.groq_api_key:
            try:
                return GroqProvider(settings.groq_api_key)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Groq provider init failed: {e}")
        return None

    def try_gemini() -> Optional[LLMProvider]:
        if settings.google_api_key:
            try:
                return GeminiProvider(settings.google_api_key)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Gemini provider init failed: {e}")
        return None

    if pinned == "none":
        return NullProvider()
    if pinned == "anthropic":
        return try_anthropic() or NullProvider()
    if pinned == "openai":
        return try_openai() or NullProvider()
    if pinned == "groq":
        return try_groq() or NullProvider()
    if pinned == "gemini":
        return try_gemini() or NullProvider()

    # "auto" priority: anthropic > openai > groq > gemini > null
    for factory in (try_anthropic, try_openai, try_groq, try_gemini):
        provider = factory()
        if provider is not None:
            return provider
    return NullProvider()


def get_provider() -> LLMProvider:
    """Return the cached provider. Cache survives the process lifetime."""
    global _PROVIDER_CACHE
    if _PROVIDER_CACHE is None:
        _PROVIDER_CACHE = _build_provider()
        logger.info(f"LLM provider active: {_PROVIDER_CACHE.name}")
    return _PROVIDER_CACHE


def reset_provider() -> None:
    """Clear the cache. Tests use this to swap providers between cases."""
    global _PROVIDER_CACHE
    _PROVIDER_CACHE = None
