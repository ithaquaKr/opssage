"""
RAG (Retrieval-Augmented Generation) system for OpsSage.

Provides simple interface for document management and knowledge retrieval.
"""

from typing import Any

from sages.rag.document_processor import DocumentProcessor
from sages.rag.vector_store import VectorStore

# Global instances (lazy loaded)
_vector_store: VectorStore | None = None
_document_processor: DocumentProcessor | None = None


def get_vector_store() -> VectorStore:
    """Get or create the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def get_document_processor() -> DocumentProcessor:
    """Get or create the global document processor instance."""
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor


# Simple API for document management


def upload_document(file_path: str, metadata: dict[str, Any] | None = None) -> str:
    """
    Upload a document to the knowledge base.

    Args:
        file_path: Path to the document file (PDF, Markdown, DOCX, or TXT)
        metadata: Optional metadata to attach to the document

    Returns:
        Document ID

    Example:
        >>> doc_id = upload_document("runbook.pdf", {"type": "runbook", "team": "platform"})
    """
    processor = get_document_processor()
    vector_store = get_vector_store()

    # Process document
    chunks = processor.process_file(file_path, metadata or {})

    # Store chunks in vector store
    doc_ids = []
    for chunk in chunks:
        doc_id = vector_store.add_document(
            text=chunk["text"],
            metadata=chunk["metadata"],
            collection_name="documents",
        )
        doc_ids.append(doc_id)

    return doc_ids[0] if doc_ids else ""


def search_documents(
    query: str,
    top_k: int = 5,
    collection_name: str = "documents",
) -> list[dict[str, Any]]:
    """
    Search documents by semantic similarity.

    Args:
        query: Search query
        top_k: Number of results to return
        collection_name: Collection to search in

    Returns:
        List of matching documents with text, metadata, and similarity scores

    Example:
        >>> results = search_documents("how to handle pod crash loop", top_k=3)
        >>> for result in results:
        ...     print(result["text"], result["score"])
    """
    vector_store = get_vector_store()
    return vector_store.search(
        query=query,
        top_k=top_k,
        collection_name=collection_name,
    )


def list_documents(collection_name: str = "documents") -> list[dict[str, Any]]:
    """
    List all documents in the knowledge base.

    Args:
        collection_name: Collection to list documents from

    Returns:
        List of document metadata

    Example:
        >>> docs = list_documents()
        >>> for doc in docs:
        ...     print(doc["id"], doc["metadata"].get("filename"))
    """
    vector_store = get_vector_store()
    return vector_store.list_documents(collection_name=collection_name)


def delete_document(document_id: str, collection_name: str = "documents") -> bool:
    """
    Delete a document from the knowledge base.

    Args:
        document_id: ID of the document to delete
        collection_name: Collection to delete from

    Returns:
        True if document was deleted, False otherwise

    Example:
        >>> delete_document("abc-123-def-456")
    """
    vector_store = get_vector_store()
    vector_store.delete_document(document_id, collection_name=collection_name)
    return True


def get_document(document_id: str, collection_name: str = "documents") -> dict[str, Any] | None:
    """
    Get a specific document by ID.

    Args:
        document_id: ID of the document
        collection_name: Collection to retrieve from

    Returns:
        Document data or None if not found

    Example:
        >>> doc = get_document("abc-123-def-456")
        >>> print(doc["text"])
    """
    vector_store = get_vector_store()
    return vector_store.get_document(document_id, collection_name=collection_name)


# Export all public functions
__all__ = [
    "VectorStore",
    "DocumentProcessor",
    "get_vector_store",
    "get_document_processor",
    "upload_document",
    "search_documents",
    "list_documents",
    "delete_document",
    "get_document",
]
