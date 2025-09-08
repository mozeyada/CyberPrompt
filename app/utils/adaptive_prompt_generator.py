import logging
from typing import List

from app.core.config import settings
from app.services.llm_client import LLMClientFactory

logger = logging.getLogger(__name__)


async def generate_adaptive_prompts(
    document_text: str, 
    task_type: str, 
    model: str = "gpt-4"
) -> List[str]:
    """
    Generate 3-5 benchmarking prompts from input document text for given task type.
    
    Args:
        document_text: Source document content to generate prompts from
        task_type: Type of SOC/GRC task (e.g., "incident_response", "compliance_mapping", "threat_assessment")
        model: LLM model to use for generation (default: gpt-4)
        
    Returns:
        List of generated benchmark prompt strings
    """
    try:
        # Create LLM client
        client = LLMClientFactory.create_client(
            model=model,
            openai_key=settings.openai_api_key,
            anthropic_key=settings.anthropic_api_key,
            google_key=settings.google_api_key
        )
        
        # Generate prompts using meta-prompt
        meta_prompt = _build_meta_prompt(document_text, task_type)
        
        response = await client.generate(
            model=model,
            prompt=meta_prompt,
            temperature=0.7,
            max_tokens=1200
        )
        
        # Parse response into individual prompts
        prompts = _parse_generated_prompts(response)
        
        logger.info(f"Generated {len(prompts)} adaptive prompts for task_type: {task_type}")
        return prompts
        
    except Exception as e:
        logger.error(f"Error generating adaptive prompts: {e}")
        raise


def _build_meta_prompt(document_text: str, task_type: str) -> str:
    """Build meta-prompt for generating SOC/GRC benchmark prompts"""
    
    task_styles = {
        "incident_response": "incident analysis, threat containment, forensic investigation",
        "compliance_mapping": "regulatory alignment, policy adherence, audit preparation", 
        "threat_assessment": "risk evaluation, vulnerability analysis, threat modeling",
        "soc_operations": "alert triage, security monitoring, incident classification",
        "grc_reporting": "compliance reporting, risk documentation, governance assessment"
    }
    
    style_guidance = task_styles.get(task_type, "cybersecurity analysis, security operations")
    
    return f"""You are a cybersecurity expert creating benchmark prompts for evaluating AI models in SOC/GRC contexts.

DOCUMENT CONTENT:
{document_text[:2000]}...

TASK: Generate 4 distinct benchmarking prompts for "{task_type}" tasks that vary in style: {style_guidance}.

REQUIREMENTS:
- Each prompt should test different aspects: summarization, classification, threat assessment, actionable recommendations
- Prompts should be realistic SOC/GRC scenarios based on the document content
- Include specific cybersecurity terminology and frameworks (MITRE, NIST, ISO 27001)
- Vary complexity from basic analysis to advanced strategic assessment
- Each prompt should be 50-150 words

FORMAT: Return exactly 4 prompts separated by "---PROMPT---" markers.

EXAMPLE OUTPUT:
---PROMPT---
[First prompt here]
---PROMPT---
[Second prompt here]
---PROMPT---
[Third prompt here]  
---PROMPT---
[Fourth prompt here]"""


def _parse_generated_prompts(response: str) -> List[str]:
    """Parse LLM response into individual prompt strings"""
    try:
        # Split by marker and clean up
        raw_prompts = response.split("---PROMPT---")
        
        prompts = []
        for prompt in raw_prompts:
            cleaned = prompt.strip()
            if cleaned and len(cleaned) > 20:  # Filter out empty/too short prompts
                prompts.append(cleaned)
        
        # Ensure we have 3-5 prompts
        if len(prompts) < 3:
            logger.warning(f"Only generated {len(prompts)} prompts, expected 3-5")
        
        return prompts[:5]  # Cap at 5 prompts
        
    except Exception as e:
        logger.error(f"Error parsing generated prompts: {e}")
        # Fallback: return response as single prompt
        return [response.strip()] if response.strip() else []