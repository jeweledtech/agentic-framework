"""Unit tests for BaseAgent, AgentConfig, AgentRole, AgentTools."""

import os
import pytest
from core.agent import BaseAgent, AgentConfig, AgentRole, AgentTools


class TestAgentRole:
    def test_create_role(self):
        role = AgentRole(
            name="Sales Rep",
            description="Handles sales",
            goal="Close deals",
            backstory="Experienced salesperson",
        )
        assert role.name == "Sales Rep"
        assert role.goal == "Close deals"

    def test_role_requires_fields(self):
        with pytest.raises(Exception):
            AgentRole(name="Missing Fields")


class TestAgentTools:
    def test_empty_tools(self):
        tools = AgentTools()
        assert tools.tool_names == []

    def test_tools_with_names(self):
        tools = AgentTools(tool_names=["web_search_tool", "crm_api_tool"])
        assert len(tools.tool_names) == 2
        assert "web_search_tool" in tools.tool_names


class TestAgentConfig:
    def test_create_config(self, sample_role, sample_tools):
        config = AgentConfig(
            id="test_001",
            role=sample_role,
            tools=sample_tools,
            department="marketing",
        )
        assert config.id == "test_001"
        assert config.department == "marketing"
        assert config.temperature == 0.7  # default

    def test_config_defaults(self, sample_role):
        config = AgentConfig(id="minimal", role=sample_role)
        assert config.tools.tool_names == []
        assert config.department == "sales"  # default
        assert config.parent_id is None
        assert config.verbose is False

    def test_config_custom_temperature(self, sample_role):
        config = AgentConfig(id="hot", role=sample_role, temperature=0.95)
        assert config.temperature == 0.95


class TestBaseAgent:
    def test_create_agent(self, sample_agent):
        assert sample_agent.config.id == "test_agent"
        assert sample_agent.llm is not None
        assert sample_agent.kb is not None
        assert sample_agent.tasks == []

    def test_agent_has_access_control(self, sample_agent):
        assert sample_agent.access_control is not None

    def test_agent_has_audit_logger(self, sample_agent):
        assert sample_agent.audit is not None

    def test_add_task(self, sample_agent):
        sample_agent.add_task("Research competitors", "Competitor report")
        assert len(sample_agent.tasks) == 1

    def test_execute_tasks_mock(self, sample_agent):
        sample_agent.add_task("Research topic X", "Research report")
        results = sample_agent.execute_tasks()
        assert len(results) == 1
        assert sample_agent.tasks == []  # Queue cleared

    def test_execute_empty_tasks(self, sample_agent):
        results = sample_agent.execute_tasks()
        assert results == []

    def test_direct_query(self, sample_agent):
        response = sample_agent.direct_query("What is our sales strategy?")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_agent_with_custom_llm_provider(self, sample_agent_config):
        from core.providers.llm import MockLLMProvider

        custom_llm = MockLLMProvider(model_name="custom_test")
        agent = BaseAgent(sample_agent_config, llm_provider=custom_llm)
        assert agent.llm is custom_llm

    def test_delegate_to_child_not_implemented(self, sample_agent):
        with pytest.raises(NotImplementedError):
            sample_agent.delegate_to_child("child", "task", "output")

    def test_mock_lead_generation(self, sample_agent):
        sample_agent.add_task("Generate leads for coaching businesses", "Lead list")
        results = sample_agent.execute_tasks()
        assert len(results) == 1
        assert "Lead" in results[0] or "lead" in results[0].lower() or "Mock" in results[0]

    def test_multiple_tasks(self, sample_agent):
        sample_agent.add_task("Task 1", "Output 1")
        sample_agent.add_task("Task 2", "Output 2")
        assert len(sample_agent.tasks) == 2
        results = sample_agent.execute_tasks()
        assert len(results) == 2
