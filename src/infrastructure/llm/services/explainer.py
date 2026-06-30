from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import structlog
from langchain_ollama import ChatOllama
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger(__name__)

_PROMPT_DIR = Path(__file__).parent.parent / "prompts"


class PromptLoader:

    _cache: dict[str, tuple[str, str]] = {}

    @classmethod
    def load(cls, name: str) -> tuple[str, str]:
        if name in cls._cache:
            return cls._cache[name]
        path = _PROMPT_DIR / name
        text = path.read_text(encoding="utf-8")
        digest = hashlib.sha256(text.encode()).hexdigest()
        cls._cache[name] = (text, digest)
        return text, digest


class LLMExplainerService:

    def __init__(self, *, base_url: str, model: str) -> None:
        self._llm = ChatOllama(base_url=base_url, model=model, temperature=0.1)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def explain_risk(self, context: dict[str, Any]) -> dict[str, Any]:
        prompt_text, prompt_hash = PromptLoader.load("activity_risk_explainer_prompt.md")
        filled = prompt_text.format(**context)
        response = await self._llm.ainvoke(filled)
        logger.info(
            "llm_explain_risk",
            prompt_hash=prompt_hash,
            model=self._llm.model,
            tokens=len(str(response.content)),
        )
        return {"explanation": str(response.content), "prompt_hash": prompt_hash}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def draft_dsr_response(self, context: dict[str, Any]) -> dict[str, Any]:
        prompt_text, prompt_hash = PromptLoader.load("dsr_response_draft_prompt.md")
        filled = prompt_text.format(**context)
        response = await self._llm.ainvoke(filled)
        logger.info("llm_draft_dsr", prompt_hash=prompt_hash)
        return {
            "draft": str(response.content),
            "prompt_hash": prompt_hash,
            "requires_human_review": True,
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def summarize_processor_review(self, context: dict[str, Any]) -> dict[str, Any]:
        prompt_text, prompt_hash = PromptLoader.load("processor_review_summary_prompt.md")
        filled = prompt_text.format(**context)
        response = await self._llm.ainvoke(filled)
        logger.info("llm_processor_summary", prompt_hash=prompt_hash)
        return {"summary": str(response.content), "prompt_hash": prompt_hash}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def suggest_incident_remediation(self, context: dict[str, Any]) -> dict[str, Any]:
        prompt_text, prompt_hash = PromptLoader.load("incident_remediation_prompt.md")
        filled = prompt_text.format(**context)
        response = await self._llm.ainvoke(filled)
        logger.info("llm_incident_remediation", prompt_hash=prompt_hash)
        return {
            "suggestion": str(response.content),
            "prompt_hash": prompt_hash,
            "requires_human_review": True,
        }
