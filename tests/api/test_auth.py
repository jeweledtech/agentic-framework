"""API tests for API key authentication enable/disable."""

import pytest


class TestAuthDisabled:
    def test_protected_endpoint_no_auth(self, api_client):
        """When auth is disabled, protected endpoints work without API key."""
        response = api_client.post("/sales/process-lead", json={
            "lead_name": "Test",
            "lead_email": "test@test.com",
            "lead_company": "Test Co",
        })
        assert response.status_code == 200


class TestAuthEnabled:
    def test_protected_endpoint_requires_key(self, api_client, auth_env):
        """When auth is enabled, missing API key returns 403."""
        response = api_client.post("/sales/process-lead", json={
            "lead_name": "Test",
            "lead_email": "test@test.com",
            "lead_company": "Test Co",
        })
        assert response.status_code == 403

    def test_protected_endpoint_wrong_key(self, api_client, auth_env):
        """When auth is enabled, wrong API key returns 403."""
        response = api_client.post(
            "/sales/process-lead",
            json={
                "lead_name": "Test",
                "lead_email": "test@test.com",
                "lead_company": "Test Co",
            },
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 403

    def test_protected_endpoint_correct_key(self, api_client, auth_env):
        """When auth is enabled, correct API key grants access."""
        response = api_client.post(
            "/sales/process-lead",
            json={
                "lead_name": "Test",
                "lead_email": "test@test.com",
                "lead_company": "Test Co",
            },
            headers={"X-API-Key": "test-api-key-12345"},
        )
        assert response.status_code == 200

    def test_unprotected_endpoints_work(self, api_client, auth_env):
        """Public endpoints like / and /health work regardless of auth."""
        assert api_client.get("/").status_code == 200
        assert api_client.get("/health").status_code == 200
        assert api_client.get("/agents").status_code == 200
