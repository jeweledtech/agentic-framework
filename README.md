# JeweledTech Agentic OS: Your Business-in-a-Box

Build, automate, and scale your entire company with a digital workforce. JeweledTech's Agentic OS is an open-source framework for scaffolding a complete enterprise, from sales and marketing to product development and back-office operations, and a complete security as a service department using a hierarchy of collaborative AI agents.

This isn't just another AI agent creation tool. It's a blueprint for architecting a fully functional, scalable business where AI agents act as department heads, managers, and specialized workers, all orchestrated to achieve your strategic goals. It's designed for entrepreneurs, startups, and SMBs who need to scale efficiently without the immediate overhead of a large human workforce.

---

## Framework at a Glance

| Metric | Count |
|--------|-------|
| **Departments** | 7 |
| **AI Agents** | 15+ |
| **n8n Workflows** | 87 |
| **Tool Integrations** | 10+ |

---

## Bring Your Own Orchestration

The framework is **orchestration-agnostic** — it calls your LLM directly by default, with no external agent framework required. Need more sophisticated multi-agent workflows? Plug in your preferred orchestration layer:

| Mode | Install | Best For |
|------|---------|----------|
| **Direct LLM** (default) | `pip install -r requirements.txt` | Single-agent tasks, simple pipelines, minimal dependencies |
| **CrewAI** (optional) | `pip install -r requirements-crewai.txt` | Multi-agent crews with process management |
| **Mock** (testing) | Set `USE_MOCK_KB=true` | Demo mode, CI/CD, no LLM needed |

All agents work identically regardless of mode — the orchestration layer only affects how multi-agent crews coordinate.

---

## LLM Providers

| Provider | Install | Default Model | Best For |
|----------|---------|---------------|----------|
| Ollama | `pip install "jeweledtech-agentic-framework[ollama]"` | llama3:8b | Local development |
| Anthropic | `pip install "jeweledtech-agentic-framework[anthropic]"` | claude-sonnet-4-20250514 | Production (cost-efficient) |
| OpenAI | `pip install "jeweledtech-agentic-framework[openai]"` | gpt-4o | OpenAI ecosystem |
| LiteLLM | `pip install "jeweledtech-agentic-framework[litellm]"` | (configurable) | Multi-provider routing |
| Mock | (built-in) | mock_model | Testing / CI |

**Heritage business deployments:** For client-facing work requiring highest quality, use `claude-opus-4-6`:
```python
from core.providers.llm import AnthropicProvider
provider = AnthropicProvider(model="claude-opus-4-6")
```

---

## Complete Organization Chart

![JeweledTech Agentic Framework - Organization Chart](docs/images/org-chart.png)

*7 departments with specialized AI agents and n8n workflow integrations*

---

## The 7 Departments

### 1. Executive Department
**Chief Executive Agent** - The central orchestrator that coordinates all department agents, makes strategic decisions, and provides business guidance.

### 2. Sales Department
| Agent | Description | Tools |
|-------|-------------|-------|
| Inbound Sales Manager | Qualifies inbound leads, routes to appropriate reps | HubSpot |
| Outbound Sales Manager | Email campaigns, lead generation, cold outreach | Gmail, SMTP |
| Sales Lead Agent | Scores leads against ICP, prioritizes prospects | HubSpot CRM |
| Outreach Agent | Personalized sequences, follow-up emails | Resend, Gmail |

### 3. Marketing Department
| Agent | Description | Tools |
|-------|-------------|-------|
| Content Marketing Agent | Blog posts, social content, SEO optimization | Notion, Social APIs |
| Campaign Agent | Campaign management, ROI analysis, A/B testing | Analytics |

### 4. Engineering Department
| Agent | Description | Tools |
|-------|-------------|-------|
| Engineering Agent | Triages issues, manages bug reports, feature requests | GitHub |
| Product Agent | Roadmap planning, feature prioritization | Jira |

### 5. Customer Department
| Agent | Description | Tools |
|-------|-------------|-------|
| Customer Support Agent | Handles tickets, provides solutions | Freshdesk |
| Escalation Agent | Manages escalations, SLA compliance | Slack |

### 6. BackOffice Department
| Agent | Description | Tools |
|-------|-------------|-------|
| Invoice Agent | Generates invoices, tracks payments | Wave |
| Finance Agent | Financial reporting, expense tracking | QuickBooks |

### 7. Security Department
| Agent | Description | Tools |
|-------|-------------|-------|
| Security Agent | Monitors alerts, detects threats | Wazuh |
| Audit Agent | Security audits, compliance checks | Logging |

---

## n8n Workflow Integration

The framework includes **87 pre-built n8n workflows** for business process automation:

