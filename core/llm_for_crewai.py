import os
from typing import Dict, List, Any, Optional
from pathlib import Path

# Get the project root directory
PROJECT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define the model path
MODEL_PATH = os.environ.get('MODEL_PATH', 
                           str(PROJECT_DIR / 'models' / 'Llama-3.2-3B-Instruct' / 'Llama-3.2-3B-Instruct-Q4_K_M.gguf'))

# LLM Configuration
LLM_CONFIG = {
    'model_path': MODEL_PATH,
    'context_length': 4096,
    'temperature': 0.7,
    'top_p': 0.9,
}

# Check if we're in mock mode
USE_MOCK_KB = os.environ.get('USE_MOCK_KB', 'false').lower() == 'true'

# Check if LangChain is available, if not, create a simple base class
try:
    from langchain.llms.base import LLM
    from langchain.callbacks.manager import CallbackManagerForLLMRun
    from pydantic import Field
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain not available, using mock implementation")
    # Create a simple base class to mimic LangChain's LLM
    class LLM:
        """Simple base class for LLM when LangChain is not available"""
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

    # Create a simple Field function to mimic Pydantic's Field
    def Field(default=None, **kwargs):
        return default
        
    # Create a simple CallbackManagerForLLMRun class
    class CallbackManagerForLLMRun:
        pass

class SimpleMockLLM(LLM):
    """Simple mock LLM for development and testing"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Using SIMPLE MOCK LLM for CrewAI (no actual model or LangChain)")
    
    def _call(self, prompt: str, **kwargs) -> str:
        """Generate a mock response"""
        return f"Mock CrewAI LLM response to: {prompt[:50]}...\n\nAs an AI assistant, I'll help with your request and ensure to follow all instructions carefully."
    
    @property
    def _llm_type(self) -> str:
        """Return the type of LLM"""
        return "simple_mock_llm"

if LANGCHAIN_AVAILABLE:
    class LlamaLangChainLLM(LLM):
        """LangChain wrapper for Llama model"""
        
        model_path: str = Field(default="")
        context_length: int = Field(default=4096)
        temperature: float = Field(default=0.7)
        top_p: float = Field(default=0.9)
        model: Optional[Any] = Field(None)
        use_mock: bool = Field(False)
        llama_model: Optional[Any] = Field(None)
        
        class Config:
            arbitrary_types_allowed = True
        
        def __init__(self, model_path=None, use_mock=None, **kwargs):
            # Set defaults from config
            if model_path is None:
                model_path = LLM_CONFIG['model_path']
            if use_mock is None:
                use_mock = USE_MOCK_KB
            
            # Set other defaults from config if not provided
            kwargs.setdefault('context_length', LLM_CONFIG['context_length'])
            kwargs.setdefault('temperature', LLM_CONFIG['temperature'])
            kwargs.setdefault('top_p', LLM_CONFIG['top_p'])
            
            super().__init__(model_path=model_path, use_mock=use_mock, **kwargs)
            self._init_model()
        
        def _init_model(self):
            """Initialize the model"""
            if self.use_mock:
                print("Using MOCK LLM for CrewAI (no actual model loaded)")
                self.llama_model = None
                return
                
            try:
                print(f"Loading model from: {self.model_path}")
                # Import llama_cpp only if not in mock mode
                from llama_cpp import Llama
                
                self.llama_model = Llama(
                    model_path=self.model_path,
                    n_ctx=self.context_length,
                    temperature=self.temperature,
                    top_p=self.top_p,
                )
                print("Model loaded successfully!")
            except Exception as e:
                print(f"Error loading model: {e}")
                # In case of error, use a mock implementation for testing
                print("Using mock model implementation for testing")
                self.llama_model = None
                self.use_mock = True
        
        def _call(self, prompt: str, stop=None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs) -> str:
            """Generate text using the model"""
            if self.llama_model is None or self.use_mock:
                # Mock response for testing
                return f"Mock CrewAI LLM response to: {prompt[:50]}...\n\nAs an AI assistant, I'll help with your request and ensure to follow all instructions carefully."
            
            try:
                if hasattr(self.llama_model, 'create_completion'):
                    response = self.llama_model.create_completion(
                        prompt=prompt, 
                        stop=stop or [],
                        max_tokens=512,  # Increase token limit for longer responses
                        temperature=self.temperature,
                        top_p=self.top_p
                    )
                    return response["choices"][0]["text"].strip()
                else:
                    # Fallback to mock for testing
                    print("Model doesn't have create_completion method, using mock response")
                    return f"Mock response to: {prompt[:50]}..."
            except Exception as e:
                print(f"Error generating response: {e}")
                return f"Error generating response: {e}"
        
        @property
        def _llm_type(self) -> str:
            """Return the type of LLM"""
            return "llama_cpp" if not self.use_mock else "mock_llm"
        
        @property
        def _identifying_params(self) -> Dict[str, Any]:
            """Get the identifying parameters."""
            return {
                "model_path": self.model_path,
                "context_length": self.context_length,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "use_mock": self.use_mock,
            }
        
        def supports_stop_words(self) -> bool:
            """Return whether this model supports stop words."""
            return True
        
        @property 
        def model_name(self) -> str:
            """Return the model name for identification."""
            return self._llm_type
        
        def get_num_tokens(self, text: str) -> int:
            """Return the number of tokens in the text."""
            # Simple approximation - this could be improved with actual tokenization
            return len(text.split())
        
        def get_token_ids(self, text: str):
            """Return token IDs for the text."""
            # Not implemented for this model
            return None
        
        def lower(self):
            """Return lowercase model type for compatibility with CrewAI."""
            return self._llm_type.lower()
        
        def __getattr__(self, name):
            """Handle missing attributes for CrewAI compatibility."""
            if name == 'lower':
                return lambda: self._llm_type.lower()
            elif name == 'supports_stop_words':
                return True
            elif hasattr(self.llama_model, name) and self.llama_model is not None:
                # Delegate to the underlying model if it has the attribute
                return getattr(self.llama_model, name)
            else:
                # Provide a sensible default for missing attributes
                if name in ['temperature', 'top_p', 'max_tokens']:
                    return getattr(self, name, 0.7)
                elif name in ['model_name', 'model_type']:
                    return self._llm_type
                else:
                    raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

# Factory function to get a LangChain compatible LLM
def get_langchain_llm():
    """Get a LangChain compatible LLM"""
    if LANGCHAIN_AVAILABLE and not USE_MOCK_KB:
        return LlamaLangChainLLM(use_mock=USE_MOCK_KB)
    else:
        # Return simple mock implementation when LangChain isn't available or in mock mode
        return SimpleMockLLM()

# For backward compatibility
def get_llm():
    """Get a LangChain compatible LLM"""
    return get_langchain_llm()