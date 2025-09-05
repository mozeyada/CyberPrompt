import logging
import re

logger = logging.getLogger(__name__)

# Patterns for potentially hallucinated content in SOC/GRC context
SUSPECT_PATTERNS = [
    r"\bCVE-\d{4}-\d{4,7}\b",  # CVE identifiers
    r"\b(?:NIST|ISO|PCI-DSS|SOC2)\s?\d{2,}\b",  # Standards with numbers
    r"\b(?:host|ip|asset):\s*[A-Za-z0-9\.\-]{6,}\b",  # Specific hosts/IPs
    r"\b[A-Z]{2,}-\d{3,}\b",  # Generic ID patterns like REQ-123
    r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",  # IP addresses
]


class RiskHeuristics:
    """Risk assessment heuristics for detecting potential hallucinations"""

    def __init__(self):
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in SUSPECT_PATTERNS]

    def hallucination_flags(self, output: str, context: str = "") -> int:
        """
        Count potential hallucination flags in output

        Args:
            output: Model output to check
            context: Original context/prompt to verify against

        Returns:
            Number of potential hallucination flags
        """
        flags = 0

        try:
            for pattern in self.compiled_patterns:
                matches = pattern.findall(output)
                for match in matches:
                    # Check if this specific match appears in the context
                    if context and match.lower() not in context.lower():
                        flags += 1
                        logger.debug(f"Potential hallucination: {match}")
                    elif not context:
                        # If no context provided, flag all matches
                        flags += 1

        except Exception as e:
            logger.error(f"Error in hallucination detection: {e}")

        return flags

    def extract_entities(self, text: str) -> set[str]:
        """Extract entities that might be hallucinated"""
        entities = set()

        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            entities.update(matches)

        return entities

    def risk_score(self, output: str, context: str = "") -> float:
        """
        Calculate a risk score based on potential hallucinations

        Returns:
            Risk score from 0.0 (low risk) to 1.0 (high risk)
        """
        flags = self.hallucination_flags(output, context)
        output_length = len(output.split())

        if output_length == 0:
            return 1.0

        # Normalize by output length (flags per 100 words)
        risk_density = (flags * 100) / output_length

        # Convert to 0-1 scale (capped at 1.0)
        return min(1.0, risk_density / 5.0)  # 5+ flags per 100 words = max risk


# Global instance
risk_heuristics = RiskHeuristics()
