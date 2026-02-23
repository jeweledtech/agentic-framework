"""Tests for AnthropicProvider — direct Anthropic SDK integration."""
import os
from unittest.mock import MagicMock, patch

import pytest

from core.providers.llm import LLMRegistry


class TestAnthropicProvider:
    """Test the Anthropic/Claude LLM provider."""

    def test_import_provider(self):
        from core.providers.llm import AnthropicProvider
        assert AnthropicProvider is not None

    def test_provider_name(self):
        from core.providers.llm import AnthropicProvider
        provider = AnthropicProvider.__new__(AnthropicProvider)
        provider._model = "claude-sonnet-4-20250514"
        provider._api_key = "test-key"
        provider._client = None
        provider._checked = False
        provider._available = False
        assert provider.provider_name == "anthropic"

    def test_default_model(self):
        from core.providers.llm import AnthropicProvider
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            provider = AnthropicProvider()
        assert provider._model == "claude-sonnet-4-20250514"

    def test_custom_model(self):
        from core.providers.llm import AnthropicProvider
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            provider = AnthropicProvider(model="claude-opus-4-6")
        assert provider._model == "claude-opus-4-6"

    def test_api_key_from_env(self):
        from core.providers.llm import AnthropicProvider
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-123"}):
            provider = AnthropicProvider()
        assert provider._api_key == "sk-test-123"

    def test_api_key_from_param(self):
        from core.providers.llm import AnthropicProvider
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key"}):
            provider = AnthropicProvider(api_key="param-key")
        assert provider._api_key == "param-key"

    def test_not_available_without_package(self):
        from core.providers.llm import AnthropicProvider
        provider = AnthropicProvider.__new__(AnthropicProvider)
        provider._model = "claude-sonnet-4-20250514"
        provider._api_key = "test-key"
        provider._client = None
        provider._checked = False
        provider._available = False
        with patch.dict("sys.modules", {"anthropic": None}):
            assert provider.is_available() is False

    def test_not_available_without_api_key(self):
        from core.providers.llm import AnthropicProvider
        provider = AnthropicProvider.__new__(AnthropicProvider)
        provider._model = "claude-sonnet-4-20250514"
        provider._api_key = None
        provider._client = None
        provider._checked = False
        provider._available = False
        assert provider.is_available() is False

    @patch("core.providers.llm.AnthropicProvider._get_client")
    def test_generate_calls_messages_create(self, mock_get_client):
        from core.providers.llm import AnthropicProvider
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello from Claude")]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            provider = AnthropicProvider()
        provider._client = mock_client
        result = provider.generate("What is 2+2?")
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-sonnet-4-20250514"
        assert call_kwargs["messages"] == [{"role": "user", "content": "What is 2+2?"}]
        assert result == "Hello from Claude"

    def test_callable_interface(self):
        from core.providers.llm import AnthropicProvider
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            provider = AnthropicProvider()
        with patch.object(provider, "generate", return_value="test"):
            assert provider("hello") == "test"

    def test_registry_detection(self):
        registry = LLMRegistry()
        provider = registry.get("anthropic")
        assert provider.provider_name == "anthropic"
