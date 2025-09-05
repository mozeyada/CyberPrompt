import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from app.services.composite import normalize_rubric_scores
from app.services.fsp import granularity_matcher
from app.models import LengthBin, ScenarioType

from .prompts import get_judge_prompt

logger = logging.getLogger(__name__)


class BaseJudge(ABC):
    """Abstract base class for judges"""

    @abstractmethod
    async def evaluate(
        self,
        output: str,
        scenario: ScenarioType,
        length_bin: LengthBin,
        bias_controls: dict[str, bool],
        context: str | None = None,
    ) -> dict[str, Any]:
        """Evaluate model output and return scores"""


class LLMJudge(BaseJudge):
    """LLM-based judge using another model for evaluation"""

    def __init__(self, judge_model: str, llm_client, prompt_version: str = "v2"):
        self.judge_model = judge_model
        self.llm_client = llm_client
        self.prompt_version = prompt_version

    async def evaluate(
        self,
        output: str,
        scenario: ScenarioType,
        length_bin: LengthBin,
        bias_controls: dict[str, bool],
        context: str | None = None,
    ) -> dict[str, Any]:
        """Evaluate using LLM judge"""
        try:
            # Get base prompt
            prompt_template = get_judge_prompt(self.prompt_version)

            # Add granularity demos if enabled
            granularity_demos = ""
            if granularity_matcher.should_include_demo(length_bin, bias_controls):
                granularity_demos = granularity_matcher.get_granularity_demo(length_bin)

            # Format prompt
            focus_desc = f"Evaluating {scenario.value} response of length {length_bin.value}"
            judge_prompt = prompt_template.format(
                scenario=scenario.value,
                focus_desc=focus_desc,
                model_output=output,
                granularity_demos=granularity_demos,
            )

            # Call judge model
            response = await self.llm_client.generate(
                model=self.judge_model,
                prompt=judge_prompt,
                temperature=0.1,  # Low temperature for consistent judging
                max_tokens=500,
            )

            # Parse JSON response
            scores = self._parse_judge_response(response)

            # Normalize and validate scores
            scores = normalize_rubric_scores(scores)

            return {
                "scores": scores,
                "judge_model": self.judge_model,
                "prompt_version": self.prompt_version,
                "raw_response": response,
            }

        except Exception as e:
            logger.error(f"Error in LLM judge evaluation: {e}")
            return self._fallback_scores(str(e))

    def _parse_judge_response(self, response: str) -> dict[str, Any]:
        """Parse JSON response from judge model"""
        try:
            # Try to find JSON in response
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in judge response")
                return self._fallback_scores("No JSON found")

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return self._fallback_scores(f"JSON parse error: {e}")

    def _fallback_scores(self, error: str) -> dict[str, Any]:
        """Return fallback scores when judge fails"""
        return {
            "scores": {
                "technical_accuracy": 0,
                "actionability": 0,
                "completeness": 0,
                "compliance_alignment": 0,
                "risk_awareness": 0,
                "relevance": 0,
                "clarity": 0,
                "composite": 0.0,
            },
            "judge_model": self.judge_model,
            "prompt_version": self.prompt_version,
            "error": error,
        }


class HumanJudge(BaseJudge):
    """Human judge - scores provided externally"""

    async def evaluate(
        self,
        output: str,
        scenario: ScenarioType,
        length_bin: LengthBin,
        bias_controls: dict[str, bool],
        context: str | None = None,
    ) -> dict[str, Any]:
        """Human evaluation - requires external input"""
        return {
            "scores": None,  # To be filled by human auditor
            "judge_type": "human",
            "requires_human_input": True,
        }


def create_judge(judge_config: dict[str, Any], llm_client=None) -> BaseJudge:
    """Factory function to create appropriate judge"""
    judge_type = judge_config.get("type", "llm")

    if judge_type == "llm":
        judge_model = judge_config.get("judge_model", "gpt-4o-mini")
        prompt_version = judge_config.get("prompt_ver", "v2")
        return LLMJudge(judge_model, llm_client, prompt_version)
    elif judge_type == "human":
        return HumanJudge()
    else:
        msg = f"Unknown judge type: {judge_type}"
        raise ValueError(msg)
