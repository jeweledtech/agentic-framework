# Security Model

The JeweledTech Agentic Framework enforces department-level data isolation through Role-Based Access Control (RBAC) and records all access decisions via structured audit logging.

## Role-Based Access Control (RBAC)

### Permission Format

Permissions follow a `resource:action:scope` pattern:

| Permission | Description |
|-----------|-------------|
| `kb:read:own` | Read own department's knowledge base |
| `kb:read:*` | Read any department's knowledge base |
| `kb:write:own` | Write to own department's knowledge base |
| `kb:write:*` | Write to any department's knowledge base |
| `agent:execute` | Execute agent tasks |
| `agent:delegate` | Delegate tasks to child agents |
| `agent:create` | Create new agents |
| `tool:use` | Use assigned tools |
| `tool:*` | Use any tool |
| `api:read` | Read API endpoints |
| `api:write` | Write to API endpoints |
| `api:admin` | Administrative API access |
| `api:*` | Full API access |

### Pre-defined Roles

**Department Member** — Standard agents within a department.
- Knowledge base: read/write own department only
- Agents: execute tasks
- Tools: use assigned tools
- API: read-only

**Department Head** — Leads of admin and security departments.
- Everything a member can do, plus:
- Agents: delegate tasks to child agents
- Tools: access all tools
- API: read and write

**Executive** — Cross-department access for leadership.
- Knowledge base: read/write all departments
- Agents: execute, delegate, and create
- Tools: all tools
- API: full access including admin

### Default Department Mapping

| Department | Role |
|-----------|------|
| sales | Department Member |
| marketing | Department Member |
| product | Department Member |
| customer | Department Member |
| back_office | Department Member |
| research | Department Member |
| admin | Department Head |
| security | Department Head |
| executive | Executive |

### Data Isolation

The core security guarantee: **agents can only access their own department's knowledge base** unless they have the `kb:read:*` permission (executives only).

```python
from core.security import AccessControl

ac = AccessControl()

# Sales agent tries to read marketing KB → denied
ac.check_kb_access("sales", "marketing")  # False

# Sales agent reads own KB → allowed
ac.check_kb_access("sales", "sales")  # True

# Executive reads any KB → allowed
ac.check_kb_access("executive", "sales")  # True
```

### Custom Security Policies

Override the default policy to customize department roles:

```python
from core.security import SecurityPolicy, Role, Permission, AccessControl

custom_role = Role(
    name="analyst",
    permissions={Permission.KB_READ_ALL, Permission.AGENT_EXECUTE, Permission.API_READ},
    description="Cross-department read access for analysts",
)

policy = SecurityPolicy(
    department_roles={
        "analytics": custom_role,
        "sales": DEPARTMENT_MEMBER,
        # ... other departments
    }
)

ac = AccessControl(policy=policy)
```

## Audit Logging

All agent actions, KB access, API requests, and security decisions are logged as structured JSON events.

### Event Types

| Event Type | Trigger |
|-----------|---------|
| `agent.task.start` | Agent begins executing a task |
| `agent.task.complete` | Agent finishes a task |
| `agent.task.error` | Agent task fails |
| `agent.delegate` | Agent delegates to another agent |
| `agent.query` | Agent processes a direct query |
| `kb.query` | Knowledge base search |
| `kb.document.access` | Document retrieval |
| `kb.document.create` | Document creation |
| `tool.execute` | Tool invocation |
| `api.request` | Incoming API request |
| `api.response` | API response sent |
| `security.permission_denied` | Access denied by RBAC |
| `security.permission_granted` | Access granted by RBAC |
| `system.error` | System-level error |

### Event Format

Each event is a JSON line with these fields:

```json
{
  "timestamp": "2026-02-20T14:30:00.123456",
  "event_type": "kb.query",
  "actor_id": "sales_agent_001",
  "department": "sales",
  "action": "search",
  "resource": "sales_knowledge_base",
  "details": {"query": "Q1 pipeline", "results": 5},
  "outcome": "success",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `AUDIT_LOG_FILE` | *(none)* | Path to write audit log file. When unset, logs go to stdout only. |

### Usage

```python
from core.audit import get_audit_logger

audit = get_audit_logger()

# Log a KB access
audit.log_kb_access(
    actor_id="sales_agent",
    department="sales",
    action="search",
    resource="sales_kb",
    outcome="success",
    query="pipeline forecast",
)

# Log a permission denial
audit.log_permission_denied(
    actor_id="sales_agent",
    department="sales",
    action="read",
    resource="engineering_kb",
    reason="KB_READ_ALL permission required",
)
```

### Integration Points

Audit logging is automatically integrated at these layers:

1. **API middleware** — Every HTTP request/response is logged with method, path, status code, client IP, and duration.
2. **BaseAgent** — Task execution (`execute_tasks`) and direct queries (`direct_query`) emit start/complete events.
3. **Knowledge base** — Can be instrumented via the `AuditLogger` helper methods.

The `AuditLogger` is a thread-safe singleton, safe for use across concurrent requests in the FastAPI server.
