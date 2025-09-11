"""Token-based prompt classification utility."""

from app.models import LengthBin
from app.utils.token_meter import token_meter


def classify_by_tokens(token_count: int) -> LengthBin:
    """Classify prompt into length bin based on token count.
    
    Args:
        token_count: Number of tokens in the prompt
        
    Returns:
        LengthBin enum value based on token ranges for research comparison:
        - S: ≤16 tokens (Short prompts - ~33% of dataset)
        - M: 17-20 tokens (Medium prompts - ~33% of dataset)  
        - L: >20 tokens (Long prompts - ~33% of dataset)
    """
    if token_count <= 16:
        return LengthBin.S
    elif 17 <= token_count <= 20:
        return LengthBin.M
    elif token_count > 20:
        return LengthBin.L
    else:
        # Should not happen with current logic
        return None


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