import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from app.services.composite import normalize_rubric_scores
from app.services.fsp import granularity_matcher, fsp_processor
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
        """Evaluate using LLM judge with FSP support"""
        try:
            # Check if FSP should be used
            use_fsp = bias_controls.get("fsp", False) and fsp_processor.should_use_fsp(output, length_bin)
            
            if use_fsp:
                # FSP: Evaluate segments and aggregate
                return await self._evaluate_with_fsp(output, scenario, length_bin, bias_controls, context)
            else:
                # Standard: Evaluate full response
                return await self._evaluate_standard(output, scenario, length_bin, bias_controls, context)
                
        except Exception as e:
            logger.error(f"Error in LLM judge evaluation: {e}")
            return self._fallback_scores(str(e))
    
    async def _evaluate_standard(
        self,
        output: str,
        scenario: ScenarioType,
        length_bin: LengthBin,
        bias_controls: dict[str, bool],
        context: str | None = None,
    ) -> dict[str, Any]:
        """Standard evaluation without FSP"""
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
            temperature=0.1,
        )

        # Parse and normalize scores
        scores = self._parse_judge_response(response)
        scores = normalize_rubric_scores(scores)

        return {
            "scores": scores,
            "judge_model": self.judge_model,
            "prompt_version": self.prompt_version,
            "fsp_used": False,
            "raw_response": response,
        }
    
    async def _evaluate_with_fsp(
        self,
        output: str,
        scenario: ScenarioType,
        length_bin: LengthBin,
        bias_controls: dict[str, bool],
        context: str | None = None,
    ) -> dict[str, Any]:
        """FSP evaluation: Focus Sentence Prompting - evaluate one sentence at a time with full context"""
        # Split into sentences (not arbitrary segments)
        sentences = fsp_processor.split_into_sentences(output)
        sentence_scores = []
        
        prompt_template = get_judge_prompt(self.prompt_version)
        
        for sentence in sentences:
            # FSP: Evaluate one sentence at a time while providing full document context
            # This is the key insight from the paper - maintain context but focus evaluation
            fsp_prompt = fsp_processor.create_fsp_prompt(
                scenario.value,
                output,  # Full document context
                sentence["text"],  # Focus sentence
                context or ""  # Original prompt context if available
            )
            
            judge_prompt = prompt_template.format(
                scenario=scenario.value,
                focus_desc="Focus Sentence Prompting: Evaluate the target sentence within full document context",
                model_output=fsp_prompt,
                granularity_demos="",
            )
            
            # Evaluate focused sentence
            response = await self.llm_client.generate(
                model=self.judge_model,
                prompt=judge_prompt,
                temperature=0.1,
            )
            
            sentence_score = self._parse_judge_response(response)
            sentence_score["sentence_text"] = sentence["text"]
            sentence_score["raw_response"] = response
            sentence_scores.append(sentence_score)
        
        # Aggregate sentence-level scores to document level
        aggregated_scores = fsp_processor.aggregate_sentence_scores(sentence_scores)
        aggregated_scores = normalize_rubric_scores(aggregated_scores)
        
        return {
            "scores": aggregated_scores,
            "judge_model": self.judge_model,
            "prompt_version": self.prompt_version,
            "fsp_used": True,
            "sentences_evaluated": len(sentences),
            "raw_responses": [s.get("raw_response", "") for s in sentence_scores],
        }

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
