"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

import os
from openai import OpenAI
from multi_agent_research_lab.core.errors import StudentTodoError

@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


from multi_agent_research_lab.core.config import get_settings

class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = model

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        msg = response.choices[0].message.content or ""
        usage = response.usage
        return LLMResponse(
            content=msg,
            input_tokens=usage.prompt_tokens if usage else None,
            output_tokens=usage.completion_tokens if usage else None,
            cost_usd=None,
        )
