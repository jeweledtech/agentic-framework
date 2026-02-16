# JeweledTech Agentic Framework - Open Source Release

## What We've Created

This is a production-ready open-source framework for building multi-agent AI systems. The framework provides:

### Core Features
- **Agent Architecture**: BaseAgent class with role-based configuration
- **Framework-Agnostic Orchestration**: Direct LLM execution by default, CrewAI as opt-in
- **Tool System**: Extensible tools for web search, file operations, etc.
- **Knowledge Base Integration**: RAG-ready architecture for enhanced agent intelligence
- **REST API**: FastAPI server with comprehensive endpoints
- **Local LLM Support**: Runs entirely on your infrastructure with Ollama

### Execution Modes
| Mode | Description | Dependencies |
|------|-------------|-------------|
| **Direct LLM** (default) | Agents call Ollama/LiteLLM directly | Core requirements only |
| **CrewAI** (optional) | Multi-agent crews with process orchestration | `requirements-crewai.txt` |
| **Mock** (testing) | Demo responses, no LLM needed | Set `USE_MOCK_KB=true` |

### Example Implementation
- **ResearchAgent**: Demonstrates research, comparison, and fact-checking capabilities
- **WriterAgent**: Shows content generation across multiple formats
- **Collaboration Endpoint**: Multi-agent workflows in action

### Developer Experience
- Docker Compose for one-command startup
- Interactive API documentation
- Demo UI for testing
- Comprehensive getting started guide

## Repository Structure
```
agentic_framework_opensource/
├── agents/                  # Agent implementations
│   ├── __init__.py
│   └── examples/           # Example agents
│       ├── __init__.py
│       ├── research_agent.py
│       └── writer_agent.py
├── core/                   # Core framework
│   ├── __init__.py
│   ├── agent.py           # BaseAgent class (direct LLM + optional CrewAI)
│   ├── crew.py            # Crew orchestration (framework-agnostic)
│   ├── llm_singleton.py   # LLM management
│   └── tools.py           # Tool system
├── knowledge_bases/        # Knowledge management
│   ├── __init__.py
│   ├── kb_interface.py    # RAG interface
│   └── examples/          # Example knowledge
├── tools/                  # Agent tools
│   ├── __init__.py
│   ├── web_search.py
│   └── file_tools.py
├── demo-ui/               # Demo interface
│   └── index.html
├── docs/                  # Documentation
│   └── getting-started.md
├── api_server.py          # FastAPI server
├── docker-compose.yml     # Container orchestration
├── Dockerfile            # Container definition
├── requirements.txt      # Core dependencies (no CrewAI)
├── requirements-crewai.txt # Optional CrewAI dependencies
├── .env.example         # Environment template
├── README.md            # Main documentation
├── CONTRIBUTING.md      # Contribution guide
├── LICENSE              # MIT license
└── .gitignore          # Git ignore rules
```

## Commercial Strategy

The open-source framework serves as both a valuable community tool and a marketing engine for JeweledTech's enterprise offerings:

### Open Source (This Release)
- Core agent framework
- Example agents
- Basic tools
- Local deployment

### Enterprise (Commercial)
- 20+ specialized business agents
- Production Kubernetes deployments
- Advanced workflow orchestration
- CRM/tool integrations
- Professional support
- Custom agent development

## Next Steps for Publishing

1. **Create GitHub Repository**
   ```bash
   # On GitHub: Create new public repo "agentic-framework"

   cd agentic_framework_opensource
   git init
   git add .
   git commit -m "Initial release of JeweledTech Agentic Framework"
   git remote add origin https://github.com/jeweledtech/agentic-framework.git
   git push -u origin main
   ```

2. **Add GitHub Features**
   - Enable Issues and Discussions
   - Create initial issues for community contributions
   - Set up GitHub Actions for CI/CD
   - Add topics: `ai`, `agents`, `multi-agent`, `llm`, `framework`

3. **Community Building**
   - Announce on HackerNews, Reddit r/MachineLearning
   - Create Discord server
   - Write launch blog post
   - Submit to awesome-lists

4. **Marketing Integration**
   - Add framework link to jeweledtech.com
   - Create enterprise comparison page
   - Set up analytics to track conversions
   - Prepare case studies

## Success Metrics

Track these to measure open-source success:
- GitHub stars and forks
- Community contributions
- Enterprise inquiry conversions
- Framework adoption in projects
- Community engagement (Discord, discussions)

This open-source release positions JeweledTech as a thought leader in multi-agent AI systems while creating a natural funnel to enterprise services.
