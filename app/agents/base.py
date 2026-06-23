"""Shared base class and OpenAI client factory for all agents."""

import os
import json
import re
from typing import Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-4o"
MAX_TOKENS = 4096


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. Add it to your .env file."
        )
    return OpenAI(api_key=api_key)


def extract_json(text: str) -> Any:
    """
    Extract the first valid JSON object or array from an LLM response string.
    Handles markdown code fences (```json ... ```) gracefully.
    """
    # Strip markdown fences
    text = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find first { or [ and attempt to parse from there
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError(f"No valid JSON found in response:\n{text[:500]}")


class BaseAgent:
    """Thin wrapper around the OpenAI API with prompt/response helpers."""

    def __init__(self):
        self.client = get_client()
        self.model = MODEL

    def _call(self, system: str, user: str, max_tokens: int = MAX_TOKENS) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        return response.choices[0].message.content

    def _call_with_history(
        self,
        system: str,
        messages: list[dict],
        max_tokens: int = MAX_TOKENS,
    ) -> str:
        full_messages = [{"role": "system", "content": system}] + messages
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=full_messages,
        )
        return response.choices[0].message.content
