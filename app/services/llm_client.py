import logging
import time
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""

    @abstractmethod
    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
        seed: int | None = None,
    ) -> str:
        """Generate response from model"""

    @abstractmethod
    def get_token_counts(self, prompt: str, response: str, model: str) -> tuple[int, int]:
        """Get input and output token counts"""


class OpenAIClient(BaseLLMClient):
    """OpenAI API client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            import openai
            self._client = openai.AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            logger.error("OpenAI library not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
        seed: int | None = None,
    ) -> str:
        """Generate response using OpenAI API"""
        try:
            kwargs = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if seed is not None:
                kwargs["seed"] = seed

            start_time = time.time()
            response = await self._client.chat.completions.create(**kwargs)
            latency_ms = int((time.time() - start_time) * 1000)

            content = response.choices[0].message.content

            # Store usage info for later retrieval
            self._last_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "latency_ms": latency_ms,
            }

            return content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def get_token_counts(self, prompt: str, response: str, model: str) -> tuple[int, int]:
        """Get token counts from last API call"""
        if hasattr(self, "_last_usage"):
            return self._last_usage["prompt_tokens"], self._last_usage["completion_tokens"]

        # Fallback to estimation
        from app.utils.token_meter import token_meter
        input_tokens = token_meter.count_tokens(prompt, model)
        output_tokens = token_meter.count_tokens(response, model)
        return input_tokens, output_tokens


class AnthropicClient(BaseLLMClient):
    """Anthropic API client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None
        self._model_mapping = {
            "claude-3-5-sonnet": "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku": "claude-3-5-haiku-20241022", 
            "claude-3-opus": "claude-3-opus-20240229"
        }
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            self._client = anthropic.AsyncAnthropic(
                api_key=self.api_key,
                timeout=60.0  # Add timeout
            )
        except ImportError:
            logger.error("Anthropic library not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise

    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
        seed: int | None = None,
    ) -> str:
        """Generate response using Anthropic API"""
        try:
            # Map short model names to full names
            actual_model = self._model_mapping.get(model, model)
            
            start_time = time.time()
            
            # Prepare kwargs
            kwargs = {
                "model": actual_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            # Only add seed for specific Claude models that support it
            # Check against exact model names that support seed parameter
            models_with_seed = [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022"
            ]
            
            if seed is not None and model in models_with_seed:
                kwargs["seed"] = seed
            
            # Make the API call
            response = await self._client.messages.create(**kwargs)
            latency_ms = int((time.time() - start_time) * 1000)

            content = response.content[0].text

            # Store usage info
            self._last_usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                "latency_ms": latency_ms,
            }

            return content

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            logger.error(f"Model: {model}, Prompt length: {len(prompt)}")
            if "not_found_error" in str(e):
                logger.error("Available Claude models: claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022, claude-3-opus-20240229")
            raise

    def get_token_counts(self, prompt: str, response: str, model: str) -> tuple[int, int]:
        """Get token counts from last API call"""
        if hasattr(self, "_last_usage"):
            return self._last_usage["prompt_tokens"], self._last_usage["completion_tokens"]

        # Fallback to estimation
        from app.utils.token_meter import token_meter
        input_tokens = token_meter.count_tokens(prompt, model)
        output_tokens = token_meter.count_tokens(response, model)
        return input_tokens, output_tokens


class GoogleClient(BaseLLMClient):
    """Google Gemini API client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Google Gemini client"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai
        except ImportError:
            logger.error("Google GenerativeAI library not installed. Install with: pip install google-generativeai")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Google Gemini client: {e}")
            raise

    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
        seed: int | None = None,
    ) -> str:
        """Generate response using Google Gemini API"""
        try:
            # Map our model name to Google's
            google_model = model.replace("gemini-2.5-flash", "gemini-2.0-flash-exp")

            start_time = time.time()
            model_instance = self._client.GenerativeModel(google_model)

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            response = await model_instance.generate_content_async(
                prompt,
                generation_config=generation_config,
            )
            latency_ms = int((time.time() - start_time) * 1000)

            content = response.text

            # Store usage info (Gemini doesn't provide detailed token counts in all regions)
            # We'll estimate for now
            from app.utils.token_meter import token_meter
            input_tokens = token_meter.count_tokens(prompt, model)
            output_tokens = token_meter.count_tokens(content, model)

            self._last_usage = {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "latency_ms": latency_ms,
            }

            return content

        except Exception as e:
            logger.error(f"Google Gemini API error: {e}")
            raise

    def get_token_counts(self, prompt: str, response: str, model: str) -> tuple[int, int]:
        """Get token counts from last API call"""
        if hasattr(self, "_last_usage"):
            return self._last_usage["prompt_tokens"], self._last_usage["completion_tokens"]

        # Fallback to estimation
        from app.utils.token_meter import token_meter
        input_tokens = token_meter.count_tokens(prompt, model)
        output_tokens = token_meter.count_tokens(response, model)
        return input_tokens, output_tokens


class LLMClientFactory:
    """Factory for creating LLM clients"""

    @staticmethod
    def create_client(model: str, openai_key: str = "", anthropic_key: str = "", google_key: str = "") -> BaseLLMClient:
        """Create appropriate client for model"""
        if model.startswith("gpt") or "gpt" in model.lower():
            return OpenAIClient(openai_key)
        elif "claude" in model.lower():
            return AnthropicClient(anthropic_key)
        elif "gemini" in model.lower():
            return GoogleClient(google_key)
        else:
            # Default to OpenAI for unknown models
            logger.warning(f"Unknown model {model}, defaulting to OpenAI client")
            return OpenAIClient(openai_key)


class ModelRunner:
    """Manages model execution with multiple clients"""

    def __init__(self, openai_key: str = "", anthropic_key: str = "", google_key: str = ""):
        self.openai_key = openai_key
        self.anthropic_key = anthropic_key
        self.google_key = google_key
        self._clients: dict[str, BaseLLMClient] = {}

    def _get_client(self, model: str) -> BaseLLMClient:
        """Get or create client for model"""
        if model not in self._clients:
            self._clients[model] = LLMClientFactory.create_client(
                model, self.openai_key, self.anthropic_key, self.google_key,
            )
        return self._clients[model]

    async def execute_run(
        self,
        model: str,
        prompt: str,
        settings: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a single model run"""
        try:
            client = self._get_client(model)

            # Generate response
            start_time = time.time()
            response = await client.generate(
                model=model,
                prompt=prompt,
                temperature=settings.get("temperature", 0.2),
                max_tokens=settings.get("max_output_tokens", 800),
                seed=settings.get("seed"),
            )
            latency_ms = int((time.time() - start_time) * 1000)

            # Get token counts
            input_tokens, output_tokens = client.get_token_counts(prompt, response, model)

            return {
                "response": response,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens,
                },
                "latency_ms": latency_ms,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Model execution failed for {model}: {e}")
            return {
                "response": "",
                "tokens": {"input": 0, "output": 0, "total": 0},
                "latency_ms": 0,
                "success": False,
                "error": str(e),
            }
