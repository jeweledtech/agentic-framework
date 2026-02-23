"""Tests for OpenAIProvider — direct OpenAI SDK integration."""
import os
from unittest.mock import MagicMock, patch

import pytest

from core.providers.llm import LLMRegistry


class TestOpenAIProvider:
    """Test the OpenAI LLM provider."""

    def test_import_provider(self):
        """OpenAIProvider should be importable from providers module."""
        from core.providers.llm import OpenAIProvider
        assert OpenAIProvider is not None

    def test_provider_name(self):
        """Provider name should be 'openai'."""
        from core.providers.llm import OpenAIProvider
        provider = OpenAIProvider.__new__(OpenAIProvider)
        provider._model = "gpt-4o"
        provider._api_key = "test-key"
        provider._client = None
        provider._checked = False
        provider._available = False
        assert provider.provider_name == "openai"

    def test_default_model(self):
        """Default model should be gpt-4o."""
        from core.providers.llm import OpenAIProvider
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()
        assert provider._model == "gpt-4o"

    def test_api_key_from_env(self):
        """Should read API key from OPENAI_API_KEY env var."""
        from core.providers.llm import OpenAIProvider
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-456"}):
            provider = OpenAIProvider()
        assert provider._api_key == "sk-test-456"

    def test_api_key_from_param(self):
        """Explicit api_key param should override env var."""
        from core.providers.llm import OpenAIProvider
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            provider = OpenAIProvider(api_key="param-key")
        assert provider._api_key == "param-key"

    def test_not_available_without_api_key(self):
        """Should return False if no API key configured."""
        from core.providers.llm import OpenAIProvider
        provider = OpenAIProvider.__new__(OpenAIProvider)
        provider._model = "gpt-4o"
        provider._api_key = None
        provider._client = None
        provider._checked = False
        provider._available = False
        assert provider.is_available() is False

    @patch("core.providers.llm.OpenAIProvider._get_client")
    def test_generate_calls_chat_completions(self, mock_get_client):
        """generate() should call client.chat.completions.create."""
        from core.providers.llm import OpenAIProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello from GPT"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()
        provider._client = mock_client

        result = provider.generate("What is 2+2?")

        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "gpt-4o"
        assert result == "Hello from GPT"

    def test_callable_interface(self):
        """Provider should be callable (backward compat)."""
        from core.providers.llm import OpenAIProvider
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()
        with patch.object(provider, "generate", return_value="test"):
            assert provider("hello") == "test"

    def test_registry_detection(self):
        """OpenAIProvider should be discoverable via LLMRegistry."""
        registry = LLMRegistry()
        provider = registry.get("openai")
        assert provider.provider_name == "openai"
