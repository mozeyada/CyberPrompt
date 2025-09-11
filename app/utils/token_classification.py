"""Token-based prompt classification utility."""

from app.models import LengthBin
from app.utils.token_meter import token_meter


def classify_by_tokens(token_count: int) -> LengthBin:
    """Classify prompt into length bin based on token count.
    
    Args:
        token_count: Number of tokens in the prompt
        
    Returns:
        LengthBin enum value based on continuous cybersecurity prompt ranges:
        - S: ≤300 tokens (Short SOC/GRC prompts)
        - M: 301-800 tokens (Medium SOC/GRC prompts)  
        - L: >800 tokens (Long SOC/GRC prompts)
    """
    if token_count <= 300:
        return LengthBin.S
    elif 301 <= token_count <= 800:
        return LengthBin.M
    else:  # > 800
        return LengthBin.L


def get_token_count_and_bin(text: str, model: str = "gpt-4o") -> tuple[int, LengthBin | None]:
    """Get token count and classification bin for prompt text.
    
    Args:
        text: Prompt text to analyze
        model: Model to use for tokenization (default: gpt-4o)
        
    Returns:
        Tuple of (token_count, length_bin)
    """
    token_count = token_meter.count_tokens(text, model)
    length_bin = classify_by_tokens(token_count)
    return token_count, length_bin