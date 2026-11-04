"""
Role-Based Access Control (RBAC) for the JeweledTech Agentic Framework.

Provides department-level permission management to enforce data isolation
between departments. Each department's agents can only access their own
knowledge base by default; executives get cross-department access.

Permission format: "resource:action:scope"
  - kb:read:sales       → read sales knowledge base
  - kb:read:*           → read any department's knowledge base
  - agent:execute       → execute agent tasks
  - agent:delegate      → delegate tasks to child agents
  - tool:*              → use any tool
  - api:*               → access any API endpoint
"""

import logging
from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Set

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """Granular permissions for the framework."""

    # Knowledge base
    KB_READ_OWN = "kb:read:own"
    KB_READ_ALL = "kb:read:*"
    KB_WRITE_OWN = "kb:write:own"
    KB_WRITE_ALL = "kb:write:*"

    # Agent operations
    AGENT_EXECUTE = "agent:execute"
    AGENT_DELEGATE = "agent:delegate"
    AGENT_CREATE = "agent:create"

    # Tool access
    TOOL_USE = "tool:use"
    TOOL_ALL = "tool:*"

    # API access
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_ADMIN = "api:admin"
    API_ALL = "api:*"


class Role(BaseModel):
    """A named role with a set of permissions."""
    model_config = {"frozen": True}

    name: str
    permissions: Set[Permission] = Field(default_factory=set)
    description: str = ""


# Pre-defined roles
DEPARTMENT_MEMBER = Role(
    name="department_member",
    description="Standard department member — own KB access, task execution",
    permissions={
        Permission.KB_READ_OWN,
        Permission.KB_WRITE_OWN,
        Permission.AGENT_EXECUTE,
        Permission.TOOL_USE,
        Permission.API_READ,
    },
)

DEPARTMENT_HEAD = Role(
    name="department_head",
    description="Department head — own KB + delegation + API write",
    permissions={
        Permission.KB_READ_OWN,
        Permission.KB_WRITE_OWN,
        Permission.AGENT_EXECUTE,
        Permission.AGENT_DELEGATE,
        Permission.TOOL_USE,
        Permission.TOOL_ALL,
        Permission.API_READ,
        Permission.API_WRITE,
    },
)

EXECUTIVE = Role(
    name="executive",
    description="Executive — full cross-department access",
    permissions={
        Permission.KB_READ_ALL,
        Permission.KB_WRITE_ALL,
        Permission.AGENT_EXECUTE,
        Permission.AGENT_DELEGATE,
        Permission.AGENT_CREATE,
        Permission.TOOL_ALL,
        Permission.API_ALL,
    },
)


class SecurityPolicy(BaseModel):
    """Maps departments to their default role."""
    model_config = {"arbitrary_types_allowed": True}

    department_roles: Dict[str, Role] = Field(default_factory=dict)


# Default policy: every department gets DEPARTMENT_MEMBER; executive gets EXECUTIVE
DEFAULT_POLICY = SecurityPolicy(
    department_roles={
        "sales": DEPARTMENT_MEMBER,
        "marketing": DEPARTMENT_MEMBER,
        "product": DEPARTMENT_MEMBER,
        "customer": DEPARTMENT_MEMBER,
        "back_office": DEPARTMENT_MEMBER,
        "admin": DEPARTMENT_HEAD,
        "security": DEPARTMENT_HEAD,
        "executive": EXECUTIVE,
        "research": DEPARTMENT_MEMBER,
    }
)

# Departments whose heads get DEPARTMENT_HEAD role
_HEAD_DEPARTMENTS = {"admin", "security"}


class AccessControl:
    """Stateless access control checker.

    Injected into BaseAgent to enforce permission checks at runtime.
    Does not import from agent.py — dependency flows one way.
    """

    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self._policy = policy or DEFAULT_POLICY

    def get_role_for_department(self, department: str) -> Role:
        """Return the role assigned to a department."""
        return self._policy.department_roles.get(department, DEPARTMENT_MEMBER)

    def check_permission(self, department: str, permission: Permission) -> bool:
        """Check whether *department* has *permission*."""
        role = self.get_role_for_department(department)
        return permission in role.permissions

    def check_kb_access(self, agent_department: str, target_department: str) -> bool:
        """Check whether an agent in *agent_department* can read *target_department*'s KB.

        Rules:
        - Agents with KB_READ_ALL can read any KB.
        - Otherwise, agents can only read their own department's KB.
        """
        role = self.get_role_for_department(agent_department)

        if Permission.KB_READ_ALL in role.permissions:
            return True

        return agent_department == target_department

    def list_accessible_departments(self, department: str) -> List[str]:
        """Return the list of departments whose KB *department* can access."""
        role = self.get_role_for_department(department)

        if Permission.KB_READ_ALL in role.permissions:
            return list(self._policy.department_roles.keys())

        return [department]
