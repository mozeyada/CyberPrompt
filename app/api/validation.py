import logging
from typing import Dict, List

import numpy as np
from fastapi import APIRouter, Header, HTTPException
from scipy.stats import entropy

from app.core.security import validate_api_key_header
from app.db.repositories import PromptRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/validation", tags=["validation"])


@router.get("/kl-divergence")
async def calculate_kl_divergence(
    x_api_key: str = Header(..., description="API key"),
) -> Dict:
    """Calculate KL divergence between adaptive and static prompts"""
    validate_api_key_header(x_api_key)
    
    try:
        repo = PromptRepository()
        
        # Get static prompts (CySecBench baseline)
        static_prompts = await repo.list_prompts(source="CySecBench", limit=1000)
        
        # Get adaptive prompts
        adaptive_prompts = await repo.list_prompts(source="adaptive", limit=1000)
        
        if not static_prompts or not adaptive_prompts:
            raise HTTPException(status_code=400, detail="Need both CySecBench baseline and adaptive prompts to validate RQ2")
        
        # Calculate scenario distribution KL divergence
        scenario_kl = _calculate_scenario_kl_divergence(static_prompts, adaptive_prompts)
        
        # Calculate length distribution KL divergence
        length_kl = _calculate_length_kl_divergence(static_prompts, adaptive_prompts)
        
        return {
            "scenario_kl_divergence": scenario_kl,
            "length_kl_divergence": length_kl,
            "interpretation": _interpret_kl_scores(scenario_kl, length_kl),
            "static_count": len(static_prompts),
            "adaptive_count": len(adaptive_prompts)
        }
        
    except Exception as e:
        logger.error(f"Error calculating KL divergence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _calculate_scenario_kl_divergence(static_prompts: List, adaptive_prompts: List) -> float:
    """Calculate KL divergence for scenario distributions"""
    scenarios = ["SOC_INCIDENT", "GRC_MAPPING", "CTI_SUMMARY"]
    
    # Count scenarios in each dataset
    static_counts = {s: sum(1 for p in static_prompts if p.scenario == s) for s in scenarios}
    adaptive_counts = {s: sum(1 for p in adaptive_prompts if p.scenario == s) for s in scenarios}
    
    # Convert to probability distributions
    static_total = sum(static_counts.values())
    adaptive_total = sum(adaptive_counts.values())
    
    static_dist = np.array([static_counts[s] / static_total for s in scenarios])
    adaptive_dist = np.array([adaptive_counts[s] / adaptive_total for s in scenarios])
    
    # Add small epsilon to avoid log(0)
    epsilon = 1e-10
    static_dist = static_dist + epsilon
    adaptive_dist = adaptive_dist + epsilon
    
    return float(entropy(adaptive_dist, static_dist))


def _calculate_length_kl_divergence(static_prompts: List, adaptive_prompts: List) -> float:
    """Calculate KL divergence for length distributions"""
    length_bins = ["XS", "S", "M", "L", "XL"]
    
    # Count length bins in each dataset
    static_counts = {lb: sum(1 for p in static_prompts if p.length_bin == lb) for lb in length_bins}
    adaptive_counts = {lb: sum(1 for p in adaptive_prompts if p.length_bin == lb) for lb in length_bins}
    
    # Convert to probability distributions
    static_total = sum(static_counts.values())
    adaptive_total = sum(adaptive_counts.values())
    
    static_dist = np.array([static_counts[lb] / static_total for lb in length_bins])
    adaptive_dist = np.array([adaptive_counts[lb] / adaptive_total for lb in length_bins])
    
    # Add small epsilon to avoid log(0)
    epsilon = 1e-10
    static_dist = static_dist + epsilon
    adaptive_dist = adaptive_dist + epsilon
    
    return float(entropy(adaptive_dist, static_dist))


def _interpret_kl_scores(scenario_kl: float, length_kl: float) -> Dict:
    """Interpret KL divergence scores for research"""
    def interpret_single(kl_score: float) -> str:
        if kl_score < 0.1:
            return "Very similar distributions"
        elif kl_score < 0.5:
            return "Moderately similar distributions"
        elif kl_score < 1.0:
            return "Noticeable differences"
        else:
            return "Significant distributional differences"
    
    return {
        "scenario_interpretation": interpret_single(scenario_kl),
        "length_interpretation": interpret_single(length_kl),
        "overall_assessment": "Representative" if max(scenario_kl, length_kl) < 1.0 else "Significant drift"
    }