```
┌─────────────────────────────────────────────────────────────────┐
│                     n8n Cloud Instance                          │
│              https://your-instance.app.n8n.cloud                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │   Webhooks   │   │  Workflows   │   │ Credentials  │        │
│  │  /sales-*    │   │  87 total    │   │  HubSpot     │        │
│  │  /marketing  │   │              │   │  Gmail/SMTP  │        │
│  │  /proposal   │   │              │   │  Supabase    │        │
│  └──────┬───────┘   └──────┬───────┘   └──────────────┘        │
│         │                  │                                    │
│         └────────┬─────────┘                                    │
│                  │                                              │
│         ┌────────▼────────┐                                     │
│         │  Instance MCP   │◄──── MCP Tools                      │
│         │  /mcp-server/   │      search_workflows               │
│         └────────┬────────┘      execute_workflow               │
│                  │               get_workflow_details           │
└──────────────────┼──────────────────────────────────────────────┘
                   │
          ┌────────▼────────┐
          │    Framework    │
          │   API Server    │
          │  localhost:8080 │
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │   Agent Engine  │
          │  7 Departments  │
          │   15+ Agents    │
          └─────────────────┘
```

### Workflow Categories

| Department | Workflows | Key Automations |
|------------|-----------|-----------------|
| Sales | 6+ | Lead processing, ICP qualification, proposal nurturing |
| Marketing | 5+ | Content distribution, social posting, email campaigns |
| Engineering | 3+ | Issue triage, bug tracking, feature requests |
| Customer | 3+ | Ticket handling, escalations, SLA monitoring |
| BackOffice | 3+ | Invoice generation, payment tracking |
| Security | 3+ | Threat detection, incident response |

---

## Demo UI

The framework includes a visual demo interface at `demo-ui/index.html`:

**Features:**
- Interactive org chart visualization
- Agent discovery with filtering by department
- n8n workflow browser
- Live API testing ("Try It Out")
- Real-time API status indicator

**To view the demo:**
```bash
# Start the API server
python api_server.py

# Open in browser
open demo-ui/index.html
```

---

## Quick Start

### Option 1: Local Development (Mock Mode)

```bash
# Clone the repository
git clone https://github.com/JeweledTech/agentic-framework.git
cd agentic-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies (no CrewAI needed)
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Start API server (mock mode - no LLM required)
USE_MOCK_KB=true python api_server.py
```

### Option 2: With Ollama (Full AI — Direct LLM)

```bash
# Start Ollama
ollama serve

# Pull a model
ollama pull llama3.1

# Start API server (uses direct LLM calls by default)
python api_server.py
```

### Option 3: With CrewAI (Multi-Agent Crews)

```bash
# Install optional CrewAI dependencies
pip install -r requirements-crewai.txt

# Start API server (CrewAI auto-detected)
python api_server.py
```

### Option 4: Docker Deployment

```bash
# Development
docker compose up -d

# Production (with GPU support)
docker compose -f docker-compose.production.yml up -d
```

---

## API Endpoints

Once running, access the API at `http://localhost:8080`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and agent count |
| `/agents` | GET | List all available agents |
| `/research` | POST | Research a topic |
| `/write` | POST | Generate content |
| `/collaborate` | POST | Multi-agent collaboration |
| `/chat` | POST | Executive chat interface |
| `/crew/create` | POST | Create agent crew (requires CrewAI) |
| `/docs` | GET | Interactive API documentation |

---

## Configuration

### Environment Variables

```env
# LLM Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# n8n Integration
N8N_HOST=https://your-instance.app.n8n.cloud
N8N_MCP_TOKEN=your_jwt_token

# Development
USE_MOCK_KB=true  # Enable mock mode for testing
DEBUG_MODE=true
```

---

## Project Structure

```
agentic-framework/
├── agents/
│   ├── sales/           # Sales department agents
│   ├── marketing/       # Marketing department agents
│   ├── examples/        # Research & Writer agents
│   └── executive_chat.py
├── core/
│   ├── agent.py         # BaseAgent class (direct LLM + optional CrewAI)
│   ├── crew.py          # Crew orchestration (framework-agnostic)
│   ├── llm_singleton.py # LLM management
│   └── tools.py         # Tool implementations
├── n8n_workflows/       # 87 workflow templates
│   ├── phase5/          # Advanced nurture sequences
│   └── README.md        # Import instructions
├── demo-ui/
│   └── index.html       # Visual demo interface
├── docs/
│   └── images/          # Documentation images
├── api_server.py        # FastAPI server
├── docker-compose.yml   # Development deployment
├── docker-compose.production.yml  # Production w/ GPU
├── requirements.txt     # Core dependencies
└── requirements-crewai.txt  # Optional CrewAI deps
```

---

## Forked the Repository?

If you've forked this repository and want a complete guide on setting up your environment, implementing custom agents, and building out your workforce:

- **[Fork Setup Guide](FORK_SETUP_GUIDE.md)** - Complete setup instructions
- **[Agent Templates](AGENT_TEMPLATES.md)** - Ready-to-use agent templates

---

## Enterprise & SaaS Options

The Community Edition provides the foundational engine. For businesses ready to scale:

- **JeweledTech Enterprise**: Complete multi-department digital workforce with all specialized agents, advanced autonomous capabilities, and full n8n automation workflows.

- **JeweledTech SaaS Platform**: Fully managed, multi-tenant cloud platform. Get all the power of Enterprise with the convenience of SaaS.

Learn more at [jeweledtech.com](https://jeweledtech.com)

---

## Contributing

We welcome contributions from the community!

- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[GitHub Issues](https://github.com/JeweledTech/agentic-framework/issues)** - Report bugs or request features

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Framework-agnostic agent engine built with FastAPI, Ollama, and n8n**

*Let's build the future of the enterprise, together.*
