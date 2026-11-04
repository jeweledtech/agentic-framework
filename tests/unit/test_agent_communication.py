"""Unit tests for AgentCommunicationProtocol, MessageRouter, CommunicationAnalytics."""

import pytest
from core.agent_communication import (
    AgentCommunicationProtocol,
    MessageRouter,
    CommunicationAnalytics,
)


class TestAgentCommunicationProtocol:
    def test_create_delegation_message(self):
        msg = AgentCommunicationProtocol.create_delegation_message(
            sender_id="head_of_sales",
            recipient_id="lead_gen_agent",
            task={
                "description": "Generate 5 leads",
                "priority": "HIGH",
                "objective": "Fill pipeline",
            },
        )
        assert msg["sender"]["agent_id"] == "head_of_sales"
        assert msg["recipient"]["agent_id"] == "lead_gen_agent"
        assert msg["message_type"] == "REQUEST"
        assert msg["priority"] == "HIGH"
        assert "message_id" in msg

    def test_create_response_message(self):
        original = AgentCommunicationProtocol.create_delegation_message(
            "sender", "recipient", {"description": "task"}
        )
        response = AgentCommunicationProtocol.create_response_message(
            original,
            sender_id="recipient",
            result={"status": "COMPLETED", "executive_summary": "Done"},
        )
        assert response["message_type"] == "RESPONSE"
        assert response["sender"]["response_to"] == original["message_id"]

    def test_create_escalation_message(self):
        msg = AgentCommunicationProtocol.create_escalation_message(
            sender_id="sales_agent",
            recipient_id="head_of_sales",
            escalation_context={
                "issue_description": "Cannot reach prospect",
                "reason": "Blocked by IT filter",
            },
        )
        assert msg["message_type"] == "ESCALATION"
        assert msg["priority"] == "HIGH"

    def test_create_handoff_template(self):
        template = AgentCommunicationProtocol.create_handoff_template({
            "sender_agent": "research_agent",
            "recipient_responsibility": "Write blog post",
            "expected_output": "1000-word article",
        })
        assert "research_agent" in template
        assert "Write blog post" in template

    def test_create_collaboration_request(self):
        msg = AgentCommunicationProtocol.create_collaboration_request(
            initiator_id="head_of_content",
            collaborators=["writer_agent", "seo_agent"],
            project_context={"project_name": "Q1 Content Push", "objective": "10 articles"},
        )
        assert msg["message_type"] == "COLLABORATION_REQUEST"
        assert len(msg["collaborators"]) == 2


class TestMessageRouter:
    def test_route_request(self):
        router = MessageRouter()
        msg = AgentCommunicationProtocol.create_delegation_message(
            "sender", "recipient", {"description": "task"}
        )
        recipients = router.route_message(msg, {})
        assert "recipient" in recipients

    def test_route_response(self):
        router = MessageRouter()
        original = AgentCommunicationProtocol.create_delegation_message(
            "sender", "recipient", {"description": "task"}
        )
        response = AgentCommunicationProtocol.create_response_message(
            original, "recipient", {"status": "COMPLETED"}
        )
        recipients = router.route_message(response, {})
        assert "sender" in recipients

    def test_route_escalation_default(self):
        router = MessageRouter()
        msg = AgentCommunicationProtocol.create_escalation_message(
            "agent", "chief", {"issue_description": "problem"}
        )
        recipients = router.route_message(msg, {})
        assert "chief_agent" in recipients

    def test_message_history(self):
        router = MessageRouter()
        msg = AgentCommunicationProtocol.create_delegation_message(
            "a", "b", {"description": "task"}
        )
        router.route_message(msg, {})
        assert len(router.message_history) == 1


class TestCommunicationAnalytics:
    def test_analyze_empty_history(self):
        analytics = CommunicationAnalytics()
        result = analytics.analyze_communication_patterns([])
        assert result["total_messages"] == 0

    def test_analyze_message_types(self):
        analytics = CommunicationAnalytics()
        messages = [
            {"message_type": "REQUEST"},
            {"message_type": "REQUEST"},
            {"message_type": "RESPONSE"},
        ]
        result = analytics.analyze_communication_patterns(messages)
        assert result["message_types"]["REQUEST"] == 2
        assert result["message_types"]["RESPONSE"] == 1

    def test_escalation_rate(self):
        analytics = CommunicationAnalytics()
        messages = [
            {"message_type": "REQUEST"},
            {"message_type": "ESCALATION"},
        ]
        result = analytics.analyze_communication_patterns(messages)
        assert result["escalation_rate"] == 1.0  # 1 escalation / 1 request
