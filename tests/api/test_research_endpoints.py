"""API tests for /research, /write, /collaborate endpoints."""

import pytest


class TestResearchEndpoint:
    def test_research_topic(self, api_client):
        response = api_client.post("/research", json={
            "topic": "AI in coaching industry",
            "depth": "medium",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "research_agent"
        assert data["status"] == "completed"

    def test_research_default_depth(self, api_client):
        response = api_client.post("/research", json={
            "topic": "Market trends",
        })
        assert response.status_code == 200


class TestWriteEndpoint:
    def test_write_content(self, api_client):
        response = api_client.post("/write", json={
            "topic": "Benefits of AI coaching",
            "tone": "professional",
            "word_count": 500,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "writer_agent"
        assert data["status"] == "completed"


class TestCollaborateEndpoint:
    def test_collaborate_blog_post(self, api_client):
        response = api_client.post("/collaborate", json={
            "topic": "Future of coaching technology",
            "output_type": "blog_post",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["collaboration"] == "research_and_write"
        assert "research_phase" in data
        assert "writing_phase" in data
