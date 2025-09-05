import logging

import tiktoken

logger = logging.getLogger(__name__)

# Model to encoding mapping
MODEL_ENCODINGS = {
    "gpt-4": "cl100k_base",
    "gpt-4o": "cl100k_base",
    "gpt-4o-mini": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "claude-3-5-sonnet": "cl100k_base",  # Approximation
    "claude-3-opus": "cl100k_base",  # Approximation
    "claude-3-haiku": "cl100k_base",  # Approximation
}


class TokenMeter:
    """Token counting and cost calculation utility"""

    def __init__(self):
        self._encoders: dict[str, tiktoken.Encoding] = {}

    def _get_encoder(self, model: str) -> tiktoken.Encoding:
        """Get tiktoken encoder for model"""
        encoding_name = MODEL_ENCODINGS.get(model, "cl100k_base")

        if encoding_name not in self._encoders:
            try:
                self._encoders[encoding_name] = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                logger.warning(f"Failed to get encoding {encoding_name}: {e}")
                # Fallback to cl100k_base
                self._encoders[encoding_name] = tiktoken.get_encoding("cl100k_base")

        return self._encoders[encoding_name]

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for given model"""
        try:
            encoder = self._get_encoder(model)
            return len(encoder.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens for model {model}: {e}")
            # Fallback: rough estimation
            return len(text.split()) * 1.3  # Rough approximation

    def estimate_tokens(self, text: str) -> int:
        """Quick token estimation without model specifics"""
        return len(text.split()) * 1.3


class CostCalculator:
    """Cost calculation utility with dynamic pricing"""

    def __init__(self, pricing_config: dict[str, dict[str, float]]):
        self.pricing = pricing_config

    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str,
    ) -> tuple[float, float, float]:
        """
        Calculate cost in AUD
        Returns: (total_cost, input_unit_price, output_unit_price)
        """
        model_pricing = self.pricing.get(model, {"input": 0.0, "output": 0.0})

        input_price_per_1k = model_pricing.get("input", 0.0)
        output_price_per_1k = model_pricing.get("output", 0.0)

        input_cost = (input_tokens / 1000) * input_price_per_1k
        output_cost = (output_tokens / 1000) * output_price_per_1k
        total_cost = input_cost + output_cost

        return total_cost, input_price_per_1k, output_price_per_1k

    def update_pricing(self, pricing_config: dict[str, dict[str, float]]):
        """Update pricing configuration"""
        self.pricing = pricing_config


# Global instances
token_meter = TokenMeter()
cost_calculator = None  # Will be initialized with pricing config
