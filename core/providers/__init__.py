"""
Provider interfaces for the JeweledTech Agentic Framework.

Bring-your-own-anything: LLM, vector store, and workflow engine providers
can be swapped via environment variables or programmatic registration.
"""

from core.providers.llm import (
    LLMProvider,
    LLMRegistry,
    OllamaProvider,
    MockLLMProvider,
    LiteLLMProvider,
)
from core.providers.vectorstore import (
    VectorStoreProvider,
    VectorStoreRegistry,
    ChromaDBProvider,
    FileSystemVectorStoreProvider,
    MockVectorStoreProvider,
)
from core.providers.workflow import (
    WorkflowProvider,
    WorkflowRegistry,
    N8NProvider,
    MockWorkflowProvider,
)

__all__ = [
    # LLM
    "LLMProvider",
    "LLMRegistry",
    "OllamaProvider",
    "MockLLMProvider",
    "LiteLLMProvider",
    # Vector Store
    "VectorStoreProvider",
    "VectorStoreRegistry",
    "ChromaDBProvider",
    "FileSystemVectorStoreProvider",
    "MockVectorStoreProvider",
    # Workflow
    "WorkflowProvider",
    "WorkflowRegistry",
    "N8NProvider",
    "MockWorkflowProvider",
]
