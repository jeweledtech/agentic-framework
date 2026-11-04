"""Unit tests for API key authentication and principal resolution (core/auth.py)."""

import pytest

from core.auth import (
    AuthNotConfiguredError,
    auth_enabled,
    authenticate,
    load_api_keys,
)
from core.security import (
    DEPARTMENT_HEAD,
    DEPARTMENT_MEMBER,
    EXECUTIVE,
    Permission,
    role_has_permission,
)


class TestAuthEnabledDefault:
    def test_auth_enabled_when_env_unset(self, monkeypatch):
        """Auth fails closed: if ENABLE_AUTH is not set, auth is ON."""
        monkeypatch.delenv("ENABLE_AUTH", raising=False)
        assert auth_enabled() is True

    def test_auth_disabled_only_when_explicitly_false(self, monkeypatch):
        monkeypatch.setenv("ENABLE_AUTH", "false")
        assert auth_enabled() is False

    @pytest.mark.parametrize("value", ["true", "1", "yes", "", "garbage"])
    def test_any_other_value_means_enabled(self, monkeypatch, value):
        monkeypatch.setenv("ENABLE_AUTH", value)
        assert auth_enabled() is True


class TestLoadApiKeys:
    def test_multi_key_config_maps_keys_to_departments(self, monkeypatch):
        monkeypatch.delenv("FRAMEWORK_API_KEY", raising=False)
        monkeypatch.setenv("FRAMEWORK_API_KEYS", "k-exec:executive, k-sales:sales")
        keys = load_api_keys()
        assert keys["k-exec"] == "executive"
        assert keys["k-sales"] == "sales"

    def test_legacy_single_key_is_executive(self, monkeypatch):
        monkeypatch.delenv("FRAMEWORK_API_KEYS", raising=False)
        monkeypatch.setenv("FRAMEWORK_API_KEY", "legacy-key")
        assert load_api_keys() == {"legacy-key": "executive"}

    def test_no_keys_configured(self, monkeypatch):
        monkeypatch.delenv("FRAMEWORK_API_KEYS", raising=False)
        monkeypatch.delenv("FRAMEWORK_API_KEY", raising=False)
        assert load_api_keys() == {}

    def test_malformed_entry_rejected(self, monkeypatch):
        monkeypatch.setenv("FRAMEWORK_API_KEYS", "no-department-here")
        with pytest.raises(ValueError):
            load_api_keys()


class TestAuthenticate:
    @pytest.fixture(autouse=True)
    def keys(self, monkeypatch):
        monkeypatch.setenv("ENABLE_AUTH", "true")
        monkeypatch.delenv("FRAMEWORK_API_KEY", raising=False)
        monkeypatch.setenv("FRAMEWORK_API_KEYS", "k-exec:executive,k-sales:sales")

    def test_valid_key_returns_principal_with_role(self):
        p = authenticate("k-sales")
        assert p.department == "sales"
        assert p.role == DEPARTMENT_MEMBER

    def test_principal_key_id_does_not_contain_raw_key(self):
        p = authenticate("k-exec")
        assert "k-exec" not in p.key_id
        assert p.key_id

    def test_invalid_key_returns_none(self):
        assert authenticate("wrong") is None

    def test_missing_key_returns_none(self):
        assert authenticate(None) is None
        assert authenticate("") is None

    def test_enabled_without_keys_raises(self, monkeypatch):
        monkeypatch.delenv("FRAMEWORK_API_KEYS", raising=False)
        with pytest.raises(AuthNotConfiguredError):
            authenticate("anything")

    def test_disabled_returns_dev_principal(self, monkeypatch):
        monkeypatch.setenv("ENABLE_AUTH", "false")
        p = authenticate(None)
        assert p.key_id == "auth-disabled"


class TestRolePermissionImplication:
    def test_api_all_implies_api_admin(self):
        assert role_has_permission(EXECUTIVE, Permission.API_ADMIN)

    def test_tool_all_implies_tool_use(self):
        assert role_has_permission(EXECUTIVE, Permission.TOOL_USE)

    def test_member_lacks_admin(self):
        assert not role_has_permission(DEPARTMENT_MEMBER, Permission.API_ADMIN)
        assert not role_has_permission(DEPARTMENT_MEMBER, Permission.API_WRITE)

    def test_head_has_write_not_admin(self):
        assert role_has_permission(DEPARTMENT_HEAD, Permission.API_WRITE)
        assert not role_has_permission(DEPARTMENT_HEAD, Permission.API_ADMIN)
