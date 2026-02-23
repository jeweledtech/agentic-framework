"""
LLM Provider Interface — Bring Your Own LLM

Abstract base class and built-in implementations for LLM providers.
Users can implement LLMProvider to add any LLM backend (Claude, GPT-4,
Gemini, local models, etc.) and register it with the LLMRegistry.

Built-in providers:
- OllamaProvider: Wraps Ollama/ChatOllama (requires langchain + ollama)
- MockLLMProvider: Returns canned responses for testing
- LiteLLMProvider: Multi-provider routing via LiteLLM (optional)

Configuration:
  LLM_PROVIDER=ollama       (default — auto-detected)
  LLM_PROVIDER=mock         (for testing)
  LLM_PROVIDER=litellm      (for OpenAI/Anthropic/etc. via LiteLLM)
  LLM_PROVIDER=<custom>     (any registered provider name)
"""

import os
import logging
import threading
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract interface for LLM providers. Implement this to bring your own LLM."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM given a prompt."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this provider is currently reachable/usable."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable name for this provider (e.g. 'ollama', 'openai')."""
        ...

    def __call__(self, prompt: str, **kwargs) -> str:
        """Allow providers to be called like functions (backward compat with LangChain LLM)."""
        return self.generate(prompt, **kwargs)


class LLMRegistry:
    """Register and retrieve LLM providers by name.

    Thread-safe singleton registry. Providers are registered by name and
    can be retrieved or auto-detected based on availability.
    """

    _instance: Optional["LLMRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "LLMRegistry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._providers: Dict[str, Type[LLMProvider]] = {}
                    inst._instances: Dict[str, LLMProvider] = {}
                    cls._instance = inst
        return cls._instance

    def register(self, name: str, provider_class: Type[LLMProvider]) -> None:
        """Register a provider class under *name*."""
        self._providers[name] = provider_class

    def get(self, name: Optional[str] = None, **kwargs) -> LLMProvider:
        """Get a provider instance by name, or auto-detect if *name* is None.

        Instances are cached — the same provider name always returns the
        same instance (singleton per name).
        """
        if name is None:
            name = os.environ.get("LLM_PROVIDER", "").lower() or None

        # Auto-detect: try registered providers in priority order
        if name is None:
            name = self._auto_detect()

        if name not in self._providers:
            raise KeyError(
                f"LLM provider '{name}' not registered. "
                f"Available: {self.list_providers()}"
            )

        if name not in self._instances:
            with self._lock:
                if name not in self._instances:
                    self._instances[name] = self._providers[name](**kwargs)

        return self._instances[name]

    def _auto_detect(self) -> str:
        """Try each registered provider and return the first available one."""
        # Priority order for auto-detection
        priority = ["ollama", "anthropic", "openai", "litellm"]
        for name in priority:
            if name in self._providers:
                try:
                    instance = self._providers[name]()
                    if instance.is_available():
                        self._instances[name] = instance
                        logger.info(f"Auto-detected LLM provider: {name}")
                        return name
                except Exception:
                    continue

        # Fallback to mock
        logger.info("No LLM provider detected, falling back to mock")
        return "mock"

    def list_providers(self) -> List[str]:
        """Return names of all registered providers."""
        return list(self._providers.keys())

    def reset(self) -> None:
        """Clear cached instances (useful for testing)."""
        with self._lock:
            self._instances.clear()

    @classmethod
    def reset_singleton(cls) -> None:
        """Reset the singleton entirely (useful for testing)."""
        with cls._lock:
            cls._instance = None


# ---------------------------------------------------------------------------
# Built-in provider implementations
# ---------------------------------------------------------------------------


class OllamaProvider(LLMProvider):
    """LLM provider that wraps Ollama via LangChain's ChatOllama.

    Extracts the existing Ollama logic from llm_singleton.py into a clean
    provider interface.
    """

    def __init__(
        self,
        model: str = "ollama/llama3:8b",
        temperature: float = 0.7,
        base_url: str = "http://localhost:11434",
    ):
        self._model = model
        self._temperature = temperature
        self._base_url = base_url
        self._llm: Any = None  # Lazy init
        self._checked = False
        self._available = False

    @property
    def provider_name(self) -> str:
        return "ollama"

    def is_available(self) -> bool:
        if self._checked:
            return self._available
        try:
            import requests
            resp = requests.get(f"{self._base_url}/api/tags", timeout=5)
            self._available = resp.status_code == 200
        except Exception:
            self._available = False
        self._checked = True
        return self._available

    def _get_llm(self) -> Any:
        if self._llm is None:
            try:
                from langchain_community.llms import Ollama as ChatOllama
                self._llm = ChatOllama(
                    model=self._model,
                    temperature=self._temperature,
                    base_url=self._base_url,
                )
            except ImportError:
                raise ImportError(
                    "Ollama provider requires langchain-community. "
                    "Install with: pip install 'jeweledtech-agentic-framework[ollama]'"
                )
        return self._llm

    def generate(self, prompt: str, **kwargs) -> str:
        llm = self._get_llm()
        return llm(prompt)


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing — returns canned responses."""

    def __init__(self, model_name: str = "mock_model"):
        self._model_name = model_name

    @property
    def provider_name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    def generate(self, prompt: str, **kwargs) -> str:
        return (
            f"Mock {self._model_name} response to: {prompt[:50]}...\n\n"
            "As an AI assistant, I'll help with your request and "
            "ensure to follow all instructions carefully."
        )


class AnthropicProvider(LLMProvider):
    """LLM provider using the Anthropic SDK directly for Claude models.

    Default model: claude-sonnet-4-20250514 (cost-efficient).
    For heritage business deployments requiring highest quality: claude-opus-4-6.
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ):
        self._model = model
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._client: Any = None
        self._checked = False
        self._available = False

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                raise ImportError(
                    "Anthropic provider requires the anthropic package. "
                    "Install with: pip install 'jeweledtech-agentic-framework[anthropic]'"
                )
        return self._client

    def is_available(self) -> bool:
        if self._checked:
            return self._available
        if not self._api_key:
            self._checked = True
            self._available = False
            return False
        try:
            self._get_client()
            self._available = True
        except (ImportError, Exception):
            self._available = False
        self._checked = True
        return self._available

    def generate(self, prompt: str, **kwargs) -> str:
        client = self._get_client()
        response = client.messages.create(
            model=self._model,
            max_tokens=kwargs.get("max_tokens", self._max_tokens),
            temperature=kwargs.get("temperature", self._temperature),
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text


class LiteLLMProvider(LLMProvider):
    """LLM provider that uses LiteLLM for multi-provider routing.

    Supports OpenAI, Anthropic, Google, Azure, and many other backends
    through a single unified interface.
    """

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
    ):
        self._model = model
        self._temperature = temperature

    @property
    def provider_name(self) -> str:
        return "litellm"

    def is_available(self) -> bool:
        try:
            import litellm  # noqa: F401
            return True
        except ImportError:
            return False

    def generate(self, prompt: str, **kwargs) -> str:
        try:
            import litellm
            response = litellm.completion(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._temperature,
                **kwargs,
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError(
                "LiteLLM provider requires litellm. "
                "Install with: pip install 'jeweledtech-agentic-framework[litellm]'"
            )


# ---------------------------------------------------------------------------
# Auto-register built-in providers
# ---------------------------------------------------------------------------

def _register_builtins() -> None:
    registry = LLMRegistry()
    registry.register("ollama", OllamaProvider)
    registry.register("anthropic", AnthropicProvider)
    registry.register("mock", MockLLMProvider)
    registry.register("litellm", LiteLLMProvider)


_register_builtins()
