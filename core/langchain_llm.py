import os
from typing import Any, List, Mapping, Optional
from pathlib import Path
from llama_cpp import Llama
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from pydantic import Field

# Get the project root directory
PROJECT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define the model path
MODEL_PATH = os.environ.get('MODEL_PATH', 
                           str(PROJECT_DIR / 'models' / 'Llama-3.2-3B-Instruct' / 'Llama-3.2-3B-Instruct-Q4_K_M.gguf'))

class CustomLLM(LLM):
    """LangChain wrapper for our LLM"""
    
    model_path: str = Field(...)
    context_length: int = Field(4096)
    temperature: float = Field(0.7)
    top_p: float = Field(0.9)
    model: Optional[Any] = Field(None)
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "custom_llm"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the LLM."""
        try:
            if self.model is None:
                print("Lazy-loading the model...")
                try:
                    self.model = Llama(
                        model_path=self.model_path,
                        n_ctx=self.context_length,
                        temperature=self.temperature,
                        top_p=self.top_p,
                    )
                except Exception as e:
                    print(f"Error loading model: {e}")
                    return f"Error loading model: {e}\n\nMock response to: {prompt[:100]}..."
            
            response = self.model.create_completion(prompt=prompt, stop=stop or [])
            return response["choices"][0]["text"].strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error generating response: {e}\n\nMock response to: {prompt[:100]}..."

# Factory function
def get_langchain_llm():
    """Get a LangChain compatible LLM."""
    return CustomLLM(model_path=MODEL_PATH)
