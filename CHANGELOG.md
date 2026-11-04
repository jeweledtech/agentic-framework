# Changelog

All notable changes to the JeweledTech Agentic Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security

- **Authentication now fails closed.** `ENABLE_AUTH` defaults to `true`; the server refuses to start when auth is on and no API key is configured.
- **Every route except `/` and `/health` requires an API key.** Previously `/chat`, `/chat/analyze`, `/chat/reset`, `/research`, `/write`, `/collaborate`, `/crew/create` and `/agents` were unauthenticated.
- **RBAC is enforced on every endpoint.** API keys map to departments via `FRAMEWORK_API_KEYS`; each route requires a `Permission`, and `/sales/*` and `/marketing/*` are restricted to their department (or executive).
- **Human approval for side-effecting agent actions.** n8n workflow triggers and executions, MCP writes (files, email, calendar, CRM, Notion, publishing, payroll, CI/CD, ...), and the email, CRM and sequence tools are queued and only run after an `api:admin` key approves them via `/approvals`. Requests and decisions are audited.
- Chat history is isolated per caller and bounded (50 messages per session, 1,000 sessions); `/chat/reset` only clears the caller's own session.
- A route-enumeration test fails CI if an endpoint is added without a permission check.

### Changed

- Missing or invalid API key now returns `401` (was `403`); `403` now means "authenticated but not permitted".
- `GET /agents` now requires an API key.

## [0.1.0] - 2026-02-20

### Added

- **Vendor Abstraction Layer** — Provider interfaces for LLM, vector store, and workflow engines
  - `LLMProvider` ABC with built-in Ollama, Mock, and LiteLLM providers
  - `VectorStoreProvider` ABC with built-in ChromaDB, FileSystem, and Mock providers
  - `WorkflowProvider` ABC with built-in n8n and Mock providers
  - Registry pattern for each provider type with auto-detection and env var override
  - Bring-your-own-anything: subclass any provider ABC and register it
- **Pip-installable package** via `pyproject.toml`
  - Package name: `jeweledtech-agentic-framework`
  - Optional dependency groups: `[ollama]`, `[litellm]`, `[openai]`, `[crewai]`, `[chromadb]`, `[dev]`, `[docs]`, `[all]`
  - `agentic-server` CLI entry point
  - Minimal base dependencies — no LLM-specific packages required
- **Role-Based Access Control (RBAC)** in `core/security.py`
  - `Permission` enum with granular `resource:action:scope` format
  - Pre-defined roles: `DEPARTMENT_MEMBER`, `DEPARTMENT_HEAD`, `EXECUTIVE`
  - `AccessControl` class enforcing department-level data isolation
  - Default security policy mapping 9 departments to roles
- **Structured audit logging** in `core/audit.py`
  - `AuditEventType` enum with 14 event categories
  - `AuditEvent` Pydantic model with auto-generated timestamps and correlation IDs
  - Thread-safe `AuditLogger` singleton with JSON-lines output
  - Audit middleware for all API requests
- **Comprehensive test suite** — 181 tests across unit, integration, and API layers
  - Unit tests for agents, crew, communication, tools, LLM singleton, KB interface, providers, security, and audit
  - Integration tests for agent delegation, communication flows, and crew execution
  - API tests for health, chat, research, sales, and authentication endpoints
  - Shared test fixtures with automatic singleton reset between tests
- **CI improvements** — Coverage reporting, pyproject.toml-based install
- **Semantic versioning** — Single source of truth in `core/_version.py`
- **CHANGELOG.md** — This file

### Changed

- `core/llm_singleton.py` — Delegates to `LLMRegistry` when `LLM_PROVIDER` env var is set
- `core/agent.py` — Accepts optional `llm_provider` parameter; integrates RBAC and audit logging
- `api_server.py` — Dynamic version from `core._version`, audit middleware, `main()` entry point
- `requirements.txt` — Removed unused `litellm` and `openai` from base dependencies

### Removed

- Hard dependency on `litellm` and `openai` (moved to optional groups)
- `sys.path.append` hack in `api_server.py`
