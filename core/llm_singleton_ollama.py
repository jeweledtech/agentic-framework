"""
Enhanced LLM Singleton Manager with Ollama Multi-Model Support
=============================================================

This module extends the existing LLM singleton pattern to support:
- Ollama integration with multiple models
- Model selection based on agent requirements  
- Fallback to existing Llama.cpp implementation
- Thread-safe model management

Phase 4 Enhancement: Foundational AI Engine Upgrade
"""

import os
import threading
from typing import Optional, Any, Dict
from pathlib import Path

# Get the project root directory
PROJECT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Default model configurations - Use ollama/ prefix for litellm compatibility
DEFAULT_MODELS = {
    'general': 'ollama/llama3:8b',           # Fast general-purpose model
    'coding': 'ollama/codellama:34b',        # Specialized coding model
    'analysis': 'ollama/llama3:8b',          # Large model for complex analysis (using 8b since 70b not available)
    'creative': 'ollama/llama3:8b',          # Creative tasks
    'fallback': 'ollama/llama3:8b'           # Fallback model
}

# Model specialization mapping - Use ollama/ prefix for litellm compatibility
MODEL_SPECIALIZATIONS = {
    'coding': ['ollama/codellama:34b', 'ollama/codellama:13b', 'ollama/codellama:7b'],
    'analysis': ['ollama/llama3:8b', 'ollama/mistral:7b'],
    'creative': ['ollama/llama3:8b', 'ollama/mistral:7b'], 
    'general': ['ollama/llama3:8b', 'ollama/mistral:7b']
}

# LLM Configuration
LLM_CONFIG = {
    'temperature': 0.7,
    'top_p': 0.9,
    'context_length': 4096,
    'max_tokens': 512
}

# Environment settings
USE_OLLAMA = os.environ.get('USE_OLLAMA', 'false').lower() == 'true'
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
USE_MOCK_KB = os.environ.get('USE_MOCK_KB', 'false').lower() == 'true'

# Import checks
try:
    from langchain_community.llms import Ollama
    from langchain.llms.base import LLM
    from langchain.callbacks.manager import CallbackManagerForLLMRun
    from pydantic import Field
    OLLAMA_AVAILABLE = True
    LANGCHAIN_AVAILABLE = True
except ImportError:
    try:
        from langchain.llms.base import LLM
        from langchain.callbacks.manager import CallbackManagerForLLMRun
        from pydantic import Field
        OLLAMA_AVAILABLE = False
        LANGCHAIN_AVAILABLE = True
        print("Ollama not available, falling back to existing LLM implementation")
    except ImportError:
        OLLAMA_AVAILABLE = False
        LANGCHAIN_AVAILABLE = False
        print("LangChain not available, using mock implementation")
        
        # Create compatibility classes
        class LLM:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
            
            def _call(self, prompt: str, **kwargs) -> str:
                raise NotImplementedError("LLM not implemented")
            
            def __call__(self, prompt: str, **kwargs) -> str:
                return self._call(prompt, **kwargs)
            
            @property
            def _llm_type(self) -> str:
                return "mock_llm"

        def Field(default=None, **kwargs):
            return default
            
        class CallbackManagerForLLMRun:
            pass


