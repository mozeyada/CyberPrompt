import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models import (
    BaselineRun,
    LengthBin,
    OutputBlob,
    Prompt,
    Run,
    RunStatus,
    ScenarioType,
    SourceDocument,
)
from app.utils.mongodb import convert_objectid, convert_objectid_list

from .connection import get_database

logger = logging.getLogger(__name__)


class PromptRepository:
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self.db = db or get_database()
        self.collection = self.db.prompts

    async def create(self, prompt: Prompt) -> str:
        """Create a new prompt"""
        await self.collection.insert_one(prompt.model_dump())
        return prompt.prompt_id

    async def upsert(self, prompt: Prompt) -> str:
        """Upsert prompt by prompt_id"""
        await self.collection.replace_one(
            {"prompt_id": prompt.prompt_id},
            prompt.model_dump(),
            upsert=True,
        )
        return prompt.prompt_id

    async def get_by_id(self, prompt_id: str) -> Prompt | None:
        """Get prompt by ID with proper validation"""
        doc = await self.collection.find_one({"prompt_id": prompt_id})
        if not doc:
            return None

        try:
            doc = convert_objectid(doc)
            return Prompt(**doc)
        except Exception as e:
            logger.warning(f"Validation error for prompt {prompt_id}: {e}")
            return None

    async def list_prompts(
        self,
        scenario: ScenarioType | None = None,
        length_bin: LengthBin | None = None,
        category: str | None = None,
        source: str | None = None,
        prompt_type: str | None = None,
        min_tokens: int | None = None,
        max_tokens: int | None = None,
        include_variants: bool = False,
        q: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> list[Prompt]:
        """List prompts with filters"""
        filter_query = {}

        if scenario:
            filter_query["scenario"] = scenario
        if length_bin:
            filter_query["length_bin"] = length_bin
        if category:
            filter_query["category"] = category
        if source:
            filter_query["source"] = source
        if prompt_type:
            filter_query["prompt_type"] = prompt_type
        if min_tokens or max_tokens:
            token_filter = {}
            if min_tokens:
                token_filter["$gte"] = min_tokens
            if max_tokens:
                token_filter["$lte"] = max_tokens
            filter_query["token_count"] = token_filter
        if q:
            filter_query["$text"] = {"$search": q}

        skip = (page - 1) * limit
        cursor = self.collection.find(filter_query).skip(skip).limit(limit)

        docs = await cursor.to_list(length=limit)
        docs = convert_objectid_list(docs)

        validated_prompts = []
        for doc in docs:
            try:
                validated_prompts.append(Prompt(**doc))
            except Exception as e:
                logger.warning(f"Skipping invalid prompt document: {e}")
                continue

        # If include_variants is True, expand original prompts to include their variants
        if include_variants:
            expanded_prompts = []
            original_ids = set()
            
            for prompt in validated_prompts:
                expanded_prompts.append(prompt)
                
                # If this is an original prompt (no variant_of), find its variants
                if not prompt.metadata or not prompt.metadata.get('variant_of'):
                    original_ids.add(prompt.prompt_id)
            
            # Find all variants for the original prompts
            if original_ids:
                variant_cursor = self.collection.find({
                    'metadata.variant_of': {'$in': list(original_ids)}
                })
                variant_docs = await variant_cursor.to_list(length=None)
                variant_docs = convert_objectid_list(variant_docs)
                
                for doc in variant_docs:
                    try:
                        expanded_prompts.append(Prompt(**doc))
                    except Exception as e:
                        logger.warning(f"Skipping invalid variant document: {e}")
                        continue
            
            return expanded_prompts

        return validated_prompts


class RunRepository:
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self.db = db or get_database()
        self.collection = self.db.runs

    async def create(self, run: Run) -> str:
        """Create a new run"""
        await self.collection.insert_one(run.model_dump())
        return run.run_id

    async def update(self, run_id: str, update_data: dict[str, Any]) -> bool:
        """Update run by ID"""
        result = await self.collection.update_one(
            {"run_id": run_id},
            {"$set": update_data},
        )
        return result.modified_count > 0

    async def get_by_id(self, run_id: str) -> Run | None:
        """Get run by ID with proper validation"""
        doc = await self.collection.find_one({"run_id": run_id})
        if not doc:
            return None

        try:
            doc = convert_objectid(doc)
            return Run(**doc)
        except Exception as e:
            logger.error(f"Validation error for run {run_id}: {e}")
            return None

    async def list_runs(
        self,
        status: RunStatus | None = None,
        prompt_id: str | None = None,
        model: str | None = None,
        scenario: ScenarioType | None = None,
        length_bin: LengthBin | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> list[Run]:
        """List runs with filters"""
        filter_query = {}

        if status:
            filter_query["status"] = status
        if prompt_id:
            filter_query["prompt_id"] = prompt_id
        if model:
            filter_query["model"] = model
        if scenario:
            filter_query["scenario"] = scenario
        if length_bin:
            filter_query["length_bin"] = length_bin

        skip = (page - 1) * limit
        cursor = self.collection.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)

        docs = await cursor.to_list(length=limit)
        docs = convert_objectid_list(docs)

        validated_runs = []
        for doc in docs:
            try:
                validated_runs.append(Run(**doc))
            except Exception as e:
                logger.warning(f"Skipping invalid run document: {e}")
                continue

        return validated_runs


class OutputBlobRepository:
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self.db = db or get_database()
        self.collection = self.db.output_blobs

    async def store(self, blob: OutputBlob) -> str:
        """Store output blob"""
        await self.collection.insert_one(blob.model_dump())
        return blob.blob_id

    async def get_by_id(self, blob_id: str) -> OutputBlob | None:
        """Get blob by ID with proper validation"""
        doc = await self.collection.find_one({"blob_id": blob_id})
        if not doc:
            return None

        try:
            doc = convert_objectid(doc)
            return OutputBlob(**doc)
        except Exception as e:
            logger.error(f"Validation error for blob {blob_id}: {e}")
            return None


class BaselineRepository:
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self.db = db or get_database()
        self.collection = self.db.baselines

    async def create(self, baseline: BaselineRun) -> str:
        """Create a new baseline run"""
        await self.collection.insert_one(baseline.model_dump())
        return baseline.baseline_id

    async def list_by_source(self, source: str, model: str | None = None) -> list[BaselineRun]:
        """List baseline runs by source"""
        filter_query = {"source": source}
        if model:
            filter_query["model"] = model

        cursor = self.collection.find(filter_query)
        docs = await cursor.to_list(length=None)
        docs = convert_objectid_list(docs)

        validated_baselines = []
        for doc in docs:
            try:
                validated_baselines.append(BaselineRun(**doc))
            except Exception as e:
                logger.warning(f"Skipping invalid baseline document: {e}")
                continue

        return validated_baselines


class SourceDocumentRepository:
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self.db = db or get_database()
        self.collection = self.db.source_documents

    async def create(self, document: SourceDocument) -> str:
        """Create a new source document"""
        await self.collection.insert_one(document.model_dump())
        return document.doc_id

    async def get_by_id(self, doc_id: str) -> SourceDocument | None:
        """Get source document by ID with proper validation"""
        doc = await self.collection.find_one({"doc_id": doc_id})
        if not doc:
            return None

        try:
            doc = convert_objectid(doc)
            return SourceDocument(**doc)
        except Exception as e:
            logger.error(f"Validation error for document {doc_id}: {e}")
            return None

    async def list_documents(self) -> list[SourceDocument]:
        """List all source documents with proper validation"""
        cursor = self.collection.find({}).sort("created_at", -1)
        docs = await cursor.to_list(length=None)
        docs = convert_objectid_list(docs)

        validated_documents = []
        for doc in docs:
            try:
                validated_documents.append(SourceDocument(**doc))
            except Exception as e:
                logger.warning(f"Skipping invalid document: {e}")
                continue

        return validated_documents

    async def delete_by_id(self, doc_id: str) -> bool:
        """Delete source document by ID"""
        result = await self.collection.delete_one({"doc_id": doc_id})
        return result.deleted_count > 0
