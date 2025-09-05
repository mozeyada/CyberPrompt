import json
import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.repositories import PromptRepository, SourceDocumentRepository
from app.models import Prompt, ScenarioType, SourceType
from app.services.llm_client import ModelRunner
from app.utils.ulid_gen import generate_ulid

logger = logging.getLogger(__name__)


async def generate_and_save_prompts(doc_id: str, db: AsyncIOMotorDatabase):
    """Generate prompts from source document using LLM and save to database"""
    try:
        # Fetch source document
        doc_repo = SourceDocumentRepository(db)
        document = await doc_repo.get_by_id(doc_id)

        if not document:
            logger.error(f"Document {doc_id} not found")
            return

        # Determine scenario based on source type
        scenario = ScenarioType.GRC_MAPPING if document.source_type.value == "GRC_POLICY" else ScenarioType.CTI_SUMMARY

        # Create meta-prompt for LLM
        meta_prompt = f"""Based on the following security document, generate 5 distinct, high-quality benchmark prompts for a cybersecurity professional. Each prompt should be a specific task related to the document's content.

Document Type: {document.source_type.value}
Document Content: {document.content[:2000]}...

Requirements:
- Each prompt should be actionable and specific
- Focus on {scenario.value.lower().replace('_', ' ')} tasks
- Return ONLY a JSON array of strings
- No additional text or formatting

Example format: ["prompt 1", "prompt 2", "prompt 3", "prompt 4", "prompt 5"]"""

        # Generate prompts using LLM
        from app.core.config import settings
        model_runner = ModelRunner(
            openai_key=settings.openai_api_key,
            anthropic_key=settings.anthropic_api_key,
            google_key=settings.google_api_key,
        )

        result = await model_runner.execute_run(
            model="gpt-4o",
            prompt=meta_prompt,
            settings={"temperature": 0.7, "max_output_tokens": 800},
        )

        if not result["success"]:
            logger.error(f"LLM generation failed: {result.get('error')}")
            return

        response = result["response"]

        # Parse JSON response
        try:
            generated_prompts = json.loads(response.strip())
            if not isinstance(generated_prompts, list):
                msg = "Response is not a list"
                raise ValueError(msg)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return

        # Save prompts to database
        prompt_repo = PromptRepository(db)
        saved_count = 0

        for prompt_text in generated_prompts:
            if isinstance(prompt_text, str) and len(prompt_text.strip()) > 10:
                prompt = Prompt(
                    prompt_id=generate_ulid(),
                    text=prompt_text.strip(),
                    source=SourceType.CURATED,
                    scenario=scenario,
                    complexity=3,
                    tags=[f"adaptive_{document.source_type.value.lower()}", f"doc_{doc_id}"],
                )

                await prompt_repo.create(prompt)
                saved_count += 1

        logger.info(f"Generated and saved {saved_count} prompts from document {doc_id}")

    except Exception as e:
        logger.error(f"Error generating prompts from document {doc_id}: {e}")
        raise
