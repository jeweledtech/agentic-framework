"""Unit tests for LLM, VectorStore, and Workflow provider interfaces."""

import pytest
from core.providers.llm import (
    LLMProvider,
    LLMRegistry,
    MockLLMProvider,
    OllamaProvider,
    LiteLLMProvider,
)
from core.providers.vectorstore import (
    VectorStoreProvider,
    VectorStoreRegistry,
    MockVectorStoreProvider,
    FileSystemVectorStoreProvider,
    ChromaDBProvider,
)
from core.providers.workflow import (
    WorkflowProvider,
    WorkflowRegistry,
    MockWorkflowProvider,
    N8NProvider,
)


# ---- LLM Provider Tests ----

class TestLLMRegistry:
    def test_registry_singleton(self):
        r1 = LLMRegistry()
        r2 = LLMRegistry()
        assert r1 is r2

    def test_list_builtin_providers(self):
        registry = LLMRegistry()
        providers = registry.list_providers()
        assert "ollama" in providers
        assert "mock" in providers
        assert "litellm" in providers

    def test_get_mock_provider(self):
        registry = LLMRegistry()
        provider = registry.get("mock")
        assert isinstance(provider, MockLLMProvider)

    def test_register_custom_provider(self):
        class CustomProvider(LLMProvider):
            @property
            def provider_name(self):
                return "custom"
            def generate(self, prompt, **kwargs):
                return "custom response"
            def is_available(self):
                return True

        registry = LLMRegistry()
        registry.register("custom_test", CustomProvider)
        assert "custom_test" in registry.list_providers()

        provider = registry.get("custom_test")
        assert provider.generate("hello") == "custom response"

    def test_get_nonexistent_provider_raises(self):
        registry = LLMRegistry()
        with pytest.raises(KeyError, match="not registered"):
            registry.get("nonexistent_provider_xyz")

    def test_auto_detect_falls_back_to_mock(self):
        registry = LLMRegistry()
        # With no Ollama running, auto-detect should fall back to mock
        provider = registry.get()
        assert provider is not None

    def test_registry_reset(self):
        registry = LLMRegistry()
        registry.get("mock")
        registry.reset()
        # After reset, instances are cleared but providers remain
        assert "mock" in registry.list_providers()


class TestMockLLMProvider:
    def test_generate(self):
        provider = MockLLMProvider()
        response = provider.generate("Hello world")
        assert isinstance(response, str)
        assert "Mock" in response

    def test_is_available(self):
        assert MockLLMProvider().is_available() is True

    def test_provider_name(self):
        assert MockLLMProvider().provider_name == "mock"

    def test_callable(self):
        provider = MockLLMProvider()
        response = provider("test prompt")
        assert isinstance(response, str)

    def test_custom_model_name(self):
        provider = MockLLMProvider(model_name="gpt-custom")
        response = provider.generate("test")
        assert "gpt-custom" in response


class TestOllamaProvider:
    def test_provider_name(self):
        provider = OllamaProvider()
        assert provider.provider_name == "ollama"

    def test_is_not_available_when_not_running(self):
        # Ollama is not running in test environment
        provider = OllamaProvider(base_url="http://localhost:99999")
        assert provider.is_available() is False


class TestLiteLLMProvider:
    def test_provider_name(self):
        provider = LiteLLMProvider()
        assert provider.provider_name == "litellm"


# ---- VectorStore Provider Tests ----

class TestVectorStoreRegistry:
    def test_list_providers(self):
        registry = VectorStoreRegistry()
        providers = registry.list_providers()
        assert "chromadb" in providers
        assert "filesystem" in providers
        assert "mock" in providers

    def test_get_mock_provider(self):
        registry = VectorStoreRegistry()
        provider = registry.get("mock")
        assert isinstance(provider, MockVectorStoreProvider)

    def test_register_custom_vectorstore(self):
        class CustomVS(VectorStoreProvider):
            @property
            def provider_name(self):
                return "custom_vs"
            def search(self, query, top_k=5, **kwargs):
                return [{"content": "custom", "metadata": {}}]
            def add_documents(self, documents):
                pass
            def is_available(self):
                return True

        registry = VectorStoreRegistry()
        registry.register("custom_vs_test", CustomVS)
        provider = registry.get("custom_vs_test")
        results = provider.search("test")
        assert len(results) == 1
        assert results[0]["content"] == "custom"


