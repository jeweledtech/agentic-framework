#!/usr/bin/env python3
"""
Quick test script to validate the JeweledTech Agentic Framework
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all core imports work"""
    print("Testing imports...")
    try:
        from core.agent import BaseAgent, AgentConfig, AgentRole, AgentTools
        print("✓ Core agent imports successful")
        
        from agents.examples import ResearchAgent, WriterAgent
        print("✓ Example agent imports successful")
        
        from core.crew import CrewBuilder
        print("✓ Crew imports successful")
        
        from knowledge_bases.kb_interface import KnowledgeBaseInterface
        print("✓ Knowledge base imports successful")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_agent_creation():
    """Test creating example agents"""
    print("\nTesting agent creation...")
    try:
        from agents.examples import ResearchAgent, WriterAgent
        
        research_agent = ResearchAgent()
        print("✓ Research agent created successfully")
        
        writer_agent = WriterAgent()
        print("✓ Writer agent created successfully")
        
        return True
    except Exception as e:
        print(f"✗ Agent creation error: {e}")
        return False

def test_knowledge_base():
    """Test knowledge base access"""
    print("\nTesting knowledge base...")
    try:
        from knowledge_bases.kb_interface import get_kb_interface
        
        kb = get_kb_interface("research")
        categories = kb.list_categories()
        print(f"✓ Knowledge base accessible with {len(categories)} categories")
        
        return True
    except Exception as e:
        print(f"✗ Knowledge base error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("JeweledTech Agentic Framework - Validation Test")
    print("="*60)
    
    tests = [
        test_imports(),
        test_agent_creation(),
        test_knowledge_base()
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("\n" + "="*60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Framework is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())