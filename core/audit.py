"""
Structured Audit Logging for the JeweledTech Agentic Framework.

Provides a thread-safe audit logger that writes structured JSON events
to stdout (and optionally to a file via AUDIT_LOG_FILE env var).

Event types follow the pattern "category.action":
  agent.task.start, agent.task.complete, kb.query, api.request,
  security.permission_denied, etc.

Usage:
    from core.audit import get_audit_logger

    audit = get_audit_logger()
    audit.log_agent_action("research_agent", "sales", "task.start",
                           resource="lead_generation", details={"count": 3})
"""

import json
import logging
import os
import threading
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Categories of auditable events."""

    # Agent lifecycle
    AGENT_TASK_START = "agent.task.start"
    AGENT_TASK_COMPLETE = "agent.task.complete"
    AGENT_TASK_ERROR = "agent.task.error"
    AGENT_QUERY = "agent.query"
    AGENT_DELEGATE = "agent.delegate"

    # Knowledge base
    KB_QUERY = "kb.query"
    KB_DOCUMENT_READ = "kb.document.read"

    # API
    API_REQUEST = "api.request"
    API_AUTH_SUCCESS = "api.auth.success"
    API_AUTH_FAILURE = "api.auth.failure"

    # Security
    SECURITY_PERMISSION_DENIED = "security.permission_denied"
    SECURITY_PERMISSION_GRANTED = "security.permission_granted"

    # Provider
    PROVIDER_SELECTED = "provider.selected"
    PROVIDER_FALLBACK = "provider.fallback"


class AuditEvent(BaseModel):
    """A single audit log entry."""

    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str
    actor_id: str = ""
    department: str = ""
    action: str = ""
    resource: str = ""
    details: Dict[str, Any] = Field(default_factory=dict)
    outcome: str = "success"
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class AuditLogger:
    """Thread-safe singleton audit logger.

    Writes JSON-lines to a Python logger (stdout by default) and optionally
    to a file specified by AUDIT_LOG_FILE.
    """

    _instance: Optional["AuditLogger"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "AuditLogger":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._audit_logger = logging.getLogger("audit")
                    inst._audit_logger.setLevel(logging.INFO)

                    # File handler (optional)
                    audit_file = os.environ.get("AUDIT_LOG_FILE")
                    if audit_file:
                        fh = logging.FileHandler(audit_file)
                        fh.setFormatter(logging.Formatter("%(message)s"))
                        inst._audit_logger.addHandler(fh)

                    # Stream handler for structured output
                    if not inst._audit_logger.handlers:
                        sh = logging.StreamHandler()
                        sh.setFormatter(logging.Formatter("%(message)s"))
                        inst._audit_logger.addHandler(sh)

                    cls._instance = inst
        return cls._instance

    def log(self, event: AuditEvent) -> None:
        """Write an audit event as a JSON line."""
        self._audit_logger.info(event.model_dump_json())

    def log_agent_action(
        self,
        actor_id: str,
        department: str,
        action: str,
        resource: str = "",
        details: Optional[Dict[str, Any]] = None,
        outcome: str = "success",
        correlation_id: Optional[str] = None,
    ) -> None:
        """Convenience method for agent-related events."""
        event = AuditEvent(
            event_type=f"agent.{action}",
            actor_id=actor_id,
            department=department,
            action=action,
            resource=resource,
            details=details or {},
            outcome=outcome,
            correlation_id=correlation_id or str(uuid.uuid4()),
        )
        self.log(event)

    def log_kb_access(
        self,
        actor_id: str,
        department: str,
        target_department: str,
        query: str = "",
        outcome: str = "success",
    ) -> None:
        """Convenience method for knowledge base access events."""
        event = AuditEvent(
            event_type=AuditEventType.KB_QUERY,
            actor_id=actor_id,
            department=department,
            action="kb.query",
            resource=target_department,
            details={"query": query[:200]},  # Truncate long queries
            outcome=outcome,
        )
        self.log(event)

    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        client_ip: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Convenience method for API request events."""
        event = AuditEvent(
            event_type=AuditEventType.API_REQUEST,
            actor_id=client_ip,
            action="api.request",
            resource=path,
            details={"method": method, "status_code": status_code, **(details or {})},
            outcome="success" if status_code < 400 else "failure",
        )
        self.log(event)

    def log_permission_denied(
        self,
        actor_id: str,
        department: str,
        permission: str,
        resource: str = "",
    ) -> None:
        """Convenience method for permission denial events."""
        event = AuditEvent(
            event_type=AuditEventType.SECURITY_PERMISSION_DENIED,
            actor_id=actor_id,
            department=department,
            action="security.permission_denied",
            resource=resource,
            details={"permission": permission},
            outcome="denied",
        )
        self.log(event)

    @classmethod
    def reset_singleton(cls) -> None:
        """Reset the singleton (for testing)."""
        with cls._lock:
            cls._instance = None


def get_audit_logger() -> AuditLogger:
    """Get the singleton AuditLogger instance."""
    return AuditLogger()
