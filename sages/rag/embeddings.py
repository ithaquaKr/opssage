"""
Embedding service for generating vector embeddings from text.
"""

from typing import Any

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Service for generating embeddings using sentence-transformers.
    Uses a lightweight model suitable for semantic search.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize the embedding service.

        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.model_name = model_name
        self.model: SentenceTransformer | None = None

    def _ensure_model_loaded(self) -> None:
        """Lazy load the model on first use."""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

    def embed_text(self, text: str) -> list[float]:
        """
        Generate embeddings for a single text.

        Args:
            text: Text to embed

        Returns:
            List of embedding values
        """
        self._ensure_model_loaded()
        assert self.model is not None
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        self._ensure_model_loaded()
        assert self.model is not None
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        self._ensure_model_loaded()
        assert self.model is not None
        return self.model.get_sentence_embedding_dimension()


# Global singleton instance
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """
    Get the global embedding service singleton.

    Returns:
        The global EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
