"""Unit tests for audit logging (core/audit.py)."""

import json
import logging
import pytest
from core.audit import (
    AuditEvent,
    AuditEventType,
    AuditLogger,
    get_audit_logger,
)


class TestAuditEvent:
    def test_create_event(self):
        event = AuditEvent(
            event_type=AuditEventType.AGENT_TASK_START,
            actor_id="test_agent",
            department="sales",
            action="task.start",
            resource="lead_gen",
        )
        assert event.event_type == "agent.task.start"
        assert event.actor_id == "test_agent"
        assert event.outcome == "success"
        assert event.correlation_id  # Auto-generated

    def test_event_serialization(self):
        event = AuditEvent(
            event_type="test.event",
            actor_id="agent_1",
            details={"key": "value"},
        )
        json_str = event.model_dump_json()
        parsed = json.loads(json_str)
        assert parsed["event_type"] == "test.event"
        assert parsed["details"]["key"] == "value"

    def test_event_defaults(self):
        event = AuditEvent(event_type="minimal")
        assert event.actor_id == ""
        assert event.department == ""
        assert event.outcome == "success"
        assert event.timestamp  # Auto-generated


class TestAuditLogger:
    def test_singleton(self):
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()
        assert logger1 is logger2

    def test_log_event(self, caplog):
        audit = get_audit_logger()
        event = AuditEvent(
            event_type="test.log",
            actor_id="unit_test",
        )
        with caplog.at_level(logging.INFO, logger="audit"):
            audit.log(event)
        # The event should have been logged
        assert any("test.log" in record.message for record in caplog.records)

    def test_log_agent_action(self, caplog):
        audit = get_audit_logger()
        with caplog.at_level(logging.INFO, logger="audit"):
            audit.log_agent_action(
                actor_id="research_agent",
                department="sales",
                action="task.start",
                resource="lead_generation",
                details={"count": 3},
            )
        assert any("research_agent" in record.message for record in caplog.records)

    def test_log_kb_access(self, caplog):
        audit = get_audit_logger()
        with caplog.at_level(logging.INFO, logger="audit"):
            audit.log_kb_access(
                actor_id="sales_agent",
                department="sales",
                target_department="sales",
                query="icp details",
            )
        assert any("kb.query" in record.message for record in caplog.records)

    def test_log_api_request(self, caplog):
        audit = get_audit_logger()
        with caplog.at_level(logging.INFO, logger="audit"):
            audit.log_api_request(
                method="GET",
                path="/health",
                status_code=200,
                client_ip="127.0.0.1",
            )
        assert any("api.request" in record.message for record in caplog.records)

    def test_log_permission_denied(self, caplog):
        audit = get_audit_logger()
        with caplog.at_level(logging.INFO, logger="audit"):
            audit.log_permission_denied(
                actor_id="sales_agent",
                department="sales",
                permission="kb:read:engineering",
                resource="engineering_kb",
            )
        assert any("permission_denied" in record.message for record in caplog.records)


class TestAuditEventType:
    def test_event_types_are_strings(self):
        assert isinstance(AuditEventType.AGENT_TASK_START, str)
        assert AuditEventType.KB_QUERY == "kb.query"
        assert AuditEventType.API_REQUEST == "api.request"
        assert AuditEventType.SECURITY_PERMISSION_DENIED == "security.permission_denied"
