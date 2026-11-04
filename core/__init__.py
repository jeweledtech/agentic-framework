"""Core components of JeweledTech Agentic Framework"""

from .agent import BaseAgent, AgentConfig, AgentRole, AgentTools
from .crew import CrewBuilder, AgentLoader, TaskLoader

# Version (single source of truth)
try:
    from core._version import __version__
except ImportError:
    __version__ = "0.0.0-dev"

# Provider interfaces (lazy — don't fail if providers haven't been created yet)
try:
    from core.providers import (
        LLMProvider,
        LLMRegistry,
        VectorStoreProvider,
        VectorStoreRegistry,
        WorkflowProvider,
        WorkflowRegistry,
    )
except ImportError:
    LLMProvider = None
    LLMRegistry = None
    VectorStoreProvider = None
    VectorStoreRegistry = None
    WorkflowProvider = None
    WorkflowRegistry = None

# Security (lazy)
try:
    from core.security import AccessControl
except ImportError:
    AccessControl = None

try:
    from core.audit import AuditLogger, get_audit_logger
except ImportError:
    AuditLogger = None
    get_audit_logger = None

__all__ = [
    # Version
    '__version__',
    # Agent
    'BaseAgent',
    'AgentConfig',
    'AgentRole',
    'AgentTools',
    # Crew
    'CrewBuilder',
    'AgentLoader',
    'TaskLoader',
    # Providers
    'LLMProvider',
    'LLMRegistry',
    'VectorStoreProvider',
    'VectorStoreRegistry',
    'WorkflowProvider',
    'WorkflowRegistry',
    # Security
    'AccessControl',
    'AuditLogger',
    'get_audit_logger',
]
