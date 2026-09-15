"""Optional LLM augmentation for description normalization (offline-capable)."""
from __future__ import annotations

import os
from typing import Optional
from functools import lru_cache

# Optional imports — only loaded if LLM enabled
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from app.config import settings


class LLMNormalizer:
    """LLM-based description normalization (fallback when regex fails)."""

    def __init__(self):
        self.enabled = self._check_enabled()
        self.provider = self._determine_provider()
        self.client = None
        self._init_client()

    def _check_enabled(self) -> bool:
        return settings.LLM_ENABLED and (
            settings.LLM_API_KEY or
            os.getenv("ANTHROPIC_API_KEY") or
            os.getenv("OPENAI_API_KEY")
        )

    def _determine_provider(self) -> str:
        if settings.LLM_PROVIDER != "auto":
            return settings.LLM_PROVIDER
        if os.getenv("ANTHROPIC_API_KEY") or settings.LLM_API_KEY:
            return "anthropic"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        return "none"

    def _init_client(self):
        if self.provider == "anthropic" and HAS_ANTHROPIC:
            api_key = settings.LLM_API_KEY or os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
        elif self.provider == "openai" and HAS_OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = openai.OpenAI(api_key=api_key)

    @lru_cache(maxsize=256)
    def normalize(self, raw_description: str) -> str:
        """
        Use LLM to expand abbreviations, fix units, standardize description.
        Only called when regex-based normalization is uncertain (e.g., very short
        or garbled descriptions).
        """
        if not self.enabled or self.client is None:
            return raw_description

        prompt = f"""Normalize this industrial material description for deduplication.
Expand abbreviations (SS→Stainless Steel, MTR→Meter, DIA→Diameter, QTY→Quantity, etc.).
Normalize units to SI (mm, m, kg).
Return ONLY the normalized description, no extra text.

Input: {raw_description}
Output:"""

        try:
            if self.provider == "anthropic":
                resp = self.client.messages.create(
                    model=settings.LLM_MODEL,
                    max_tokens=100,
                    temperature=0,
                    messages=[{"role": "user", "content": prompt}],
                )
                return resp.content[0].text.strip()
            elif self.provider == "openai":
                resp = self.client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    max_tokens=100,
                    temperature=0,
                    messages=[{"role": "user", "content": prompt}],
                )
                return resp.choices[0].message.content.strip()
        except Exception:
            pass

        return raw_description


llm_normalizer = LLMNormalizer()


def get_llm_normalizer() -> LLMNormalizer:
    return llm_normalizer