class TestMockVectorStoreProvider:
    def test_search(self):
        provider = MockVectorStoreProvider()
        results = provider.search("test query")
        assert isinstance(results, list)
        assert len(results) > 0
        assert "content" in results[0]

    def test_add_documents(self):
        provider = MockVectorStoreProvider()
        provider.add_documents([{"content": "doc1", "metadata": {"src": "test"}}])
        assert len(provider._documents) == 1

    def test_is_available(self):
        assert MockVectorStoreProvider().is_available() is True


class TestFileSystemVectorStoreProvider:
    def test_search(self):
        provider = FileSystemVectorStoreProvider(department="sales")
        results = provider.search("icp")
        assert isinstance(results, list)

    def test_is_available(self):
        assert FileSystemVectorStoreProvider().is_available() is True

    def test_provider_name(self):
        assert FileSystemVectorStoreProvider().provider_name == "filesystem"


# ---- Workflow Provider Tests ----

class TestWorkflowRegistry:
    def test_list_providers(self):
        registry = WorkflowRegistry()
        providers = registry.list_providers()
        assert "n8n" in providers
        assert "mock" in providers

    def test_get_mock_provider(self):
        registry = WorkflowRegistry()
        provider = registry.get("mock")
        assert isinstance(provider, MockWorkflowProvider)


class TestMockWorkflowProvider:
    def test_trigger_workflow(self):
        provider = MockWorkflowProvider()
        result = provider.trigger_workflow("wf-001", {"data": "test"})
        assert result["status"] == "completed"
        assert result["workflow_id"] == "wf-001"

    def test_list_workflows(self):
        provider = MockWorkflowProvider()
        workflows = provider.list_workflows()
        assert isinstance(workflows, list)
        assert len(workflows) == 2

    def test_is_available(self):
        assert MockWorkflowProvider().is_available() is True

    def test_triggered_history(self):
        provider = MockWorkflowProvider()
        provider.trigger_workflow("wf-1", {})
        provider.trigger_workflow("wf-2", {})
        assert len(provider._triggered) == 2


class TestN8NProvider:
    def test_provider_name(self):
        provider = N8NProvider()
        assert provider.provider_name == "n8n"

    def test_is_not_available_when_not_running(self):
        provider = N8NProvider(mcp_url="http://localhost:99999/mcp")
        assert provider.is_available() is False


# ---- End-to-end BYO test ----

class TestBringYourOwn:
    def test_custom_llm_through_agent(self):
        """Prove the bring-your-own pattern works end-to-end."""
        from core.agent import BaseAgent, AgentConfig, AgentRole, AgentTools

        class MyLLMProvider(LLMProvider):
            @property
            def provider_name(self):
                return "my_custom"
            def generate(self, prompt, **kwargs):
                return "CUSTOM LLM RESPONSE"
            def is_available(self):
                return True

        config = AgentConfig(
            id="byo_agent",
            role=AgentRole(
                name="BYO Agent",
                description="Tests BYO pattern",
                goal="Validate custom provider",
                backstory="Test agent",
            ),
        )
        agent = BaseAgent(config, llm_provider=MyLLMProvider())
        response = agent.direct_query("test")
        assert "CUSTOM LLM RESPONSE" in response

    def test_custom_llm_via_registry(self):
        """Register a custom provider and retrieve it by name."""
        class RegistryTestProvider(LLMProvider):
            @property
            def provider_name(self):
                return "registry_test"
            def generate(self, prompt, **kwargs):
                return "REGISTRY RESPONSE"
            def is_available(self):
                return True

        registry = LLMRegistry()
        registry.register("registry_test", RegistryTestProvider)
        provider = registry.get("registry_test")
        assert provider.generate("hello") == "REGISTRY RESPONSE"
