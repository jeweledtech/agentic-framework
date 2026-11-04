"""Unit tests for CrewBuilder, AgentLoader, TaskLoader, OrganizationBuilder."""

import pytest
from core.agent import BaseAgent, AgentConfig, AgentRole, AgentTools
from core.crew import CrewBuilder


class TestCrewBuilder:
    def test_create_crew_with_agents(self, sample_agent):
        crew = CrewBuilder.create_crew("test_crew", [sample_agent])
        assert isinstance(crew, dict)
        assert crew["name"] == "test_crew"
        assert len(crew["agents"]) == 1

    def test_create_crew_with_tasks(self, sample_agent):
        task = {
            "description": "Test task",
            "expected_output": "Test output",
            "agent": sample_agent,
            "context": {},
        }
        crew = CrewBuilder.create_crew("task_crew", [sample_agent], [task])
        assert len(crew["tasks"]) == 1

    def test_run_crew_dict(self, sample_agent):
        task = {
            "description": "Research topic",
            "expected_output": "Report",
            "agent": sample_agent,
            "context": {},
        }
        crew = CrewBuilder.create_crew("run_crew", [sample_agent], [task])
        results = CrewBuilder.run_crew(crew)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_run_crew_empty_tasks(self, sample_agent):
        crew = CrewBuilder.create_crew("empty_crew", [sample_agent])
        results = CrewBuilder.run_crew(crew)
        assert isinstance(results, list)

    def test_crew_verbose_default(self, sample_agent):
        crew = CrewBuilder.create_crew("verbose_crew", [sample_agent])
        assert crew["verbose"] is True
