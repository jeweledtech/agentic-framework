"""API tests for the human-approval endpoints."""

from unittest.mock import Mock

import pytest

from core.approvals import ApprovalStatus, gate_action, get_approval_queue

EXEC = "k-exec-111"


@pytest.fixture
def secured(monkeypatch):
    monkeypatch.setenv("ENABLE_AUTH", "true")
    monkeypatch.setenv("FRAMEWORK_API_KEYS", f"{EXEC}:executive,k-sales:sales")


def _queue_one(execute):
    gate_action("Write File via MCP", "filesystem.write_file", {"path": "/x"},
                read_only=False, execute=execute)
    return get_approval_queue().list(status=ApprovalStatus.PENDING)[0]


def test_list_pending(api_client, secured):
    action = _queue_one(Mock(return_value="ok"))
    r = api_client.get("/approvals", headers={"X-API-Key": EXEC})
    assert r.status_code == 200
    ids = [a["id"] for a in r.json()["approvals"]]
    assert action.id in ids


def test_approve_executes_and_records_approver(api_client, secured):
    execute = Mock(return_value="written")
    action = _queue_one(execute)
    r = api_client.post(f"/approvals/{action.id}/approve", headers={"X-API-Key": EXEC})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "executed"
    assert body["decided_by"]
    execute.assert_called_once()


def test_reject(api_client, secured):
    execute = Mock()
    action = _queue_one(execute)
    r = api_client.post(f"/approvals/{action.id}/reject", json={"reason": "not now"},
                        headers={"X-API-Key": EXEC})
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"
    execute.assert_not_called()


def test_double_approve_is_conflict(api_client, secured):
    action = _queue_one(Mock(return_value="ok"))
    api_client.post(f"/approvals/{action.id}/approve", headers={"X-API-Key": EXEC})
    r = api_client.post(f"/approvals/{action.id}/approve", headers={"X-API-Key": EXEC})
    assert r.status_code == 409


def test_unknown_approval_is_404(api_client, secured):
    r = api_client.post("/approvals/nope/approve", headers={"X-API-Key": EXEC})
    assert r.status_code == 404


def test_non_admin_cannot_approve(api_client, secured):
    execute = Mock()
    action = _queue_one(execute)
    r = api_client.post(f"/approvals/{action.id}/approve", headers={"X-API-Key": "k-sales"})
    assert r.status_code == 403
    execute.assert_not_called()
