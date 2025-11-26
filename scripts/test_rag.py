#!/usr/bin/env python3
"""
Test script for RAG pipeline functionality.
Verifies all components can be imported and basic operations work.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all RAG components can be imported."""
    print("Testing imports...")
    try:
        from sages.rag import (
            DocumentProcessor,
            EmbeddingService,
            VectorStore,
            get_vector_store,
        )

        print("✓ All RAG modules import successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_document_processor():
    """Test document processing."""
    print("\nTesting DocumentProcessor...")
    try:
        from sages.rag import DocumentProcessor

        processor = DocumentProcessor()

        # Test text processing
        test_content = b"# Test Document\n\nThis is a test document with some content."
        result = processor.process_file(test_content, "test.md")

        assert result["filename"] == "test.md"
        assert result["extension"] == ".md"
        assert len(result["text"]) > 0

        # Test chunking
        long_text = "This is a test sentence. " * 100
        chunks = processor.chunk_text(long_text, chunk_size=100, overlap=20)
        assert len(chunks) > 1

        print("✓ DocumentProcessor works correctly")
        return True
    except Exception as e:
        print(f"✗ DocumentProcessor test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_api_imports():
    """Test that API endpoints can be imported."""
    print("\nTesting API imports...")
    try:
        from apis.documents import router

        print("✓ Document API router imports successfully")
        return True
    except Exception as e:
        print(f"✗ API import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_knowledge_adapter():
    """Test knowledge adapter imports."""
    print("\nTesting knowledge adapters...")
    try:
        from sages.tools import MockKnowledgeAdapter, RealKnowledgeAdapter

        # Test mock adapter
        mock_adapter = MockKnowledgeAdapter()
        print("✓ MockKnowledgeAdapter created")

        # Test real adapter (without actually using vector store)
        real_adapter = RealKnowledgeAdapter()
        print("✓ RealKnowledgeAdapter created")

        return True
    except Exception as e:
        print(f"✗ Knowledge adapter test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("RAG Pipeline Verification")
    print("=" * 60)
    print()

    tests = [
        test_imports,
        test_document_processor,
        test_api_imports,
        test_knowledge_adapter,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()

    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ All {total} tests passed!")
        print()
        print("RAG pipeline is ready to use.")
        print()
        print("Next steps:")
        print("1. Install dependencies: uv sync")
        print("2. Start server: make run")
        print("3. Upload documents: curl -X POST http://localhost:8000/api/v1/documents/upload ...")
        print("4. See docs/RAG_GUIDE.md for detailed usage")
        return 0
    else:
        print(f"✗ {total - passed}/{total} tests failed")
        print()
        print("Some tests failed. This might be due to missing dependencies.")
        print("Run: uv sync")
        return 1


if __name__ == "__main__":
    sys.exit(main())
