"""Groq API client for adaptive prompt generation."""

import logging
from typing import Any, Dict

import httpx

from app.services.llm_client import BaseLLMClient

logger = logging.getLogger(__name__)


class GroqClient(BaseLLMClient):
    """Groq API client for fast, cost-effective LLM inference."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self._last_usage = {}
        
    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
        seed: int | None = None,
        **kwargs
    ) -> str:
        """Generate text using Groq API."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if seed is not None:
            payload["seed"] = seed
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Store usage information for token counting
                if "usage" in data:
                    self._last_usage = data["usage"]
                
                return data["choices"][0]["message"]["content"]
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
                logger.error(f"Groq API HTTP error {e.response.status_code}: {error_detail}")
                raise Exception(f"Groq API error {e.response.status_code}: {error_detail}")
            except Exception as e:
                logger.error(f"Groq API error: {e}")
                raise

    def get_token_counts(self, prompt: str, response: str, model: str) -> tuple[int, int]:
        """Get token counts from last API call or estimate"""
        if self._last_usage:
            return self._last_usage.get("prompt_tokens", 0), self._last_usage.get("completion_tokens", 0)
        
        # Fallback to estimation
        from app.utils.token_meter import token_meter
        input_tokens = token_meter.count_tokens(prompt, model)
        output_tokens = token_meter.count_tokens(response, model)
        return input_tokens, output_tokens


# Current supported Groq models
GROQ_MODELS = {
    "llama-3.3-70b": "llama-3.3-70b-versatile"  # Only confirmed working model
}