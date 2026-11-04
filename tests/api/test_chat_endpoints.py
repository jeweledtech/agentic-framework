"""API tests for /chat, /chat/analyze, /chat/reset endpoints."""

import pytest


class TestChatEndpoint:
    def test_chat_basic(self, api_client):
        response = api_client.post("/chat", json={
            "message": "What is our sales strategy?",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "response" in data

    def test_chat_with_conversation_id(self, api_client):
        response = api_client.post("/chat", json={
            "message": "Hello",
            "conversation_id": "conv-123",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == "conv-123"

    def test_chat_with_context(self, api_client):
        response = api_client.post("/chat", json={
            "message": "Analyze this lead",
            "context": {"lead_source": "n8n", "priority": "high"},
        })
        assert response.status_code == 200


class TestChatAnalyzeEndpoint:
    def test_analyze_business_request(self, api_client):
        response = api_client.post("/chat/analyze", json={
            "request": "We need to increase Q2 revenue by 20%",
        })
        assert response.status_code == 200


class TestChatResetEndpoint:
    def test_reset_conversation(self, api_client):
        response = api_client.post("/chat/reset")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
