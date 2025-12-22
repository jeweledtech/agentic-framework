#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add current directory to path if needed
if '.' not in sys.path:
    sys.path.append('.')

def test_knowledge_base():
    """Test if we can access the knowledge base"""
    try:
        # Try importing the knowledge base interface if it exists
        try:
            from knowledge_bases.kb_interface import get_kb_interface
            print("✅ Successfully imported knowledge base interface")
        except ImportError:
            print("❌ Could not import knowledge base interface")
            return False
        
        # Initialize the knowledge base interface
        kb = get_kb_interface("sales")
        print("✅ Successfully initialized knowledge base interface")
        
        # List categories
        categories = kb.list_categories()
        print(f"Found {len(categories)} categories: {categories}")
        
        # Try to get a document if categories were found
        if categories:
            doc = kb.get_document(categories[0])
            print(f"First document in {categories[0]} has {len(doc)} characters")
        
        return True
    except Exception as e:
        print(f"❌ Error testing knowledge base: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm():
    """Test if we can access the LLM"""
    try:
        # Try importing the LLM module if it exists
        try:
            from core.llm import get_llm
            print("✅ Successfully imported LLM module")
        except ImportError:
            print("❌ Could not import LLM module")
            return False
        
        try:
            # Initialize the LLM (but don't generate text for this basic test)
            llm = get_llm()
            print("✅ Successfully initialized LLM")
            print("Model loaded from:", llm.config['model_path'])
            return True
        except Exception as e:
            print(f"❌ Error initializing LLM: {e}")
            import traceback
            traceback.print_exc()
            return False
    except Exception as e:
        print(f"❌ Error testing LLM: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Testing Basic Components ===")
    kb_success = test_knowledge_base()
    llm_success = test_llm()
    
    if kb_success:
        print("✅ Knowledge base test passed")
    else:
        print("❌ Knowledge base test failed")
        
    if llm_success:
        print("✅ LLM test passed")
    else:
        print("❌ LLM test failed")
