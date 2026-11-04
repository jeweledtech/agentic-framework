"""
Vector Store Provider Interface — Bring Your Own Vector Store

Abstract base class and built-in implementations for vector store providers.
Users can implement VectorStoreProvider to add Pinecone, Weaviate, Qdrant,
or any other vector database.

Built-in providers:
- ChromaDBProvider: Wraps current ChromaDB logic (requires chromadb)
- FileSystemVectorStoreProvider: Keyword search over file-system knowledge bases
- MockVectorStoreProvider: Returns canned results for testing

Configuration:
  VECTORSTORE_PROVIDER=chromadb       (requires chromadb package)
  VECTORSTORE_PROVIDER=filesystem     (default — uses kb_interface)
  VECTORSTORE_PROVIDER=mock           (for testing)
  VECTORSTORE_PROVIDER=<custom>       (any registered provider name)
"""

import os
import logging
import threading
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class VectorStoreProvider(ABC):
    """Abstract interface for vector stores. Implement this to bring your own."""

    @abstractmethod
    def search(self, query: str, top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search for documents matching *query*. Returns list of result dicts."""
        ...

    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the vector store.

        Each document dict should have at least 'content' and optional 'metadata'.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this provider is currently reachable/usable."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable name for this provider."""
        ...


class VectorStoreRegistry:
    """Register and retrieve vector store providers by name."""

    _instance: Optional["VectorStoreRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "VectorStoreRegistry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._providers: Dict[str, Type[VectorStoreProvider]] = {}
                    inst._instances: Dict[str, VectorStoreProvider] = {}
                    cls._instance = inst
        return cls._instance

    def register(self, name: str, provider_class: Type[VectorStoreProvider]) -> None:
        self._providers[name] = provider_class

    def get(self, name: Optional[str] = None, **kwargs) -> VectorStoreProvider:
        if name is None:
            name = os.environ.get("VECTORSTORE_PROVIDER", "").lower() or "filesystem"

        if name not in self._providers:
            raise KeyError(
                f"Vector store provider '{name}' not registered. "
                f"Available: {self.list_providers()}"
            )

        if name not in self._instances:
            with self._lock:
                if name not in self._instances:
                    self._instances[name] = self._providers[name](**kwargs)

        return self._instances[name]

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())

    def reset(self) -> None:
        with self._lock:
            self._instances.clear()

    @classmethod
    def reset_singleton(cls) -> None:
        with cls._lock:
            cls._instance = None


# ---------------------------------------------------------------------------
# Built-in provider implementations
# ---------------------------------------------------------------------------


class ChromaDBProvider(VectorStoreProvider):
    """Vector store provider backed by ChromaDB."""

    def __init__(
        self,
        vectorstore_path: str = "vectorstore",
        collection_name: str = "knowledge_base",
        department_filter: Optional[str] = None,
    ):
        self._vectorstore_path = vectorstore_path
        self._collection_name = collection_name
        self._department_filter = department_filter

    @property
    def provider_name(self) -> str:
        return "chromadb"

    def is_available(self) -> bool:
        try:
            import chromadb  # noqa: F401
            return True
        except ImportError:
            return False

    def search(self, query: str, top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        try:
            import chromadb
            from chromadb.utils.embedding_functions import (
                SentenceTransformerEmbeddingFunction,
            )
        except ImportError:
            raise ImportError(
                "ChromaDB provider requires chromadb. "
                "Install with: pip install 'jeweledtech-agentic-framework[chromadb]'"
            )

        client = chromadb.PersistentClient(path=self._vectorstore_path)
        collection = client.get_collection(
            name=self._collection_name,
            embedding_function=SentenceTransformerEmbeddingFunction(
                model_name="nomic-ai/nomic-embed-text-v1.5",
                trust_remote_code=True,
            ),
        )

        dept = kwargs.get("department_filter", self._department_filter)
        where_filter = {"department": dept} if dept else None

        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
        )

        docs = []
        if results["documents"] and results["documents"][0]:
            documents = results["documents"][0]
            metadatas = (
                results["metadatas"][0] if results["metadatas"] else [{}] * len(documents)
            )
            for doc, meta in zip(documents, metadatas):
                docs.append({"content": doc, "metadata": meta})

        return docs

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        try:
            import chromadb
            from chromadb.utils.embedding_functions import (
                SentenceTransformerEmbeddingFunction,
            )
        except ImportError:
            raise ImportError(
                "ChromaDB provider requires chromadb. "
                "Install with: pip install 'jeweledtech-agentic-framework[chromadb]'"
            )

        client = chromadb.PersistentClient(path=self._vectorstore_path)
        collection = client.get_or_create_collection(
            name=self._collection_name,
            embedding_function=SentenceTransformerEmbeddingFunction(
                model_name="nomic-ai/nomic-embed-text-v1.5",
                trust_remote_code=True,
            ),
        )

        ids = []
        texts = []
        metadatas = []
        for i, doc in enumerate(documents):
            ids.append(doc.get("id", f"doc_{i}"))
            texts.append(doc["content"])
            metadatas.append(doc.get("metadata", {}))

        collection.add(ids=ids, documents=texts, metadatas=metadatas)


class FileSystemVectorStoreProvider(VectorStoreProvider):
    """Vector store backed by file-system keyword search.

    Wraps the existing KnowledgeBaseInterface for simple text-based search
    over the knowledge_bases/ directory.
    """

    def __init__(self, department: str = "sales"):
        self._department = department

    @property
    def provider_name(self) -> str:
        return "filesystem"

    def is_available(self) -> bool:
        return True

    def search(self, query: str, top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        from knowledge_bases.kb_interface import get_kb_interface

        dept = kwargs.get("department", self._department)
        kb = get_kb_interface(dept)
        raw_results = kb.search_knowledge_base(query)

        docs = []
        for category, items in raw_results.items():
            for item in items:
                docs.append({
                    "content": item.get("snippet", ""),
                    "metadata": {
                        "category": category,
                        "document": item.get("document", ""),
                        "department": dept,
                    },
                })
                if len(docs) >= top_k:
                    return docs

        return docs

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        logger.warning(
            "FileSystemVectorStoreProvider.add_documents is a no-op. "
            "Add files directly to the knowledge_bases/ directory."
        )


class MockVectorStoreProvider(VectorStoreProvider):
    """Mock vector store for testing."""

    def __init__(self):
        self._documents: List[Dict[str, Any]] = []

    @property
    def provider_name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    def search(self, query: str, top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        return [
            {
                "content": f"Mock result for query: '{query}'",
                "metadata": {"source": "mock", "score": 0.95},
            }
        ]

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        self._documents.extend(documents)


# ---------------------------------------------------------------------------
# Auto-register built-in providers
# ---------------------------------------------------------------------------

def _register_builtins() -> None:
    registry = VectorStoreRegistry()
    registry.register("chromadb", ChromaDBProvider)
    registry.register("filesystem", FileSystemVectorStoreProvider)
    registry.register("mock", MockVectorStoreProvider)


_register_builtins()
