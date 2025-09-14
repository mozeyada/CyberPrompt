"""Groq API client for adaptive prompt generation."""

import logging
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)


class GroqClient:
    """Groq API client for fast, cost-effective LLM inference."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        
    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1200,
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
                return data["choices"][0]["message"]["content"]
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
                logger.error(f"Groq API HTTP error {e.response.status_code}: {error_detail}")
                raise Exception(f"Groq API error {e.response.status_code}: {error_detail}")
            except Exception as e:
                logger.error(f"Groq API error: {e}")
                raise


# Current supported Groq models
GROQ_MODELS = {
    "llama-3.3-70b": "llama-3.3-70b-versatile"  # Only confirmed working model
}