"""
Document processor for extracting text from various file formats.
"""

import io
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Process documents and extract text content.
    Supports: TXT, MD, PDF, DOCX
    """

    def __init__(self) -> None:
        """Initialize the document processor."""
        self.supported_extensions = {".txt", ".md", ".pdf", ".docx", ".json"}

    def process_file(self, file_content: bytes, filename: str) -> dict[str, Any]:
        """
        Process a file and extract its text content.

        Args:
            file_content: Raw file bytes
            filename: Name of the file (used to determine format)

        Returns:
            Dictionary with processed document data

        Raises:
            ValueError: If file format is not supported
        """
        extension = Path(filename).suffix.lower()

        if extension not in self.supported_extensions:
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported: {', '.join(self.supported_extensions)}"
            )

        # Extract text based on file type
        if extension == ".txt":
            text = self._process_txt(file_content)
        elif extension == ".md":
            text = self._process_markdown(file_content)
        elif extension == ".pdf":
            text = self._process_pdf(file_content)
        elif extension == ".docx":
            text = self._process_docx(file_content)
        elif extension == ".json":
            text = self._process_json(file_content)
        else:
            text = file_content.decode("utf-8", errors="ignore")

        return {
            "filename": filename,
            "extension": extension,
            "text": text,
            "char_count": len(text),
            "word_count": len(text.split()),
        }

    def _process_txt(self, content: bytes) -> str:
        """Process plain text file."""
        return content.decode("utf-8", errors="ignore")

    def _process_markdown(self, content: bytes) -> str:
        """Process markdown file."""
        import markdown

        md_text = content.decode("utf-8", errors="ignore")
        # Convert markdown to HTML then strip tags for plain text
        html = markdown.markdown(md_text)
        # Simple tag stripping (for more complex needs, use BeautifulSoup)
        import re

        text = re.sub("<[^<]+?>", "", html)
        return text

    def _process_pdf(self, content: bytes) -> str:
        """Process PDF file."""
        from pypdf import PdfReader

        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)

        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        return "\n\n".join(text_parts)

    def _process_docx(self, content: bytes) -> str:
        """Process DOCX file."""
        from docx import Document

        docx_file = io.BytesIO(content)
        doc = Document(docx_file)

        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)

        return "\n\n".join(text_parts)

    def _process_json(self, content: bytes) -> str:
        """Process JSON file."""
        import json

        data = json.loads(content.decode("utf-8"))
        # Convert JSON to readable text format
        return json.dumps(data, indent=2)

    def chunk_text(
        self, text: str, chunk_size: int = 1000, overlap: int = 200
    ) -> list[str]:
        """
        Split text into overlapping chunks for better retrieval.

        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(".")
                last_newline = chunk.rfind("\n")
                break_point = max(last_period, last_newline)

                if break_point > chunk_size // 2:
                    chunk = chunk[: break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks
