"""API tests for /sales/process-lead, /sales/qualify-lead endpoints."""

import pytest


class TestSalesProcessLead:
    def test_process_lead(self, api_client):
        response = api_client.post("/sales/process-lead", json={
            "lead_name": "Jane Doe",
            "lead_email": "jane@example.com",
            "lead_company": "Acme Coaching",
            "lead_source": "test",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["lead"]["name"] == "Jane Doe"

    def test_process_lead_with_additional_data(self, api_client):
        response = api_client.post("/sales/process-lead", json={
            "lead_name": "John Smith",
            "lead_email": "john@example.com",
            "lead_company": "Growth Co",
            "lead_source": "n8n",
            "additional_data": {"employees": 50, "industry": "coaching"},
        })
        assert response.status_code == 200


class TestSalesQualifyLead:
    def test_qualify_lead(self, api_client):
        response = api_client.post("/sales/qualify-lead", json={
            "lead_id": "lead-001",
            "lead_data": {
                "company": "Elevate Coaching",
                "employees": 12,
                "industry": "coaching",
            },
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["lead_id"] == "lead-001"

    def test_qualify_lead_with_custom_icp(self, api_client):
        response = api_client.post("/sales/qualify-lead", json={
            "lead_id": "lead-002",
            "lead_data": {"company": "Big Corp", "employees": 5000},
            "icp_criteria": {
                "company_size": "5-50 employees",
                "industry": ["coaching"],
            },
        })
        assert response.status_code == 200
        data = response.json()
        assert "icp_criteria_used" in data
