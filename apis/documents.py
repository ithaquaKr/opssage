"""
Document management API endpoints for RAG pipeline.
Handles document upload, embedding, search, and management.
"""

import logging
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from sages.rag import DocumentProcessor, get_vector_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


# ============================================================================
# Request/Response Models
# ============================================================================


class DocumentMetadata(BaseModel):
    """Metadata for a document."""

    filename: str
    doc_type: str = Field(default="general", description="Type: general, playbook, incident")
    category: str | None = Field(default=None, description="Category or tag")
    description: str | None = None


class DocumentUploadResponse(BaseModel):
    """Response for document upload."""

    document_id: str
    filename: str
    collection: str
    char_count: int
    chunk_count: int
    status: str


class DocumentSearchRequest(BaseModel):
    """Request for document search."""

    query: str = Field(..., description="Search query")
    collection: str = Field(default="documents", description="Collection to search")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results")
    filters: dict[str, Any] | None = None


class DocumentSearchResult(BaseModel):
    """A single search result."""

    id: str
    text: str
    metadata: dict[str, Any]
    relevance: float


class DocumentSearchResponse(BaseModel):
    """Response for document search."""

    query: str
    results: list[DocumentSearchResult]
    total_results: int


class DocumentListResponse(BaseModel):
    """Response for listing documents."""

    documents: list[dict[str, Any]]
    total: int
    limit: int
    offset: int


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(default="general"),
    category: str = Form(default=""),
    description: str = Form(default=""),
) -> DocumentUploadResponse:
    """
    Upload a document to the RAG pipeline.

    Supports: TXT, MD, PDF, DOCX, JSON

    Args:
        file: File to upload
        doc_type: Document type (general, playbook, incident)
        category: Optional category/tag
        description: Optional description

    Returns:
        Upload confirmation with document ID
    """
    try:
        # Read file content
        content = await file.read()
        filename = file.filename or "unknown"

        logger.info(f"Uploading document: {filename} (type: {doc_type})")

        # Process document
        processor = DocumentProcessor()
        processed = processor.process_file(content, filename)

        # Chunk the text for better retrieval
        chunks = processor.chunk_text(processed["text"])

        # Prepare metadata
        base_metadata = {
            "filename": filename,
            "doc_type": doc_type,
            "category": category if category else "uncategorized",
            "description": description,
            "char_count": processed["char_count"],
            "word_count": processed["word_count"],
        }

        # Determine collection based on doc_type
        collection_map = {
            "playbook": "playbooks",
            "incident": "incidents",
            "general": "documents",
        }
        collection = collection_map.get(doc_type, "documents")

        # Add to vector store
        vector_store = get_vector_store()

        # Add each chunk as a separate document
        chunk_ids = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)

            chunk_id = vector_store.add_document(
                text=chunk, metadata=chunk_metadata, collection_name=collection
            )
            chunk_ids.append(chunk_id)

        return DocumentUploadResponse(
            document_id=chunk_ids[0],  # Return first chunk ID as main doc ID
            filename=filename,
            collection=collection,
            char_count=processed["char_count"],
            chunk_count=len(chunks),
            status="success",
        )

    except ValueError as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(request: DocumentSearchRequest) -> DocumentSearchResponse:
    """
    Search for documents using semantic similarity.

    Args:
        request: Search parameters

    Returns:
        Search results with relevance scores
    """
    try:
        vector_store = get_vector_store()

        results = vector_store.search(
            query=request.query,
            collection_name=request.collection,
            top_k=request.top_k,
            filters=request.filters,
        )

        formatted_results = [
            DocumentSearchResult(
                id=r["id"],
                text=r["document"],
                metadata=r["metadata"],
                relevance=r["relevance"],
            )
            for r in results
        ]

        return DocumentSearchResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results),
        )

    except Exception as e:
        logger.error(f"Error searching documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/list", response_model=DocumentListResponse)
async def list_documents(
    collection: str = "documents", limit: int = 100, offset: int = 0
) -> DocumentListResponse:
    """
    List documents in a collection.

    Args:
        collection: Collection name (documents, playbooks, incidents)
        limit: Maximum number of documents to return
        offset: Offset for pagination

    Returns:
        List of documents with metadata
    """
    try:
        vector_store = get_vector_store()

        documents = vector_store.list_documents(
            collection_name=collection, limit=limit, offset=offset
        )

        total = vector_store.count_documents(collection_name=collection)

        return DocumentListResponse(
            documents=documents, total=total, limit=limit, offset=offset
        )

    except Exception as e:
        logger.error(f"Error listing documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"List failed: {str(e)}")


@router.get("/{document_id}")
async def get_document(document_id: str, collection: str = "documents") -> dict[str, Any]:
    """
    Get a specific document by ID.

    Args:
        document_id: Document ID
        collection: Collection name

    Returns:
        Document data
    """
    try:
        vector_store = get_vector_store()

        document = vector_store.get_document(
            document_id=document_id, collection_name=collection
        )

        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        return document

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Get failed: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(
    document_id: str, collection: str = "documents"
) -> dict[str, str]:
    """
    Delete a document from the vector store.

    Args:
        document_id: Document ID to delete
        collection: Collection name

    Returns:
        Deletion confirmation
    """
    try:
        vector_store = get_vector_store()

        success = vector_store.delete_document(
            document_id=document_id, collection_name=collection
        )

        if not success:
            raise HTTPException(status_code=404, detail="Document not found")

        return {"status": "deleted", "document_id": document_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.get("/stats/{collection}")
async def get_collection_stats(collection: str = "documents") -> dict[str, Any]:
    """
    Get statistics for a collection.

    Args:
        collection: Collection name

    Returns:
        Collection statistics
    """
    try:
        vector_store = get_vector_store()

        count = vector_store.count_documents(collection_name=collection)

        return {"collection": collection, "document_count": count, "status": "active"}

    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")
