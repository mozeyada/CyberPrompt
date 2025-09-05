import logging

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Query

from app.core.security import validate_api_key_header
from app.db.connection import get_database
from app.models import LengthBin, Prompt, SafetyTag, ScenarioType
from app.services.prompt_generator import generate_and_save_prompts
from app.utils.ulid_gen import generate_ulid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/import")
async def import_prompts(
    prompts: list[dict],
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Import and upsert prompts"""
    validate_api_key_header(x_api_key)

    try:
        from app.db.repositories import PromptRepository
        prompt_repo = PromptRepository()

        imported_ids = []
        rejected_count = 0

        for prompt_data in prompts:
            try:
                # Validate safety tag
                safety_tag = SafetyTag(prompt_data.get("safety_tag", "SAFE_DOC"))
                if safety_tag == SafetyTag.BLOCKED:
                    rejected_count += 1
                    continue

                # Create prompt object
                if "prompt_id" not in prompt_data:
                    prompt_data["prompt_id"] = generate_ulid()

                prompt = Prompt(**prompt_data)
                prompt_id = await prompt_repo.upsert(prompt)
                imported_ids.append(prompt_id)

            except Exception as e:
                logger.warning(f"Failed to import prompt: {e}")
                rejected_count += 1

        return {
            "imported": len(imported_ids),
            "rejected": rejected_count,
            "prompt_ids": imported_ids,
        }

    except Exception as e:
        logger.error(f"Error importing prompts: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-from-document/{doc_id}", status_code=202)
async def generate_prompts_from_document(
    doc_id: str,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(..., description="API key"),
):
    """Generate prompts from source document in background"""
    validate_api_key_header(x_api_key)

    try:
        # Schedule background task
        db = get_database()
        background_tasks.add_task(generate_and_save_prompts, doc_id, db)

        return {
            "message": "Prompt generation started in background",
            "doc_id": doc_id,
            "status": "accepted",
        }

    except Exception as e:
        logger.error(f"Error scheduling prompt generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_prompts(
    scenario: ScenarioType | None = None,
    length_bin: LengthBin | None = None,
    category: str | None = Query(None, description="Original CySecBench category"),
    source: str | None = Query(None, description="Data source (e.g., CySecBench)"),
    min_words: int | None = Query(None, ge=1, description="Minimum word count"),
    max_words: int | None = Query(None, ge=1, description="Maximum word count"),
    q: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """List prompts with filters and proper validation"""
    validate_api_key_header(x_api_key)

    try:
        from app.db.repositories import PromptRepository
        prompt_repo = PromptRepository()

        prompts = await prompt_repo.list_prompts(
            scenario=scenario,
            length_bin=length_bin,
            category=category,
            source=source,
            min_words=min_words,
            max_words=max_words,
            q=q,
            page=page,
            limit=limit,
        )

        return {
            "prompts": [prompt.model_dump() for prompt in prompts],
            "page": page,
            "limit": limit,
            "count": len(prompts),
        }

    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Data validation error: {e!s}")


@router.get("/{prompt_id}")
async def get_prompt(
    prompt_id: str,
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Get prompt by ID with proper validation"""
    validate_api_key_header(x_api_key)

    try:
        from app.db.repositories import PromptRepository
        prompt_repo = PromptRepository()

        prompt = await prompt_repo.get_by_id(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail=f"Prompt with id {prompt_id} not found")

        return {"prompt": prompt.model_dump()}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Data validation error: {e!s}")
