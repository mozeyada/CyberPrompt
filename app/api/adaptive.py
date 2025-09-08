import logging
from typing import List

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.core.security import validate_api_key_header
from app.utils.adaptive_prompt_generator import generate_adaptive_prompts

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/adaptive", tags=["adaptive"])


class AdaptivePromptRequest(BaseModel):
    document_text: str = Field(..., min_length=50, description="Source document content")
    task_type: str = Field(..., description="SOC/GRC task type")
    model: str = Field(default="gpt-4", description="LLM model for generation")


class AdaptivePromptResponse(BaseModel):
    prompts: List[str] = Field(..., description="Generated benchmark prompts")
    task_type: str = Field(..., description="Task type used for generation")
    count: int = Field(..., description="Number of prompts generated")


@router.post("/generate", response_model=AdaptivePromptResponse)
async def generate_adaptive_prompts_endpoint(
    request: AdaptivePromptRequest,
    x_api_key: str = Header(..., description="API key"),
) -> AdaptivePromptResponse:
    """Generate adaptive benchmark prompts from document text"""
    validate_api_key_header(x_api_key)
    
    try:
        prompts = await generate_adaptive_prompts(
            document_text=request.document_text,
            task_type=request.task_type,
            model=request.model
        )
        
        return AdaptivePromptResponse(
            prompts=prompts,
            task_type=request.task_type,
            count=len(prompts)
        )
        
    except Exception as e:
        logger.error(f"Error in adaptive prompt generation endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))