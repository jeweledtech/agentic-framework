# JeweledTech Agentic Framework

## Quick Reference

- `python3 -m pytest tests/ -v --tb=short` — Run test suite (278 tests, all passing)
- `python3 -m pytest tests/ --cov=core --cov=api_server --cov-report=term-missing` — Run with coverage
- `pip install -e ".[dev]"` — Dev install (no LLM backend needed)
- `pip install -e ".[dev,ollama]"` — Dev install with Ollama support
- `USE_MOCK_KB=true` and `ENABLE_AUTH=false` are set automatically by tests/conftest.py
- Use `python3` not `python` (system has python3 only)

## Architecture

Multi-department agentic framework with RBAC, provider abstraction, and optional CrewAI orchestration.

### Key Directories
- `core/` — Framework core: agents, providers, security, audit, tools, LLM singleton
- `core/providers/` — Vendor abstraction: LLM, VectorStore, Workflow interfaces + registries
- `core/security.py` — RBAC with Permission enum, Role model, AccessControl class
- `core/audit.py` — Structured JSON-lines audit logging via AuditLogger singleton
- `api_server.py` — FastAPI server with audit middleware, version from core/_version.py
- `tests/` — Unit (tests/unit/), integration (tests/integration/), API (tests/api/)
- `knowledge_bases/` — Per-department KB directories with markdown files
- `agents/` — YAML agent definitions per department

### Provider Pattern
ABC interface → concrete providers → thread-safe singleton registry → env var override.
- `LLM_PROVIDER=ollama|mock|litellm` (auto-detects if unset)
- `VECTORSTORE_PROVIDER=chromadb|filesystem|mock`
- `WORKFLOW_PROVIDER=n8n|mock`
- Registries must be reset between tests (handled by conftest.py reset_singletons fixture)

### Patterns & Conventions
- Pydantic v2: use `model_config = {"frozen": True}` not `class Config`
- Optional deps use try/except import with graceful fallback (see CrewAI pattern in core/agent.py)
- Version single source of truth: `core/_version.py`
- Tests run with zero external services (mock KB, mock LLM, TestClient for API)
- Auth fails closed (ENABLE_AUTH defaults true). Every new route needs `Depends(require(Permission.X))` — tests/api/test_route_protection.py enforces it
- Side-effecting MCP/n8n calls go through core/approvals.py gate_action; only add a remote function to MCP_READ_ONLY_FUNCTIONS / N8N_READ_ONLY_TOOLS if it cannot change anything

## Completed Work

### Phase 1: Foundation (completed 2026-02-20)
Plan file: `.claude/plans/curious-floating-book.md`
- Step 1: Vendor abstraction layer — core/providers/ with LLM, VectorStore, Workflow interfaces
- Step 2: Pip-installable package — pyproject.toml with optional dep groups, agentic-server CLI
- Step 3a: Comprehensive test suite — 181 tests across unit/integration/API
- Step 3b: Security model — RBAC (core/security.py) + audit logging (core/audit.py)
- Step 4: Tagged releases — CI with coverage, release workflow (test→version verify→build→GitHub Release→PyPI→Docker)

## TODO — Future Phases
- Phase 1 addressed: testing, security, packaging, releases, vendor lock-in
- Remaining gaps from OpenClaw comparison need to be planned as Phase 2+
