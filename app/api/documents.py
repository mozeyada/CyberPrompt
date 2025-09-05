import logging

from fastapi import APIRouter, Header, HTTPException

from app.core.security import validate_api_key_header
from app.db.repositories import SourceDocumentRepository
from app.models import SourceDocument, SourceDocumentCreate, SourceDocumentList
from app.utils.ulid_gen import generate_ulid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=dict)
async def create_document(
    document: SourceDocumentCreate,
    x_api_key: str = Header(..., description="API key"),
):
    """Create a new source document"""
    validate_api_key_header(x_api_key)

    try:
        doc_repo = SourceDocumentRepository()

        # Create document with generated ID
        new_doc = SourceDocument(
            doc_id=generate_ulid(),
            **document.model_dump(),
        )

        doc_id = await doc_repo.create(new_doc)

        return {
            "doc_id": doc_id,
            "message": "Document created successfully",
        }

    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[SourceDocumentList])
async def list_documents(
    x_api_key: str = Header(..., description="API key"),
):
    """List all source documents (metadata only)"""
    validate_api_key_header(x_api_key)

    try:
        doc_repo = SourceDocumentRepository()
        documents = await doc_repo.list_documents()

        # Return metadata only
        return [
            SourceDocumentList(
                doc_id=doc.doc_id,
                filename=doc.filename,
                source_type=doc.source_type,
                created_at=doc.created_at,
            )
            for doc in documents
        ]

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}", response_model=SourceDocument)
async def get_document(
    doc_id: str,
    x_api_key: str = Header(..., description="API key"),
):
    """Get a single document by ID including content"""
    validate_api_key_header(x_api_key)

    try:
        doc_repo = SourceDocumentRepository()
        document = await doc_repo.get_by_id(doc_id)

        if not document:
            raise HTTPException(status_code=404, detail=f"Document with id {doc_id} not found")

        return document

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    x_api_key: str = Header(..., description="API key"),
):
    """Delete a document by ID"""
    validate_api_key_header(x_api_key)

    try:
        doc_repo = SourceDocumentRepository()
        deleted = await doc_repo.delete_by_id(doc_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Document with id {doc_id} not found")

        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
