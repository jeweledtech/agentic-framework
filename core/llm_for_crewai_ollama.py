"""
LLM for CrewAI - Ollama Integration
===================================

This module provides the LLM interface for CrewAI agents using Ollama.
It replaces the old local GGUF model approach with Ollama integration.
"""

import os
from typing import Optional

# Import the Ollama singleton
from core.llm_singleton_ollama import EnhancedLLMSingleton

# Create a singleton instance
_llm_singleton = EnhancedLLMSingleton()

def get_llm(model_name: Optional[str] = None, task_type: Optional[str] = None):
    """
    Get an LLM instance for CrewAI agents.
    
    Args:
        model_name: Optional specific model name (e.g., 'llama3:8b', 'codellama:34b')
        task_type: Optional task type ('general', 'coding', 'analysis', 'creative')
    
    Returns:
        LLM instance configured for the requested model/task
    """
    return _llm_singleton.get_llm(model_name=model_name, task_type=task_type)

# Default function for backward compatibility
def get_llm_for_crewai():
    """Get the default LLM for CrewAI agents"""
    return get_llm(task_type='general')