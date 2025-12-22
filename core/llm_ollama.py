"""
Core LLM module - Ollama Integration
====================================

This module provides the main LLM interface for agents using Ollama.
Replaces the old local GGUF model approach.
"""

from typing import List, Dict, Optional
from core.llm_singleton_ollama import EnhancedLLMSingleton

# Create singleton instance
_llm_singleton = EnhancedLLMSingleton()

class OllamaModelWrapper:
    """Wrapper to match the expected interface for agents"""
    
    def __init__(self):
        self.llm = _llm_singleton.get_llm()
    
    def generate(self, 
                 system_prompt: str, 
                 user_prompt: str, 
                 chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate a response using Ollama"""
        if chat_history is None:
            chat_history = []
        
        # Combine prompts for the LLM call
        full_prompt = f"{system_prompt}\n\n"
        
        # Add chat history
        for msg in chat_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            full_prompt += f"{role}: {content}\n"
        
        # Add current user prompt
        full_prompt += f"user: {user_prompt}\nassistant: "
        
        # Generate response
        try:
            response = self.llm._call(full_prompt)
            return response
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while generating a response."

# Singleton instance
llm_instance = None

def get_llm():
    """Get or create the LLM instance"""
    global llm_instance
    if llm_instance is None:
        llm_instance = OllamaModelWrapper()
    return llm_instance