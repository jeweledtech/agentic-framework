"""
Shared test fixtures for the JeweledTech Agentic Framework test suite.

All tests run in mock mode (USE_MOCK_KB=true) so no real LLM, vector store,
or external service is needed.
"""

import os
import sys

# Ensure mock mode is set before any framework imports
os.environ["USE_MOCK_KB"] = "true"
os.environ.setdefault("ENABLE_AUTH", "false")

import pytest

from core.agent import AgentConfig, AgentRole, AgentTools, BaseAgent
from core.providers.llm import LLMRegistry, MockLLMProvider
from core.providers.vectorstore import VectorStoreRegistry
from core.providers.workflow import WorkflowRegistry
from core.audit import AuditLogger


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Ensure mock mode is active for every test."""
    monkeypatch.setenv("USE_MOCK_KB", "true")
    monkeypatch.setenv("ENABLE_AUTH", "false")


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset all singleton registries between tests to prevent state leakage."""
    yield
    LLMRegistry.reset_singleton()
    VectorStoreRegistry.reset_singleton()
    WorkflowRegistry.reset_singleton()
    AuditLogger.reset_singleton()

    # Re-register built-in providers for the next test
    from core.providers.llm import _register_builtins as llm_register
    from core.providers.vectorstore import _register_builtins as vs_register
    from core.providers.workflow import _register_builtins as wf_register
    llm_register()
    vs_register()
    wf_register()


@pytest.fixture
def auth_env(monkeypatch):
    """Enable auth with a test API key."""
    monkeypatch.setenv("ENABLE_AUTH", "true")
    monkeypatch.setenv("FRAMEWORK_API_KEY", "test-api-key-12345")


@pytest.fixture
def sample_role():
    """A reusable AgentRole fixture."""
    return AgentRole(
        name="Test Agent",
        description="A test agent for unit testing",
        goal="Test the framework",
        backstory="Created for automated testing",
    )


@pytest.fixture
def sample_tools():
    """A reusable AgentTools fixture."""
    return AgentTools(tool_names=["web_search_tool"])


@pytest.fixture
def sample_agent_config(sample_role, sample_tools):
    """A reusable AgentConfig fixture."""
    return AgentConfig(
        id="test_agent",
        role=sample_role,
        tools=sample_tools,
        department="sales",
        temperature=0.7,
        verbose=False,
    )


@pytest.fixture
def sample_agent(sample_agent_config):
    """A reusable BaseAgent instance (mock mode)."""
    return BaseAgent(sample_agent_config)


@pytest.fixture
def api_client():
    """FastAPI TestClient for API tests."""
    from fastapi.testclient import TestClient
    from api_server import app

    return TestClient(app)
