"""
Workflow Engine Provider Interface — Bring Your Own Workflow Engine

Abstract base class and built-in implementations for workflow engine providers.
Users can implement WorkflowProvider to add Temporal, Prefect, Airflow, or
any other workflow engine.

Built-in providers:
- N8NProvider: Wraps current n8n MCP integration
- MockWorkflowProvider: Returns canned results for testing

Configuration:
  WORKFLOW_PROVIDER=n8n          (default — requires n8n MCP server)
  WORKFLOW_PROVIDER=mock         (for testing)
  WORKFLOW_PROVIDER=<custom>     (any registered provider name)
"""

import json
import logging
import os
import threading
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class WorkflowProvider(ABC):
    """Abstract interface for workflow engines. Implement this to bring your own."""

    @abstractmethod
    def trigger_workflow(self, workflow_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a workflow by ID with the given parameters."""
        ...

    @abstractmethod
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List available workflows."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this provider is currently reachable/usable."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable name for this provider."""
        ...


class WorkflowRegistry:
    """Register and retrieve workflow providers by name."""

    _instance: Optional["WorkflowRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "WorkflowRegistry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._providers: Dict[str, Type[WorkflowProvider]] = {}
                    inst._instances: Dict[str, WorkflowProvider] = {}
                    cls._instance = inst
        return cls._instance

    def register(self, name: str, provider_class: Type[WorkflowProvider]) -> None:
        self._providers[name] = provider_class

    def get(self, name: Optional[str] = None, **kwargs) -> WorkflowProvider:
        if name is None:
            name = os.environ.get("WORKFLOW_PROVIDER", "").lower() or "n8n"

        if name not in self._providers:
            raise KeyError(
                f"Workflow provider '{name}' not registered. "
                f"Available: {self.list_providers()}"
            )

        if name not in self._instances:
            with self._lock:
                if name not in self._instances:
                    self._instances[name] = self._providers[name](**kwargs)

        return self._instances[name]

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())

    def reset(self) -> None:
        with self._lock:
            self._instances.clear()

    @classmethod
    def reset_singleton(cls) -> None:
        with cls._lock:
            cls._instance = None


# ---------------------------------------------------------------------------
# Built-in provider implementations
# ---------------------------------------------------------------------------


class N8NProvider(WorkflowProvider):
    """Workflow provider that integrates with n8n via MCP protocol (JSON-RPC over HTTP)."""

    def __init__(
        self,
        mcp_url: Optional[str] = None,
        mcp_token: Optional[str] = None,
    ):
        self._mcp_url = mcp_url or os.getenv(
            "N8N_MCP_SERVER_URI", "https://localhost/mcp-server/http"
        )
        self._mcp_token = mcp_token or os.getenv("N8N_MCP_TOKEN", "")

    @property
    def provider_name(self) -> str:
        return "n8n"

    def is_available(self) -> bool:
        try:
            import requests
            headers = {"Content-Type": "application/json"}
            if self._mcp_token:
                headers["Authorization"] = f"Bearer {self._mcp_token}"

            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/list",
                "params": {},
            }
            resp = requests.post(
                self._mcp_url, json=payload, headers=headers, timeout=10
            )
            return resp.status_code == 200
        except Exception:
            return False

    def _call_mcp(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        import requests

        request_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self._mcp_token:
            headers["Authorization"] = f"Bearer {self._mcp_token}"

        response = requests.post(
            self._mcp_url, json=payload, headers=headers, timeout=60
        )
        response.raise_for_status()

        # Parse SSE format
        result_data = None
        for line in response.text.split("\n"):
            if line.startswith("data: "):
                try:
                    result_data = json.loads(line[6:])
                    break
                except json.JSONDecodeError:
                    continue

        if result_data is None:
            try:
                result_data = response.json()
            except json.JSONDecodeError:
                return {"error": f"Could not parse response: {response.text[:200]}"}

        if "error" in result_data:
            return {"error": result_data["error"]}

        return result_data.get("result", result_data)

    def trigger_workflow(self, workflow_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_mcp(
            "tools/call",
            {"name": "execute_workflow", "arguments": {"workflowId": workflow_id, "inputData": params}},
        )

    def list_workflows(self) -> List[Dict[str, Any]]:
        result = self._call_mcp("tools/list", {})
        if isinstance(result, list):
            return result
        if isinstance(result, dict) and "tools" in result:
            return result["tools"]
        return [result] if result else []


class MockWorkflowProvider(WorkflowProvider):
    """Mock workflow provider for testing."""

    def __init__(self):
        self._triggered: List[Dict[str, Any]] = []

    @property
    def provider_name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    def trigger_workflow(self, workflow_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            "workflow_id": workflow_id,
            "params": params,
            "status": "completed",
            "result": f"Mock execution of workflow {workflow_id}",
        }
        self._triggered.append(record)
        return record

    def list_workflows(self) -> List[Dict[str, Any]]:
        return [
            {"id": "mock-workflow-1", "name": "Mock Sales Workflow", "active": True},
            {"id": "mock-workflow-2", "name": "Mock Marketing Workflow", "active": True},
        ]


# ---------------------------------------------------------------------------
# Auto-register built-in providers
# ---------------------------------------------------------------------------

def _register_builtins() -> None:
    registry = WorkflowRegistry()
    registry.register("n8n", N8NProvider)
    registry.register("mock", MockWorkflowProvider)


_register_builtins()