class EnhancedLLMSingleton:
    """Enhanced singleton class to manage multiple LLM models via Ollama"""
    
    _instance = None
    _lock = threading.Lock()
    _models: Dict[str, Any] = {}
    _initialized = False
    _default_model = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EnhancedLLMSingleton, cls).__new__(cls)
        return cls._instance
    
    def get_llm(self, model_name: Optional[str] = None, task_type: Optional[str] = None) -> Any:
        """
        Get an LLM instance, optionally specifying model or task type
        
        Args:
            model_name: Specific model name (e.g., 'codellama:34b')
            task_type: Task type for automatic model selection (e.g., 'coding', 'analysis')
        
        Returns:
            LLM instance
        """
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._initialize_models()
                    self._initialized = True
        
        # Determine which model to use
        target_model = self._select_model(model_name, task_type)
        
        # Return cached model if available
        if target_model in self._models:
            return self._models[target_model]
        
        # Create new model instance
        with self._lock:
            if target_model not in self._models:
                self._models[target_model] = self._create_llm(target_model)
        
        return self._models[target_model]
    
    def _initialize_models(self):
        """Initialize the default model and common models"""
        print("Initializing enhanced LLM singleton with Ollama support...")
        
        # Create default model
        default_model_name = DEFAULT_MODELS['general']
        self._default_model = self._create_llm(default_model_name)
        self._models[default_model_name] = self._default_model
        
        print(f"Default model initialized: {default_model_name}")
    
    def _select_model(self, model_name: Optional[str], task_type: Optional[str]) -> str:
        """Select the appropriate model based on requirements"""
        
        # Explicit model name takes precedence
        if model_name:
            return model_name
        
        # Task type determines model
        if task_type and task_type in DEFAULT_MODELS:
            return DEFAULT_MODELS[task_type]
        
        # Default to general purpose model
        return DEFAULT_MODELS['general']
    
    def _create_llm(self, model_name: str) -> Any:
        """Create an LLM instance for the specified model"""
        
        # Check if we're in mock mode
        if USE_MOCK_KB:
            print(f"Using MOCK LLM for model: {model_name}")
            return MockOllamaLLM(model_name=model_name)
        
        if not LANGCHAIN_AVAILABLE:
            print("Using SIMPLE MOCK LLM (no LangChain available)")
            return MockOllamaLLM(model_name=model_name)
        
        # Try Ollama first if available
        if USE_OLLAMA and OLLAMA_AVAILABLE:
            try:
                print(f"Creating Ollama LLM instance for model: {model_name}")
                return OllamaLangChainLLM(model_name=model_name)
            except Exception as e:
                print(f"Error creating Ollama LLM for {model_name}: {e}")
                print("Falling back to local implementation...")
        
        # Fallback to existing Llama.cpp implementation
        try:
            from core.llm_singleton import LlamaLangChainLLM, LLM_CONFIG as OLD_CONFIG
            print(f"Using local Llama.cpp implementation for {model_name}")
            return LlamaLangChainLLM(**OLD_CONFIG)
        except Exception as e:
            print(f"Error creating local LLM: {e}. Using mock.")
            return MockOllamaLLM(model_name=model_name)
    
    def list_available_models(self) -> Dict[str, str]:
        """List available models and their specializations"""
        return DEFAULT_MODELS.copy()
    
    def reset(self):
        """Reset the singleton for testing purposes"""
        with self._lock:
            self._models.clear()
            self._default_model = None
            self._initialized = False


class MockOllamaLLM(LLM):
    """Mock LLM that simulates Ollama behavior with different models"""
    
    model_name: str = Field(default="llama3:8b")
    
    def __init__(self, model_name: str = "llama3:8b", **kwargs):
        super().__init__(model_name=model_name, **kwargs)
        print(f"Using MOCK Ollama LLM for model: {model_name}")
    
    def _call(self, prompt: str, stop=None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs) -> str:
        """Generate a mock response tailored to the model type"""
        
        # Customize response based on model specialization
        if 'codellama' in self.model_name.lower() or 'code' in self.model_name.lower():
            return self._generate_coding_response(prompt)
        elif '70b' in self.model_name:
            return self._generate_analytical_response(prompt)
        else:
            return self._generate_general_response(prompt)
    
    def _generate_coding_response(self, prompt: str) -> str:
        """Generate coding-focused mock response"""
        return f"""# Code Response from {self.model_name}

Based on your request: "{prompt[:50]}..."

Here's a structured approach:

```python
def solution():
    # Implementation would go here
    pass
```

This solution follows best practices and includes proper error handling."""
    
    def _generate_analytical_response(self, prompt: str) -> str:
        """Generate analytical mock response"""
        return f"""Analysis from {self.model_name}:

Request: "{prompt[:50]}..."

## Key Insights:
1. **Primary consideration**: Comprehensive analysis required
2. **Strategic approach**: Multi-faceted evaluation  
3. **Recommendations**: Data-driven decision making

## Conclusion:
Based on the analysis, the recommended approach involves systematic evaluation of all factors."""
    
    def _generate_general_response(self, prompt: str) -> str:
        """Generate general purpose mock response"""
        return f"""Response from {self.model_name}:

Regarding: "{prompt[:50]}..."

I'll help you with this request. As an AI assistant using the {self.model_name} model, I'll provide accurate and helpful information while following all guidelines."""
    
    @property
    def _llm_type(self) -> str:
        return f"mock_ollama_{self.model_name.replace(':', '_')}"


if OLLAMA_AVAILABLE:
    class OllamaLangChainLLM(LLM):
        """LangChain wrapper for Ollama models"""
        
        model_name: str = Field(default="llama3:8b")
        temperature: float = Field(default=0.7)
        top_p: float = Field(default=0.9)
        max_tokens: int = Field(default=512)
        ollama_client: Optional[Any] = Field(None)
        
        class Config:
            arbitrary_types_allowed = True
        
        def __init__(self, model_name: str = "llama3:8b", **kwargs):
            # Set defaults from config
            kwargs.setdefault('temperature', LLM_CONFIG['temperature'])
            kwargs.setdefault('top_p', LLM_CONFIG['top_p'])
            kwargs.setdefault('max_tokens', LLM_CONFIG['max_tokens'])
            
            super().__init__(model_name=model_name, **kwargs)
            self._init_ollama()
        
        def _init_ollama(self):
            """Initialize Ollama client"""
            try:
                print(f"Initializing Ollama client for model: {self.model_name}")
                # Strip ollama/ prefix if present for actual Ollama calls
                actual_model = self.model_name.replace("ollama/", "") if self.model_name.startswith("ollama/") else self.model_name
                self.ollama_client = Ollama(
                    model=actual_model,
                    base_url=OLLAMA_HOST,
                    temperature=self.temperature,
                    top_p=self.top_p
                )
                print(f"Ollama client initialized successfully for {self.model_name}")
            except Exception as e:
                print(f"Error initializing Ollama client: {e}")
                self.ollama_client = None
                raise
        
        def _call(self, prompt: str, stop=None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs) -> str:
            """Generate text using Ollama"""
            if self.ollama_client is None:
                return f"Error: Ollama client not initialized for {self.model_name}"
            
            try:
                response = self.ollama_client.invoke(
                    prompt,
                    stop=stop,
                    **kwargs
                )
                return response.strip()
            except Exception as e:
                print(f"Error generating response from {self.model_name}: {e}")
                return f"Error generating response: {e}"
        
        @property
        def _llm_type(self) -> str:
            return f"ollama_{self.model_name.replace(':', '_')}"
        
        @property
        def _identifying_params(self) -> dict:
            return {
                "model_name": self.model_name,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_tokens": self.max_tokens,
                "base_url": OLLAMA_HOST
            }


# Global enhanced singleton instance
_enhanced_llm_singleton = EnhancedLLMSingleton()

def get_singleton_llm(model_name: Optional[str] = None, task_type: Optional[str] = None):
    """
    Get the singleton LLM instance with optional model selection
    
    Args:
        model_name: Specific model to use (e.g., 'codellama:34b')
        task_type: Task type for automatic model selection ('coding', 'analysis', etc.)
    
    Returns:
        LLM instance
    """
    return _enhanced_llm_singleton.get_llm(model_name=model_name, task_type=task_type)

def get_coding_llm():
    """Get an LLM optimized for coding tasks"""
    return get_singleton_llm(task_type='coding')

def get_analysis_llm():
    """Get an LLM optimized for analysis tasks"""
    return get_singleton_llm(task_type='analysis')

def get_general_llm():
    """Get a general-purpose LLM"""
    return get_singleton_llm(task_type='general')

# For backward compatibility
def get_langchain_llm():
    """Get a LangChain compatible LLM (singleton)"""
    return get_singleton_llm()

def get_llm():
    """Get a LangChain compatible LLM (singleton)"""
    return get_singleton_llm()

def list_available_models():
    """List available models"""
    return _enhanced_llm_singleton.list_available_models()