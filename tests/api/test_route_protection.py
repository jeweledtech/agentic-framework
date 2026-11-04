"""Enforcement tests: every non-public route requires a valid API key and the right role.

These tests enumerate the app's routes, so a new endpoint added without
authentication will fail ``test_every_non_public_route_rejects_missing_key``.
"""

import pytest
from fastapi.routing import APIRoute

KEYS = {
    "exec": "k-exec-111",
    "sales": "k-sales-222",
    "marketing": "k-mkt-333",
    "admin": "k-admin-444",  # department_head role (n8n integration key)
}

PUBLIC_PATHS = {"/", "/health"}

LEAD = {"lead_name": "T", "lead_email": "t@t.com", "lead_company": "T Co"}
MKT = {"action": "generate_content", "parameters": {"topic": "x"}}


@pytest.fixture
def secured(monkeypatch):
    monkeypatch.setenv("ENABLE_AUTH", "true")
    monkeypatch.delenv("FRAMEWORK_API_KEY", raising=False)
    monkeypatch.setenv(
        "FRAMEWORK_API_KEYS",
        f"{KEYS['exec']}:executive,{KEYS['sales']}:sales,"
        f"{KEYS['marketing']}:marketing,{KEYS['admin']}:admin",
    )


def _app_routes():
    from api_server import app
    for route in app.routes:
        if isinstance(route, APIRoute):
            for method in route.methods:
                yield method, route.path


def _concrete(path):
    return path.replace("{action_id}", "does-not-exist")


def test_every_non_public_route_rejects_missing_key(api_client, secured):
    checked = 0
    for method, path in _app_routes():
        if path in PUBLIC_PATHS:
            continue
        r = api_client.request(method, _concrete(path), json={})
        assert r.status_code == 401, f"{method} {path} returned {r.status_code} without a key"
        checked += 1
    assert checked >= 15


def test_every_non_public_route_rejects_wrong_key(api_client, secured):
    for method, path in _app_routes():
        if path in PUBLIC_PATHS:
            continue
        r = api_client.request(method, _concrete(path), json={},
                               headers={"X-API-Key": "wrong"})
        assert r.status_code == 401, f"{method} {path} accepted a wrong key"


def test_public_routes_work_without_key(api_client, secured):
    assert api_client.get("/").status_code == 200
    assert api_client.get("/health").status_code == 200


def test_auth_on_by_default(api_client, monkeypatch):
    """With ENABLE_AUTH unset, protected routes still require a key."""
    monkeypatch.delenv("ENABLE_AUTH", raising=False)
    monkeypatch.setenv("FRAMEWORK_API_KEYS", f"{KEYS['exec']}:executive")
    assert api_client.post("/chat", json={"message": "hi"}).status_code == 401


def test_enabled_but_no_keys_configured_fails_closed(api_client, monkeypatch):
    monkeypatch.setenv("ENABLE_AUTH", "true")
    monkeypatch.delenv("FRAMEWORK_API_KEYS", raising=False)
    monkeypatch.delenv("FRAMEWORK_API_KEY", raising=False)
    r = api_client.post("/chat", json={"message": "hi"}, headers={"X-API-Key": ""})
    assert r.status_code == 503


@pytest.mark.parametrize("who,method,path,body,expected", [
    # Sales routes: sales + executive allowed, marketing denied
    ("sales", "POST", "/sales/process-lead", LEAD, 200),
    ("exec", "POST", "/sales/process-lead", LEAD, 200),
    ("marketing", "POST", "/sales/process-lead", LEAD, 403),
    # Marketing routes: marketing + executive allowed, sales denied
    ("marketing", "POST", "/marketing/generate-content", MKT, 200),
    ("sales", "POST", "/marketing/generate-content", MKT, 403),
    # Crew creation requires AGENT_CREATE (executive only)
    ("sales", "POST", "/crew/create", ["research_agent"], 403),
    # n8n webhook requires API_WRITE (department head / executive)
    ("sales", "POST", "/n8n/webhook",
     {"workflow_id": "w", "trigger_type": "research", "payload": {}}, 403),
    ("admin", "POST", "/n8n/webhook",
     {"workflow_id": "w", "trigger_type": "research", "payload": {}}, 200),
    # Approvals require API_ADMIN (executive only)
    ("admin", "GET", "/approvals", None, 403),
    ("sales", "GET", "/approvals", None, 403),
    ("exec", "GET", "/approvals", None, 200),
    # Basic agent use is open to every authenticated department
    ("sales", "POST", "/chat", {"message": "hi"}, 200),
    ("sales", "GET", "/agents", None, 200),
])
def test_rbac_matrix(api_client, secured, who, method, path, body, expected):
    r = api_client.request(method, path, json=body, headers={"X-API-Key": KEYS[who]})
    assert r.status_code == expected, f"{who} {method} {path}: {r.status_code} {r.text[:200]}"


def test_permission_denial_is_audited(api_client, secured):
    from unittest.mock import patch
    with patch("api_server.get_audit_logger") as gal:
        api_client.post("/sales/process-lead", json=LEAD,
                        headers={"X-API-Key": KEYS["marketing"]})
    assert gal.return_value.log_permission_denied.called


def test_server_refuses_to_start_without_keys(monkeypatch):
    """Startup fails when auth is on and no API keys are configured."""
    from fastapi.testclient import TestClient
    from api_server import app
    monkeypatch.setenv("ENABLE_AUTH", "true")
    monkeypatch.delenv("FRAMEWORK_API_KEYS", raising=False)
    monkeypatch.delenv("FRAMEWORK_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="API key"):
        with TestClient(app):
            pass


def test_server_starts_with_keys(monkeypatch):
    from fastapi.testclient import TestClient
    from api_server import app
    monkeypatch.setenv("ENABLE_AUTH", "true")
    monkeypatch.setenv("FRAMEWORK_API_KEYS", "k:executive")
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
