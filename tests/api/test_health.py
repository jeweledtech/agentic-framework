"""API tests for /, /health, /agents endpoints."""

import pytest


class TestRootEndpoint:
    def test_root_returns_framework_info(self, api_client):
        response = api_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["framework"] == "JeweledTech Agentic Framework"
        assert "version" in data
        assert "endpoints" in data

    def test_root_version_not_hardcoded(self, api_client):
        from core._version import __version__

        response = api_client.get("/")
        data = response.json()
        assert data["version"] == __version__


class TestHealthEndpoint:
    def test_health_check(self, api_client):
        response = api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_health_agents_loaded(self, api_client):
        response = api_client.get("/health")
        data = response.json()
        assert data["agents_loaded"] == 3


class TestAgentsEndpoint:
    def test_list_agents(self, api_client):
        response = api_client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) == 2  # research + writer

    def test_agents_have_capabilities(self, api_client):
        response = api_client.get("/agents")
        data = response.json()
        for agent in data["agents"]:
            assert "id" in agent
            assert "capabilities" in agent
            assert isinstance(agent["capabilities"], list)
