#!/usr/bin/env python3
"""
Quick test script to validate the JeweledTech Agentic Framework
Compatible with pytest for CI/CD pipelines
"""

import sys
import os
import pytest

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set mock mode for CI testing
os.environ['USE_MOCK_KB'] = 'true'


def test_core_imports():
    """Test that all core imports work"""
    from core.agent import BaseAgent, AgentConfig, AgentRole, AgentTools

    assert BaseAgent is not None
    assert AgentConfig is not None
    assert AgentRole is not None
    assert AgentTools is not None


def test_example_agent_imports():
    """Test that example agent imports work"""
    from agents.examples import ResearchAgent, WriterAgent

    assert ResearchAgent is not None
    assert WriterAgent is not None


def test_crew_imports():
    """Test that crew imports work"""
    from core.crew import CrewBuilder

    assert CrewBuilder is not None


def test_knowledge_base_imports():
    """Test that knowledge base imports work"""
    from knowledge_bases.kb_interface import KnowledgeBaseInterface

    assert KnowledgeBaseInterface is not None


def test_agent_config_creation():
    """Test creating an agent configuration"""
    from core.agent import AgentConfig, AgentRole, AgentTools

    role = AgentRole(
        name="Test Agent",
        description="A test agent",
        goal="Test the framework",
        backstory="Created for testing"
    )

    tools = AgentTools(tool_names=["web_search"])

    config = AgentConfig(
        id="test_agent",
        role=role,
        tools=tools,
        department="research"
    )

    assert config.id == "test_agent"
    assert config.role.name == "Test Agent"
    assert "web_search" in config.tools.tool_names


def test_knowledge_base_interface():
    """Test knowledge base interface in mock mode"""
    from knowledge_bases.kb_interface import get_kb_interface

    kb = get_kb_interface("research")
    assert kb is not None

    categories = kb.list_categories()
    assert isinstance(categories, list)


def test_research_agent_creation():
    """Test creating a research agent"""
    from agents.examples import ResearchAgent

    # This should work with mock LLM
    agent = ResearchAgent()
    assert agent is not None
    assert agent.config.id == "research_agent"


def test_writer_agent_creation():
    """Test creating a writer agent"""
    from agents.examples import WriterAgent

    # This should work with mock LLM
    agent = WriterAgent()
    assert agent is not None


# Allow running as standalone script
def main():
    """Run tests with pytest when executed directly"""
    print("=" * 60)
    print("JeweledTech Agentic Framework - Validation Test")
    print("=" * 60)

    # Run pytest programmatically
    exit_code = pytest.main([__file__, "-v", "--tb=short"])

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
