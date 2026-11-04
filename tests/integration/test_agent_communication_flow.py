"""Integration tests for full message routing flows."""

import pytest
from core.agent_communication import (
    AgentCommunicationProtocol,
    MessageRouter,
)


class TestFullMessageFlow:
    def test_request_response_cycle(self):
        router = MessageRouter()

        # Step 1: Send a request
        request = AgentCommunicationProtocol.create_delegation_message(
            sender_id="head_of_sales",
            recipient_id="lead_gen_agent",
            task={"description": "Generate 5 leads", "priority": "HIGH"},
        )
        recipients = router.route_message(request, {})
        assert "lead_gen_agent" in recipients

        # Step 2: Send response back
        response = AgentCommunicationProtocol.create_response_message(
            request,
            sender_id="lead_gen_agent",
            result={"status": "COMPLETED", "executive_summary": "5 leads generated"},
        )
        recipients = router.route_message(response, {})
        assert "head_of_sales" in recipients

        # Step 3: Verify message history
        assert len(router.message_history) == 2

    def test_escalation_flow(self):
        router = MessageRouter()
        hierarchy = {
            "sales": {
                "head": "head_of_sales",
                "managers": ["outbound_manager", "inbound_manager"],
            }
        }

        # Manager escalates to department head
        escalation = AgentCommunicationProtocol.create_escalation_message(
            sender_id="outbound_manager",
            recipient_id="head_of_sales",
            escalation_context={
                "issue_description": "Budget approval needed",
                "reason": "Over $10k threshold",
            },
        )
        recipients = router.route_message(escalation, hierarchy)
        assert "head_of_sales" in recipients

    def test_thread_tracking(self):
        router = MessageRouter()
        msg1 = AgentCommunicationProtocol.create_delegation_message(
            "a", "b", {"description": "task 1"}
        )
        router.route_message(msg1, {})

        response = AgentCommunicationProtocol.create_response_message(
            msg1, "b", {"status": "COMPLETED"}
        )
        # Use the same thread_id
        response["thread_id"] = msg1["thread_id"]
        router.route_message(response, {})

        thread_id = msg1["thread_id"]
        assert thread_id in router.active_threads
        assert len(router.active_threads[thread_id]) == 2

    def test_collaboration_flow(self):
        router = MessageRouter()
        collab = AgentCommunicationProtocol.create_collaboration_request(
            initiator_id="head_of_content",
            collaborators=["writer_agent", "seo_agent", "designer_agent"],
            project_context={"project_name": "Launch Campaign"},
        )
        recipients = router.route_message(collab, {})
        assert len(recipients) == 3
        assert "writer_agent" in recipients
