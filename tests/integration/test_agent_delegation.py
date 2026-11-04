"""Integration tests for agent-to-agent delegation chains."""

import pytest
from core.agent import BaseAgent, AgentConfig, AgentRole, AgentTools


def _make_agent(agent_id, department="sales", role_name="Agent"):
    config = AgentConfig(
        id=agent_id,
        role=AgentRole(
            name=role_name,
            description=f"{role_name} agent",
            goal="Complete tasks",
            backstory="Test agent",
        ),
        department=department,
    )
    return BaseAgent(config)


class TestAgentDelegation:
    def test_parent_child_relationship(self):
        parent = _make_agent("parent_agent", role_name="Manager")
        child = _make_agent("child_agent", role_name="Worker")
        # Parent and child can both execute tasks independently
        parent.add_task("Manage project", "Project plan")
        child.add_task("Execute subtask", "Task result")
        p_results = parent.execute_tasks()
        c_results = child.execute_tasks()
        assert len(p_results) == 1
        assert len(c_results) == 1

    def test_delegation_raises_not_implemented(self):
        parent = _make_agent("parent")
        with pytest.raises(NotImplementedError):
            parent.delegate_to_child("child", "do this", "expected output")

    def test_multiple_agents_independent(self):
        agents = [_make_agent(f"agent_{i}") for i in range(3)]
        for i, agent in enumerate(agents):
            agent.add_task(f"Task {i}", f"Output {i}")
        all_results = []
        for agent in agents:
            all_results.extend(agent.execute_tasks())
        assert len(all_results) == 3
