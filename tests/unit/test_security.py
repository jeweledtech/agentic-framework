"""Unit tests for RBAC permissions (core/security.py)."""

import pytest
from core.security import (
    AccessControl,
    Permission,
    Role,
    SecurityPolicy,
    DEPARTMENT_MEMBER,
    DEPARTMENT_HEAD,
    EXECUTIVE,
    DEFAULT_POLICY,
)


class TestPermissionEnum:
    def test_permission_values(self):
        assert Permission.KB_READ_OWN == "kb:read:own"
        assert Permission.KB_READ_ALL == "kb:read:*"
        assert Permission.AGENT_EXECUTE == "agent:execute"

    def test_permission_is_string(self):
        assert isinstance(Permission.TOOL_USE, str)


class TestRole:
    def test_department_member_role(self):
        assert Permission.KB_READ_OWN in DEPARTMENT_MEMBER.permissions
        assert Permission.KB_READ_ALL not in DEPARTMENT_MEMBER.permissions

    def test_executive_role(self):
        assert Permission.KB_READ_ALL in EXECUTIVE.permissions
        assert Permission.API_ALL in EXECUTIVE.permissions
        assert Permission.AGENT_CREATE in EXECUTIVE.permissions

    def test_department_head_role(self):
        assert Permission.AGENT_DELEGATE in DEPARTMENT_HEAD.permissions
        assert Permission.KB_READ_ALL not in DEPARTMENT_HEAD.permissions

    def test_custom_role(self):
        role = Role(
            name="custom",
            permissions={Permission.KB_READ_OWN, Permission.API_READ},
        )
        assert Permission.KB_READ_OWN in role.permissions
        assert Permission.TOOL_ALL not in role.permissions


class TestAccessControl:
    def test_check_permission_sales(self):
        ac = AccessControl()
        assert ac.check_permission("sales", Permission.KB_READ_OWN) is True
        assert ac.check_permission("sales", Permission.KB_READ_ALL) is False

    def test_check_permission_executive(self):
        ac = AccessControl()
        assert ac.check_permission("executive", Permission.KB_READ_ALL) is True
        assert ac.check_permission("executive", Permission.API_ALL) is True

    def test_kb_access_same_department(self):
        ac = AccessControl()
        assert ac.check_kb_access("sales", "sales") is True

    def test_kb_access_cross_department_denied(self):
        ac = AccessControl()
        assert ac.check_kb_access("sales", "engineering") is False

    def test_kb_access_executive_cross_department(self):
        ac = AccessControl()
        assert ac.check_kb_access("executive", "sales") is True
        assert ac.check_kb_access("executive", "marketing") is True

    def test_list_accessible_departments_member(self):
        ac = AccessControl()
        depts = ac.list_accessible_departments("sales")
        assert depts == ["sales"]

    def test_list_accessible_departments_executive(self):
        ac = AccessControl()
        depts = ac.list_accessible_departments("executive")
        assert "sales" in depts
        assert "marketing" in depts
        assert len(depts) > 1

    def test_get_role_for_unknown_department(self):
        ac = AccessControl()
        role = ac.get_role_for_department("unknown_dept_xyz")
        # Falls back to DEPARTMENT_MEMBER
        assert role == DEPARTMENT_MEMBER

    def test_custom_policy(self):
        policy = SecurityPolicy(
            department_roles={"special": EXECUTIVE}
        )
        ac = AccessControl(policy=policy)
        assert ac.check_permission("special", Permission.KB_READ_ALL) is True

    def test_admin_is_department_head(self):
        ac = AccessControl()
        role = ac.get_role_for_department("admin")
        assert Permission.AGENT_DELEGATE in role.permissions
