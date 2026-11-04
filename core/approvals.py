"""
Human-approval gate for agent actions with external side effects.

Any tool call that can change something outside the framework (trigger an
n8n workflow, write a file, send an email, update a CRM record, ...) goes
through ``gate_action``. Unless the action is read-only, it is NOT executed:
it is queued as a PendingAction and the tool returns a PENDING_HUMAN_APPROVAL
message. A human with the API_ADMIN permission then approves or rejects it via
the /approvals API. Approved actions run exactly once.

The gate is on unless ``REQUIRE_HUMAN_APPROVAL=false`` is set explicitly.
Pending actions expire after ``APPROVAL_TTL_SECONDS`` (default 24h).

Every request, decision and execution is written to the audit log.

Note: the queue is in-process memory. Pending actions are lost on restart
(they fail safe — they never run), and each replica has its own queue.
"""

import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from core.audit import AuditEvent, get_audit_logger

PENDING_PREFIX = "PENDING_HUMAN_APPROVAL"
DEFAULT_TTL_SECONDS = 24 * 3600


class ApprovalError(RuntimeError):
    """The action cannot be decided (already decided, or expired)."""


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"
    FAILED = "failed"


@dataclass
class PendingAction:
    id: str
    tool: str
    action: str
    params: Dict[str, Any]
    requested_by: str
    created_at: float
    expires_at: float
    status: ApprovalStatus = ApprovalStatus.PENDING
    decided_by: Optional[str] = None
    decided_at: Optional[float] = None
    reason: str = ""
    result: Optional[str] = None
    _execute: Optional[Callable[[], Any]] = field(default=None, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tool": self.tool,
            "action": self.action,
            "params": self.params,
            "requested_by": self.requested_by,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "status": self.status.value,
            "decided_by": self.decided_by,
            "decided_at": self.decided_at,
            "reason": self.reason,
            "result": self.result,
        }


def approval_required() -> bool:
    return os.getenv("REQUIRE_HUMAN_APPROVAL", "true").strip().lower() != "false"


def _ttl_seconds() -> int:
    try:
        return int(os.getenv("APPROVAL_TTL_SECONDS", DEFAULT_TTL_SECONDS))
    except ValueError:
        return DEFAULT_TTL_SECONDS


def _audit(event_type: str, action: PendingAction, actor: str, outcome: str = "success",
           extra: Optional[Dict[str, Any]] = None) -> None:
    get_audit_logger().log(AuditEvent(
        event_type=event_type,
        actor_id=actor,
        action=event_type,
        resource=f"{action.tool}:{action.action}",
        details={"approval_id": action.id, **(extra or {})},
        outcome=outcome,
        correlation_id=action.id,
    ))


class ApprovalQueue:
    """Thread-safe in-memory store of actions awaiting human approval."""

    _instance: Optional["ApprovalQueue"] = None
    _cls_lock = threading.Lock()

    def __new__(cls) -> "ApprovalQueue":
        with cls._cls_lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst._actions = {}
                inst._lock = threading.Lock()
                cls._instance = inst
        return cls._instance

    @classmethod
    def reset_singleton(cls) -> None:
        with cls._cls_lock:
            cls._instance = None

    def submit(self, tool: str, action: str, params: Dict[str, Any],
               execute: Callable[[], Any], requested_by: str) -> PendingAction:
        now = time.time()
        pending = PendingAction(
            id=uuid.uuid4().hex,
            tool=tool,
            action=action,
            params=dict(params),
            requested_by=requested_by,
            created_at=now,
            expires_at=now + _ttl_seconds(),
            _execute=execute,
        )
        with self._lock:
            self._actions[pending.id] = pending
        _audit("approval.requested", pending, requested_by, outcome="pending")
        return pending

    def get(self, action_id: str) -> PendingAction:
        with self._lock:
            return self._actions[action_id]

    def list(self, status: Optional[ApprovalStatus] = None) -> List[PendingAction]:
        with self._lock:
            self._expire_locked()
            items = list(self._actions.values())
        if status is not None:
            items = [a for a in items if a.status == status]
        return sorted(items, key=lambda a: a.created_at)

    def _expire_locked(self) -> None:
        now = time.time()
        for a in self._actions.values():
            if a.status == ApprovalStatus.PENDING and now >= a.expires_at:
                a.status = ApprovalStatus.EXPIRED
                a._execute = None

    def approve(self, action_id: str, approver: str) -> PendingAction:
        with self._lock:
            action = self._actions[action_id]
            self._expire_locked()
            if action.status != ApprovalStatus.PENDING:
                raise ApprovalError(f"Action {action_id} is {action.status.value}")
            # Mark as executed before running so a concurrent approve cannot run it twice.
            action.status = ApprovalStatus.EXECUTED
            action.decided_by = approver
            action.decided_at = time.time()
            execute, action._execute = action._execute, None

        _audit("approval.approved", action, approver)
        try:
            result = execute() if execute else None
            action.result = None if result is None else str(result)
            _audit("approval.executed", action, approver)
        except Exception as exc:  # record, don't re-raise: the decision stands
            action.status = ApprovalStatus.FAILED
            action.result = f"Error: {exc}"
            _audit("approval.executed", action, approver, outcome="failure",
                   extra={"error": str(exc)})
        return action

    def reject(self, action_id: str, approver: str, reason: str = "") -> PendingAction:
        with self._lock:
            action = self._actions[action_id]
            self._expire_locked()
            if action.status != ApprovalStatus.PENDING:
                raise ApprovalError(f"Action {action_id} is {action.status.value}")
            action.status = ApprovalStatus.REJECTED
            action.decided_by = approver
            action.decided_at = time.time()
            action.reason = reason
            action._execute = None
        _audit("approval.rejected", action, approver, extra={"reason": reason})
        return action


def get_approval_queue() -> ApprovalQueue:
    return ApprovalQueue()


def gate_action(tool: str, action: str, params: Dict[str, Any], *, read_only: bool,
                execute: Callable[[], Any]) -> Any:
    """Run *execute* now if the action is read-only; otherwise queue it for a human."""
    if read_only or not approval_required():
        return execute()

    from core.auth import current_principal
    principal = current_principal.get()
    requested_by = principal.key_id if principal else "agent"

    pending = get_approval_queue().submit(tool, action, params, execute, requested_by)
    return (
        f"{PENDING_PREFIX}: '{action}' via {tool} is waiting for human approval "
        f"(approval id {pending.id}). It has not been executed."
    )
