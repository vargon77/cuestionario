from __future__ import annotations

import hashlib
import json
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

from app.models.contracts import LLMPolicy, LLMResult, PromptEnvelope


T = TypeVar("T", bound=BaseModel)


class LLMService(Protocol):
    def generate_structured(
        self,
        prompt: PromptEnvelope,
        response_model: type[T],
        policy: LLMPolicy,
    ) -> LLMResult[T]: ...


class FakeLLMAdapter:
    def __init__(self, responses: dict[str, dict[str, Any]] | None = None) -> None:
        self.responses = responses or {}
        self.calls: list[str] = []

    def generate_structured(
        self,
        prompt: PromptEnvelope,
        response_model: type[T],
        policy: LLMPolicy,
    ) -> LLMResult[T]:
        prompt_hash = hash_prompt(prompt)
        self.calls.append(prompt_hash)
        payload = self.responses.get(prompt_hash)
        if payload is None:
            return LLMResult(error=f"no fake response for prompt {prompt_hash}")
        try:
            return LLMResult(value=response_model.model_validate(payload))
        except Exception as exc:
            if policy.max_malformed_retries > 0:
                return LLMResult(error=f"malformed fake response: {exc}")
            return LLMResult(refusal="malformed fake response")


def hash_prompt(prompt: PromptEnvelope) -> str:
    encoded = json.dumps(
        prompt.model_dump(mode="json"),
        ensure_ascii=True,
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
