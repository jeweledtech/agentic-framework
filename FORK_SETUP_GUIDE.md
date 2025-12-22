# Fork Setup Guide

**Your Complete Guide to Getting Started After Forking JeweledTech-Desktop**

This guide walks you through everything you need to do after forking the repository to get your private AI workforce up and running.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Configuration](#configuration)
4. [Running the Framework](#running-the-framework)
5. [Validating Your Installation](#validating-your-installation)
6. [Understanding the Architecture](#understanding-the-architecture)
7. [Creating Your First Custom Agent](#creating-your-first-custom-agent)
8. [Implementing Department Agents](#implementing-department-agents)
9. [Connecting Your LLM](#connecting-your-llm)
10. [Setting Up Knowledge Bases](#setting-up-knowledge-bases)
11. [API Integration](#api-integration)
12. [Production Deployment](#production-deployment)
13. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have the following installed:

### Required
| Requirement | Minimum Version | Recommended | Check Command |
|-------------|-----------------|-------------|---------------|
| Docker | 20.10+ | Latest | `docker --version` |
| Docker Compose | 2.0+ | Latest | `docker compose version` |
| Git | 2.30+ | Latest | `git --version` |

### For Local Development (Optional)
| Requirement | Minimum Version | Recommended | Check Command |
|-------------|-----------------|-------------|---------------|
| Python | 3.11+ | 3.11.x | `python --version` |
| pip | 21.0+ | Latest | `pip --version` |

### Hardware Requirements
- **RAM**: 16GB minimum (32GB recommended)
- **Storage**: 50GB free space
- **GPU**: Modern GPU recommended for optimal LLM performance (not required)
- **OS**: Windows 10/11, macOS, or Linux

---

## Initial Setup

### Step 1: Clone Your Forked Repository

```bash
# Clone your fork (replace YOUR_USERNAME with your GitHub username)
git clone https://github.com/YOUR_USERNAME/agentic-framework.git
cd agentic-framework
```

### Step 2: Create Your Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env
```

### Step 3: Run the Automated Setup (Linux/macOS)

```bash
# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### Step 3 (Alternative): Manual Setup (Windows or if script fails)

```powershell
# Windows PowerShell
Copy-Item .env.example .env

# Pull required Docker images
docker pull ollama/ollama:latest
docker pull python:3.11-slim
```

---

## Configuration

### Essential Environment Variables

Edit your `.env` file to configure the framework:

```bash
# ===========================================
# LLM CONFIGURATION (Start Here)
# ===========================================

# Local LLM with Ollama (Default - Recommended for Privacy)
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2:latest

# Alternative: Use OpenAI API
# OPENAI_API_KEY=your-api-key-here
# LLM_PROVIDER=openai

# ===========================================
# API SERVER CONFIGURATION
# ===========================================
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# ===========================================
# AGENT CONFIGURATION
# ===========================================
AGENT_TIMEOUT=300
AGENT_LOG_LEVEL=INFO

# ===========================================
# SECURITY (Important for Production)
# ===========================================
# API_KEY=your-secure-api-key-here
DEBUG_MODE=false
```

### LLM Model Options

Choose based on your hardware:

| Model | VRAM Required | Best For |
|-------|---------------|----------|
| `llama3.2:1b` | 2GB | Testing, low-resource systems |
| `llama3.2:3b` | 4GB | Light workloads |
| `llama3.2:latest` (7B) | 8GB | **Recommended balance** |
| `mixtral:8x7b` | 24GB+ | Complex reasoning tasks |
| `codellama:13b` | 16GB | Code-focused agents |

---

## Running the Framework

### Option A: Docker Compose (Recommended)

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Option B: Local Development

```bash
# Create and activate virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start Ollama separately (in another terminal)
ollama serve

# Pull your model
ollama pull llama3.2:latest

# Update .env for local development
# OLLAMA_HOST=http://localhost:11434

# Run the API server
python api_server.py
```

### Accessing the Framework

Once running, access these endpoints:

| Endpoint | URL | Purpose |
|----------|-----|---------|
| API Root | http://localhost:8000 | Welcome page |
| API Documentation | http://localhost:8000/docs | Interactive Swagger UI |
| Health Check | http://localhost:8000/health | System status |
| Agent List | http://localhost:8000/agents | Available agents |

---

## Validating Your Installation

### Run the Framework Test

```bash
# With Docker
docker compose exec api python test_framework.py

# Local development
python test_framework.py
```

### Quick Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "agents_available": 2,
  "llm_status": "connected"
}
```

### Test the Example Agents

```bash
# Test Research Agent
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI automation benefits", "depth": "basic"}'

# Test Writer Agent
curl -X POST http://localhost:8000/write \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI in business", "tone": "professional", "word_count": 300}'
```

---

## Understanding the Architecture

### Directory Structure

```
agentic-framework/
├── agents/                    # Your agent implementations go here
│   ├── examples/              # Reference implementations
│   │   ├── research_agent.py  # Research agent example
│   │   └── writer_agent.py    # Writer agent example
│   ├── sales/                 # Sales department agents (create this)
│   ├── marketing/             # Marketing department agents
│   ├── product/               # Product/Engineering agents
│   ├── customer/              # Customer success agents
│   ├── backoffice/            # Operations agents
│   └── security/              # Security & compliance agents
├── core/                      # Framework core (modify carefully)
│   ├── agent.py               # BaseAgent class
│   ├── crew.py                # CrewAI orchestration
│   ├── tools.py               # Tool definitions
│   └── llm_singleton.py       # LLM management
├── knowledge_bases/           # Department knowledge bases
├── tools/                     # Reusable tools
├── docs/                      # Documentation
├── api_server.py              # Main API entry point
└── docker-compose.yml         # Container orchestration
```

### Core Concepts

1. **BaseAgent**: All agents extend this class
2. **Tools**: Capabilities agents can use (web search, file ops, KB queries)
3. **Crews**: Groups of agents working together
4. **Knowledge Bases**: RAG system for domain-specific information

---

## Creating Your First Custom Agent

### Step 1: Create the Agent File

Create `agents/custom/my_first_agent.py`:

```python
"""
My First Custom Agent
A simple agent to demonstrate the framework.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class MyFirstAgent(BaseAgent):
    """A custom agent that performs a specific task."""

    def __init__(self):
        config = AgentConfig(
            name="MyFirstAgent",
            role=AgentRole(
                name="Task Specialist",
                goal="Help users accomplish specific tasks efficiently",
                backstory="""You are a dedicated specialist focused on
                helping users complete their tasks with precision and care.
                You break down complex requests into manageable steps."""
            ),
            tool_names=["knowledge_base_query", "web_search"],
            temperature=0.7,
            verbose=True
        )
        super().__init__(config)

    def perform_task(self, task_description: str) -> str:
        """
        Execute a task based on the description.

        Args:
            task_description: What the user wants to accomplish

        Returns:
            Result of the task execution
        """
        self.add_task(
            description=f"Complete the following task: {task_description}",
            expected_output="A clear, actionable result or response"
        )

        results = self.execute_tasks()
        return results[0] if results else "Task could not be completed"

    def analyze_request(self, request: str) -> dict:
        """
        Analyze a user request and provide structured feedback.

        Args:
            request: The user's request to analyze

        Returns:
            Dictionary with analysis results
        """
        self.add_task(
            description=f"""Analyze this request and provide:
            1. Main objective
            2. Required steps
            3. Potential challenges
            4. Recommended approach

            Request: {request}""",
            expected_output="Structured analysis with clear recommendations"
        )

        results = self.execute_tasks()
        return {
            "request": request,
            "analysis": results[0] if results else "Analysis unavailable",
            "agent": self.config.name
        }
```

### Step 2: Create the Package Init

Create `agents/custom/__init__.py`:

```python
from .my_first_agent import MyFirstAgent

__all__ = ["MyFirstAgent"]
```

### Step 3: Register the Agent in API Server

Add to `api_server.py`:

```python
from agents.custom import MyFirstAgent

# Add endpoint for your agent
@app.post("/custom/task")
async def custom_task(request: dict):
    """Execute a task with MyFirstAgent."""
    agent = MyFirstAgent()
    result = agent.perform_task(request.get("task", ""))
    return {
        "agent": "MyFirstAgent",
        "result": result,
        "timestamp": datetime.now().isoformat()
    }
```

### Step 4: Test Your Agent

```bash
curl -X POST http://localhost:8000/custom/task \
  -H "Content-Type: application/json" \
  -d '{"task": "Create a summary of best practices for customer onboarding"}'
```

---

## Implementing Department Agents

The framework is designed for 58 agents across 6 departments. Here's how to implement them:

### Department Structure Template

```
agents/
├── sales/
│   ├── __init__.py
│   ├── head_of_sales.py           # Department head
│   ├── outbound/
│   │   ├── __init__.py
│   │   ├── manager.py             # Outbound sales manager
│   │   ├── lead_gen.py            # Lead generation agent
│   │   ├── email_outreach.py      # Email campaign agent
│   │   └── crm_update.py          # CRM management agent
│   └── inbound/
│       ├── __init__.py
│       ├── manager.py             # Inbound sales manager
│       ├── lead_prioritization.py # Lead scoring agent
│       └── sequence.py            # Follow-up sequence agent
```

### Department Head Template

Create `agents/sales/head_of_sales.py`:

```python
"""
Head of Sales Agent
Oversees all sales operations and coordinates sales team agents.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class HeadOfSalesAgent(BaseAgent):
    """
    Department head for Sales.
    Coordinates outbound and inbound sales teams.
    """

    def __init__(self):
        config = AgentConfig(
            name="HeadOfSales",
            role=AgentRole(
                name="Head of Sales",
                goal="""Maximize revenue through effective sales team coordination,
                pipeline management, and strategic sales initiatives""",
                backstory="""You are a seasoned sales leader with 15+ years of
                experience building and managing high-performing sales teams.
                You excel at strategy, forecasting, and developing talent.
                You coordinate between outbound prospecting and inbound lead
                management to optimize the entire sales funnel."""
            ),
            tool_names=[
                "knowledge_base_query",
                "file_read",
                "file_write"
            ],
            temperature=0.6,
            verbose=True
        )
        super().__init__(config)

    def review_pipeline(self, pipeline_data: str) -> dict:
        """Review sales pipeline and provide strategic recommendations."""
        self.add_task(
            description=f"""Review this sales pipeline data and provide:
            1. Pipeline health assessment
            2. Bottleneck identification
            3. Revenue forecast
            4. Action items for the team

            Pipeline Data: {pipeline_data}""",
            expected_output="Strategic pipeline analysis with actionable recommendations"
        )
        results = self.execute_tasks()
        return {"analysis": results[0] if results else "Analysis unavailable"}

    def delegate_lead(self, lead_info: dict) -> dict:
        """Determine which team should handle a lead."""
        lead_type = lead_info.get("source", "unknown")

        if lead_type in ["website", "referral", "inbound_call"]:
            return {"team": "inbound", "priority": "high"}
        else:
            return {"team": "outbound", "priority": "medium"}

    def generate_sales_report(self, period: str) -> str:
        """Generate a comprehensive sales report."""
        self.add_task(
            description=f"""Generate a sales report for {period} including:
            - Performance metrics summary
            - Top performers
            - Deals won/lost analysis
            - Recommendations for improvement""",
            expected_output="Comprehensive sales report in markdown format"
        )
        results = self.execute_tasks()
        return results[0] if results else "Report generation failed"
```

### Specialist Agent Template

Create `agents/sales/outbound/lead_gen.py`:

```python
"""
Lead Generation Agent
Identifies and qualifies potential leads for the sales team.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class LeadGenerationAgent(BaseAgent):
    """
    Specialist agent for lead generation and qualification.
    """

    def __init__(self):
        config = AgentConfig(
            name="LeadGenerationAgent",
            role=AgentRole(
                name="Lead Generation Specialist",
                goal="""Identify high-quality leads that match our ideal customer
                profile and provide qualified opportunities to the sales team""",
                backstory="""You are an expert at finding and qualifying potential
                customers. You use research, data analysis, and industry knowledge
                to identify companies and individuals who would benefit from our
                solutions. You understand buyer personas and know how to assess
                fit and timing."""
            ),
            tool_names=[
                "web_search",
                "knowledge_base_query",
                "file_write"
            ],
            temperature=0.5,
            verbose=True
        )
        super().__init__(config)

    def find_leads(self, criteria: dict) -> list:
        """
        Find potential leads based on criteria.

        Args:
            criteria: Dict with industry, size, location, etc.

        Returns:
            List of qualified leads
        """
        industry = criteria.get("industry", "technology")
        company_size = criteria.get("size", "50-500 employees")

        self.add_task(
            description=f"""Research and identify potential leads matching:
            - Industry: {industry}
            - Company Size: {company_size}
            - Additional criteria: {criteria}

            For each lead, provide:
            1. Company name
            2. Why they're a good fit
            3. Potential pain points we can address
            4. Recommended approach""",
            expected_output="List of 5-10 qualified leads with details"
        )

        results = self.execute_tasks()
        return results

    def qualify_lead(self, lead_info: dict) -> dict:
        """
        Qualify a lead using BANT criteria.

        Args:
            lead_info: Information about the lead

        Returns:
            Qualification score and assessment
        """
        self.add_task(
            description=f"""Qualify this lead using BANT criteria:
            - Budget: Can they afford our solution?
            - Authority: Is this the decision maker?
            - Need: Do they have a problem we solve?
            - Timeline: When are they looking to buy?

            Lead Information: {lead_info}""",
            expected_output="BANT qualification with score (1-10) and reasoning"
        )

        results = self.execute_tasks()
        return {
            "lead": lead_info,
            "qualification": results[0] if results else "Unable to qualify"
        }
```

---

## Connecting Your LLM

### Option 1: Ollama (Local, Private - Recommended)

```bash
# Install Ollama (if not using Docker)
# Windows: Download from https://ollama.ai
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# Pull your model
ollama pull llama3.2:latest

# Verify it's running
ollama list
```

Configure in `.env`:
```bash
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

### Option 2: OpenAI API

Configure in `.env`:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
```

### Option 3: Custom GGUF Models

1. Download your GGUF model
2. Create a Modelfile:
```
FROM /path/to/your/model.gguf
PARAMETER temperature 0.7
PARAMETER num_ctx 4096
```

3. Create the model in Ollama:
```bash
ollama create my-custom-model -f Modelfile
```

4. Update `.env`:
```bash
OLLAMA_MODEL=my-custom-model
```

---

## Setting Up Knowledge Bases

Knowledge bases provide domain-specific information to your agents.

### Creating a Department Knowledge Base

1. Create the directory structure:
```bash
mkdir -p knowledge_bases/sales/documents
mkdir -p knowledge_bases/sales/templates
```

2. Add your documents:
```
knowledge_bases/
└── sales/
    ├── documents/
    │   ├── sales_playbook.md
    │   ├── objection_handling.md
    │   ├── pricing_guide.md
    │   └── competitor_analysis.md
    └── templates/
        ├── proposal_template.md
        └── follow_up_email.md
```

3. Create an index file `knowledge_bases/sales/index.yaml`:
```yaml
department: sales
description: Sales team knowledge base
categories:
  - name: playbooks
    path: documents/sales_playbook.md
    description: Core sales methodologies and processes
  - name: objections
    path: documents/objection_handling.md
    description: Common objections and responses
  - name: pricing
    path: documents/pricing_guide.md
    description: Pricing strategies and negotiation
  - name: competitors
    path: documents/competitor_analysis.md
    description: Competitive intelligence
```

### Using Knowledge Bases in Agents

```python
from core.agent import BaseAgent, AgentConfig, AgentRole


class SalesAgent(BaseAgent):
    def __init__(self):
        config = AgentConfig(
            name="SalesAgent",
            role=AgentRole(...),
            tool_names=["knowledge_base_query"],  # Enable KB access
            knowledge_base="sales"  # Specify department KB
        )
        super().__init__(config)
```

---

## API Integration

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome page |
| GET | `/health` | Health check |
| GET | `/agents` | List available agents |
| POST | `/research` | Research agent task |
| POST | `/write` | Writer agent task |
| POST | `/collaborate` | Multi-agent collaboration |
| POST | `/crew/create` | Dynamic crew creation |
| POST | `/chat` | Executive chat interface |

### Example: Multi-Agent Collaboration

```bash
curl -X POST http://localhost:8000/collaborate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Q4 marketing campaign for product launch",
    "output_type": "strategy_document",
    "agents": ["research", "writer"]
  }'
```

### Adding Custom Endpoints

```python
# In api_server.py

from pydantic import BaseModel
from agents.sales import HeadOfSalesAgent

class PipelineReviewRequest(BaseModel):
    pipeline_data: str
    period: str = "current_quarter"

@app.post("/sales/pipeline-review")
async def review_sales_pipeline(request: PipelineReviewRequest):
    """Review sales pipeline with Head of Sales agent."""
    agent = HeadOfSalesAgent()
    result = agent.review_pipeline(request.pipeline_data)
    return {
        "agent": "HeadOfSales",
        "period": request.period,
        "analysis": result,
        "timestamp": datetime.now().isoformat()
    }
```

---

## Production Deployment

### Security Checklist

- [ ] Set `DEBUG_MODE=false` in `.env`
- [ ] Configure `API_KEY` for authentication
- [ ] Use HTTPS in production
- [ ] Review and restrict file access paths
- [ ] Set up proper logging
- [ ] Configure rate limiting
- [ ] Use secrets management for API keys

### Docker Production Configuration

Update `docker-compose.yml` for production:

```yaml
services:
  api:
    restart: always
    environment:
      - DEBUG_MODE=false
      - API_WORKERS=4
    deploy:
      resources:
        limits:
          memory: 4G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Scaling Recommendations

| Scale | API Workers | RAM | Recommendation |
|-------|-------------|-----|----------------|
| Small | 2 | 8GB | Single server |
| Medium | 4 | 16GB | Single server + GPU |
| Large | 8+ | 32GB+ | Load balanced cluster |

---

## Troubleshooting

### Common Issues

#### Docker Won't Start
```bash
# Check Docker status
docker info

# Reset Docker Compose
docker compose down -v
docker compose up --build
```

#### Ollama Connection Failed
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
docker compose restart ollama
```

#### Agent Timeout Errors
```bash
# Increase timeout in .env
AGENT_TIMEOUT=600

# Or use a smaller model
OLLAMA_MODEL=llama3.2:1b
```

#### Memory Issues
```bash
# Check Docker memory allocation
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Or use a smaller model
```

### Getting Help

1. Check the [docs/](docs/) folder for detailed documentation
2. Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
3. Open an issue on GitHub for bugs or feature requests

---

## Next Steps

1. **Explore the Examples**: Study `agents/examples/` to understand patterns
2. **Build Your First Agent**: Follow the template above
3. **Set Up Knowledge Bases**: Add your business documents
4. **Implement Department Agents**: Build out your 58-agent workforce
5. **Deploy to Production**: Follow the security checklist

---

## Quick Reference

### Start Services
```bash
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f api
```

### Test Health
```bash
curl http://localhost:8000/health
```

### Run Tests
```bash
python test_framework.py
```

---

**Your Business. Your Data. Your Technology.**

For questions and support, please open an issue on the repository.
