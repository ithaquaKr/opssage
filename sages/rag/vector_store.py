"""
Vector store implementation using ChromaDB for document storage and retrieval.
"""

import logging
import uuid
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

from sages.config import get_config
from sages.rag.embeddings import get_embedding_service

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector store for storing and retrieving document embeddings.
    Uses ChromaDB as the underlying vector database.
    """

    def __init__(self, persist_directory: str | None = None) -> None:
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory to persist the vector database (uses config if not provided)
        """
        if persist_directory is None:
            config = get_config()
            persist_directory = config.get("rag.chromadb_path", "./data/chromadb")

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create collections
        self.documents_collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "SRE documentation and runbooks"},
        )

        self.playbooks_collection = self.client.get_or_create_collection(
            name="playbooks",
            metadata={"description": "Incident response playbooks"},
        )

        self.incidents_collection = self.client.get_or_create_collection(
            name="incidents",
            metadata={"description": "Historical incident data"},
        )

        self.embedding_service = get_embedding_service()
        logger.info(f"Vector store initialized at {self.persist_directory}")

    def add_document(
        self,
        text: str,
        metadata: dict[str, Any],
        collection_name: str = "documents",
        document_id: str | None = None,
    ) -> str:
        """
        Add a document to the vector store.

        Args:
            text: Document text content
            metadata: Document metadata (filename, type, etc.)
            collection_name: Which collection to add to
            document_id: Optional document ID (generated if not provided)

        Returns:
            Document ID
        """
        if document_id is None:
            document_id = str(uuid.uuid4())

        # Get the collection
        collection = self._get_collection(collection_name)

        # Generate embedding
        embedding = self.embedding_service.embed_text(text)

        # Add to collection
        collection.add(
            ids=[document_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
        )

        logger.info(
            f"Added document {document_id} to {collection_name} "
            f"(metadata: {metadata.get('filename', 'unknown')})"
        )
        return document_id

    def add_documents_batch(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]],
        collection_name: str = "documents",
        document_ids: list[str] | None = None,
    ) -> list[str]:
        """
        Add multiple documents to the vector store.

        Args:
            texts: List of document texts
            metadatas: List of metadata dictionaries
            collection_name: Which collection to add to
            document_ids: Optional list of document IDs

        Returns:
            List of document IDs
        """
        if document_ids is None:
            document_ids = [str(uuid.uuid4()) for _ in texts]

        collection = self._get_collection(collection_name)

        # Generate embeddings
        embeddings = self.embedding_service.embed_texts(texts)

        # Add to collection
        collection.add(
            ids=document_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        logger.info(f"Added {len(texts)} documents to {collection_name}")
        return document_ids

    def search(
        self,
        query: str,
        collection_name: str = "documents",
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for similar documents using vector similarity.

        Args:
            query: Search query text
            collection_name: Which collection to search
            top_k: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of search results with documents, metadata, and scores
        """
        collection = self._get_collection(collection_name)

        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)

        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append(
                    {
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                        "relevance": 1.0
                        / (1.0 + results["distances"][0][i]),  # Convert distance to relevance score
                    }
                )

        return formatted_results

    def get_document(
        self, document_id: str, collection_name: str = "documents"
    ) -> dict[str, Any] | None:
        """
        Get a specific document by ID.

        Args:
            document_id: Document ID to retrieve
            collection_name: Which collection to search

        Returns:
            Document data or None if not found
        """
        collection = self._get_collection(collection_name)

        results = collection.get(ids=[document_id], include=["documents", "metadatas"])

        if results["ids"]:
            return {
                "id": results["ids"][0],
                "document": results["documents"][0],
                "metadata": results["metadatas"][0],
            }

        return None

    def delete_document(
        self, document_id: str, collection_name: str = "documents"
    ) -> bool:
        """
        Delete a document from the vector store.

        Args:
            document_id: Document ID to delete
            collection_name: Which collection to delete from

        Returns:
            True if deleted, False if not found
        """
        collection = self._get_collection(collection_name)

        try:
            collection.delete(ids=[document_id])
            logger.info(f"Deleted document {document_id} from {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False

    def list_documents(
        self,
        collection_name: str = "documents",
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        List documents in a collection.

        Args:
            collection_name: Which collection to list
            limit: Maximum number of documents to return
            offset: Offset for pagination

        Returns:
            List of documents with metadata
        """
        collection = self._get_collection(collection_name)

        # Get all IDs (ChromaDB doesn't have built-in pagination)
        results = collection.get(include=["metadatas"], limit=limit, offset=offset)

        documents = []
        if results["ids"]:
            for i, doc_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i] if results["metadatas"] else {}

                # Extract top-level fields from metadata for better API structure
                documents.append({
                    "id": doc_id,
                    "filename": metadata.get("filename", "unknown"),
                    "collection": collection_name,
                    "metadata": metadata
                })

        return documents

    def count_documents(self, collection_name: str = "documents") -> int:
        """
        Count documents in a collection.

        Args:
            collection_name: Which collection to count

        Returns:
            Number of documents
        """
        collection = self._get_collection(collection_name)
        return collection.count()

    def _get_collection(self, collection_name: str):
        """Get a collection by name."""
        if collection_name == "playbooks":
            return self.playbooks_collection
        elif collection_name == "incidents":
            return self.incidents_collection
        else:
            return self.documents_collection


# Global singleton instance
_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """
    Get the global vector store singleton.

    Returns:
        The global VectorStore instance
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
