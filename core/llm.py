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

class MockLlamaModel:
    """Mock implementation of the Llama model for testing without the actual model"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the mock model"""
        if config is None:
            config = LLM_CONFIG
        
        self.config = config
        print("Using MOCK LLM model (no actual model loaded)")
    
    def generate(self, 
                 system_prompt: str, 
                 user_prompt: str, 
                 chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate a mock response"""
        if chat_history is None:
            chat_history = []
        
        # For demo purposes, return a simplified response
        # In a real application, you might want more sophisticated mock responses
        return f"Mock LLM Response: I received your prompt about '{user_prompt[:30]}...' and I'm responding as a helpful assistant."


class LlamaModel:
    """Wrapper for Llama 3 model integration using llama-cpp-python"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Llama model with configuration"""
        if config is None:
            config = LLM_CONFIG
        
        self.config = config
        self.model = self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the model with the configured parameters"""
        try:
            # Check if model file exists
            if not os.path.exists(self.config['model_path']):
                raise FileNotFoundError(f"Model file not found at {self.config['model_path']}")
            
            print(f"Loading model from: {self.config['model_path']}")
            
            # Import here to allow mock mode to work without the dependency
            from llama_cpp import Llama
            
            # Set up LLM with llama-cpp-python (for GGUF files)
            model = Llama(
                model_path=self.config['model_path'],
                n_ctx=self.config.get('context_length', 4096),
                temperature=self.config.get('temperature', 0.7),
            )
            
            return model
            
        except Exception as e:
            print(f"Error initializing Llama model: {e}")
            raise
    
    def generate(self, 
                 system_prompt: str, 
                 user_prompt: str, 
                 chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate a response based on the system prompt, user prompt and chat history"""
        if chat_history is None:
            chat_history = []
        
        # Format messages for the Llama chat format
        messages = []
        
        # Add system message
        messages.append({"role": "system", "content": system_prompt})
        
        # Add chat history if available
        if chat_history:
            for msg in chat_history:
                messages.append(msg)
        
        # Add user message
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            response = self.model.create_chat_completion(
                messages=messages,
                temperature=self.config.get('temperature', 0.7),
                top_p=self.config.get('top_p', 0.9)
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while generating a response."


# Singleton instance
llm_instance = None

def get_llm():
    """Get or create the LLM instance"""
    global llm_instance
    if llm_instance is None:
        if USE_MOCK_KB:
            llm_instance = MockLlamaModel()
        else:
            llm_instance = LlamaModel()
    return llm_instance