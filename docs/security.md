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

## API Authentication and Enforcement

Authentication **fails closed**:

- Auth is ON unless `ENABLE_AUTH=false` is set explicitly (local development only; the server logs a warning).
- If auth is on and no API key is configured, the server **refuses to start**, and any protected request returns `503`.
- Every route except `GET /` and `GET /health` requires an `X-API-Key` header. Missing or invalid key → `401`; valid key without the needed permission → `403`. Both are written to the audit log (`api.auth.failure`, `security.permission_denied`).
- `tests/api/test_route_protection.py` enumerates every route in the app, so an endpoint added without a permission check fails CI.

### API keys and roles

Each key is bound to a department, and the department's role (see the mapping above) decides what the key can do:

```bash
FRAMEWORK_API_KEYS="<exec-key>:executive,<n8n-key>:admin,<sales-key>:sales,<mkt-key>:marketing"
```

The legacy single `FRAMEWORK_API_KEY` still works and is treated as an `executive` key. Keys are compared in constant time and only a hashed key id (`key-<sha256 prefix>`) is ever logged.

### Route permissions

| Route | Required permission | Who has it by default |
|---|---|---|
| `GET /`, `GET /health` | none (public) | everyone |
| `GET /agents` | `api:read` | every department |
| `POST /research`, `/write`, `/collaborate`, `/chat`, `/chat/analyze`, `/chat/reset` | `agent:execute` | every department |
| `POST /sales/*` | `agent:execute` **and** department `sales` | sales, executive |
| `POST /marketing/*` | `agent:execute` **and** department `marketing` | marketing, executive |
| `POST /n8n/webhook` | `api:write` | admin, security (department heads), executive |
| `POST /crew/create` | `agent:create` | executive |
| `GET /approvals`, `POST /approvals/{id}/approve`, `POST /approvals/{id}/reject` | `api:admin` | executive |

Wildcard permissions imply their specific forms (`api:*` → `api:read`/`api:write`/`api:admin`, `tool:*` → `tool:use`, `kb:read:*` → `kb:read:own`).

Chat history is kept per caller: sessions are keyed by `(API key id, conversation_id)`, capped at 50 messages each and 1,000 sessions total. `/chat/reset` only clears the caller's own session.

## Human Approval of Agent Actions

Agents can't take an action with outside effects on their own. Every MCP call (`MCPSuperAssistantTool`) and every n8n call (`N8NMCPTool`) passes through `core/approvals.py:gate_action`, and so do the email, CRM and sequence tools.

- **Read-only** remote functions run immediately. They are listed explicitly in `MCP_READ_ONLY_FUNCTIONS` and `N8N_READ_ONLY_TOOLS` in `core/tools.py`.
- **Everything else** is queued instead: triggering or executing workflows, writing files, sending email, publishing, updating CRM or Notion records, payroll, invoices, CI/CD and so on. The agent receives `PENDING_HUMAN_APPROVAL: ... (approval id <id>)`, and nothing is sent.
- A human with `api:admin` reviews the queue (`GET /approvals?status=pending`) and approves or rejects each action. An approved action runs **once**, immediately. A rejected or expired action never runs.
- Pending actions expire after `APPROVAL_TTL_SECONDS` (default 24h).
- Every request, approval, rejection and execution result is audited (`approval.requested`, `approval.approved`, `approval.rejected`, `approval.executed`), with the requesting and approving key ids.

Because the gate sits at the transport layer, any new MCP or n8n tool requires approval by default. To exempt a remote function, add it to the read-only allowlist, and only if it cannot change anything.

**Limitations:** the queue lives in process memory. A restart drops pending actions; they fail safe, meaning they never run. With multiple replicas, approve through the same instance that queued the action (use sticky sessions or a single replica for the API). `REQUIRE_HUMAN_APPROVAL=false` turns the gate off and is meant for local development only.

| Environment Variable | Default | Description |
|---|---|---|
| `ENABLE_AUTH` | `true` | Set to `false` to disable API auth (development only) |
| `FRAMEWORK_API_KEYS` | *(none)* | Comma-separated `key:department` pairs |
| `FRAMEWORK_API_KEY` | *(none)* | Legacy single key, treated as `executive` |
| `REQUIRE_HUMAN_APPROVAL` | `true` | Set to `false` to let agents run side-effecting tools without approval (development only) |
| `APPROVAL_TTL_SECONDS` | `86400` | How long a pending action can be approved |

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
