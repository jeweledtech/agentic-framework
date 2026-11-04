"""Integration tests for CrewBuilder end-to-end with mock LLM."""

import pytest
from core.agent import BaseAgent, AgentConfig, AgentRole, AgentTools
from core.crew import CrewBuilder


def _make_agent(agent_id, department="sales"):
    return BaseAgent(
        AgentConfig(
            id=agent_id,
            role=AgentRole(
                name=f"{agent_id.replace('_', ' ').title()}",
                description="Test agent",
                goal="Complete assigned tasks",
                backstory="Test backstory",
            ),
            department=department,
        )
    )


class TestCrewExecution:
    def test_single_agent_crew(self):
        agent = _make_agent("researcher")
        task = {
            "description": "Research topic X",
            "expected_output": "Research report",
            "agent": agent,
            "context": {},
        }
        crew = CrewBuilder.create_crew("solo", [agent], [task])
        results = CrewBuilder.run_crew(crew)
        assert len(results) > 0

    def test_multi_agent_crew(self):
        research_agent = _make_agent("researcher")
        writer_agent = _make_agent("writer")

        tasks = [
            {
                "description": "Research the market",
                "expected_output": "Market analysis",
                "agent": research_agent,
                "context": {},
            },
            {
                "description": "Write a blog post",
                "expected_output": "Blog post draft",
                "agent": writer_agent,
                "context": {},
            },
        ]

        crew = CrewBuilder.create_crew(
            "content_team", [research_agent, writer_agent], tasks
        )
        results = CrewBuilder.run_crew(crew)
        assert len(results) == 2

    def test_crew_with_no_tasks_returns_agent_status(self):
        agent = _make_agent("idle_agent")
        crew = CrewBuilder.create_crew("idle_crew", [agent])
        results = CrewBuilder.run_crew(crew)
        assert isinstance(results, list)

    def test_cross_department_crew(self):
        sales_agent = _make_agent("sales_rep", "sales")
        marketing_agent = _make_agent("marketer", "marketing")

        tasks = [
            {
                "description": "Qualify lead",
                "expected_output": "Qualification score",
                "agent": sales_agent,
                "context": {},
            },
            {
                "description": "Create campaign",
                "expected_output": "Campaign brief",
                "agent": marketing_agent,
                "context": {},
            },
        ]

        crew = CrewBuilder.create_crew(
            "cross_dept", [sales_agent, marketing_agent], tasks
        )
        results = CrewBuilder.run_crew(crew)
        assert len(results) == 2
