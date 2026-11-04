"""
API key authentication for the JeweledTech Agentic Framework.

Auth fails closed:
  - It is ON unless ``ENABLE_AUTH=false`` is set explicitly.
  - If it is on and no keys are configured, every protected request is refused.

Keys map to a department, and the department's role (core/security.py
DEFAULT_POLICY) decides what the key may do:

    FRAMEWORK_API_KEYS="key1:executive,key2:sales,key3:admin"

The legacy single ``FRAMEWORK_API_KEY`` is still accepted and maps to the
``executive`` department.
"""

import contextvars
import hashlib
import hmac
import os
from dataclasses import dataclass
from typing import Dict, Optional

from core.security import EXECUTIVE, AccessControl, Role


class AuthNotConfiguredError(RuntimeError):
    """Auth is enabled but no API keys are configured."""


@dataclass(frozen=True)
class Principal:
    """The authenticated caller of an API request."""

    key_id: str      # non-reversible identifier, safe to log
    department: str
    role: Role


DEV_PRINCIPAL = Principal(key_id="auth-disabled", department="executive", role=EXECUTIVE)

# Caller of the current request, so deeper layers (e.g. the approval queue)
# can record who asked for an action.
current_principal: contextvars.ContextVar[Optional[Principal]] = contextvars.ContextVar(
    "current_principal", default=None
)


def auth_enabled() -> bool:
    """Auth is on unless ENABLE_AUTH is explicitly 'false'."""
    return os.getenv("ENABLE_AUTH", "true").strip().lower() != "false"


def key_id_for(api_key: str) -> str:
    return "key-" + hashlib.sha256(api_key.encode()).hexdigest()[:12]


def load_api_keys() -> Dict[str, str]:
    """Return {api_key: department} from the environment."""
    keys: Dict[str, str] = {}
    raw = os.getenv("FRAMEWORK_API_KEYS", "").strip()
    if raw:
        for entry in raw.split(","):
            entry = entry.strip()
            if not entry:
                continue
            key, sep, department = entry.rpartition(":")
            if not sep or not key.strip() or not department.strip():
                raise ValueError(
                    "FRAMEWORK_API_KEYS entries must be 'key:department'"
                )
            keys[key.strip()] = department.strip()
    legacy = os.getenv("FRAMEWORK_API_KEY", "").strip()
    if legacy and legacy not in keys:
        keys[legacy] = "executive"
    return keys


def authenticate(api_key: Optional[str]) -> Optional[Principal]:
    """Resolve an API key to a Principal.

    Returns None for a missing or unknown key. Raises AuthNotConfiguredError
    when auth is enabled but no keys exist.
    """
    if not auth_enabled():
        return DEV_PRINCIPAL

    keys = load_api_keys()
    if not keys:
        raise AuthNotConfiguredError(
            "ENABLE_AUTH is on but FRAMEWORK_API_KEYS / FRAMEWORK_API_KEY is not set"
        )
    if not api_key:
        return None

    # Compare against every key in constant time.
    match: Optional[str] = None
    for candidate, department in keys.items():
        if hmac.compare_digest(candidate.encode(), api_key.encode()):
            match = department
    if match is None:
        return None

    role = AccessControl().get_role_for_department(match)
    return Principal(key_id=key_id_for(api_key), department=match, role=role)
