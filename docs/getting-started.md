# Getting Started with JeweledTech Agentic Framework

Welcome to the JeweledTech Agentic Framework! This guide will walk you through setting up and using the framework to build your own multi-agent AI systems.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- 8GB RAM minimum (16GB recommended for optimal performance)
- Basic understanding of REST APIs

## Installation Methods

### Method 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/jeweledtech/agentic-framework.git
   cd agentic-framework
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env if you need custom configuration
   ```

3. **Start the framework**
   ```bash
   docker-compose up
   ```

   This will:
   - Pull and start Ollama with the configured model
   - Build and start the API server
   - Set up networking between services

4. **Verify installation**
   ```bash
   # Check API health
   curl http://localhost:8000/health
   
   # View API documentation
   open http://localhost:8000/docs
   ```

### Method 2: Local Development

1. **Clone and setup**
   ```bash
   git clone https://github.com/jeweledtech/agentic-framework.git
   cd agentic-framework
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install and start Ollama**
   ```bash
   # Visit https://ollama.ai for installation instructions
   ollama serve
   ollama pull llama3.2:latest
   ```

3. **Configure and run**
   ```bash
   cp .env.example .env
   # Update OLLAMA_HOST=http://localhost:11434 in .env
   python api_server.py
   ```

## First Agent Interaction

### 1. Research Something

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "artificial general intelligence",
    "depth": "medium"
  }'
```

### 2. Generate Content

```bash
curl -X POST http://localhost:8000/write \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The impact of AI on education",
    "tone": "professional",
    "word_count": 500
  }'
```

### 3. Multi-Agent Collaboration

```bash
curl -X POST http://localhost:8000/collaborate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Sustainable technology",
    "output_type": "blog_post"
  }'
```

## Using the Demo UI

Open `demo-ui/index.html` in your browser or serve it with:

```bash
python -m http.server 3000 --directory demo-ui
```

Then visit `http://localhost:3000`

## Creating Your First Custom Agent

1. Create a new file in `agents/custom/my_agent.py`:

```python
from core.agent import BaseAgent, AgentConfig, AgentRole, AgentTools

class MyAnalystAgent(BaseAgent):
    def __init__(self):
        config = AgentConfig(
            id="my_analyst",
            role=AgentRole(
                name="Data Analyst",
                description="Analyzes data and provides insights",
                goal="Transform data into actionable insights",
                backstory="Expert analyst with years of experience"
            ),
            tools=AgentTools(tool_names=["web_search"])
        )
        super().__init__(config)
    
    def analyze(self, data):
        self.add_task(
            f"Analyze this data: {data}",
            "Comprehensive analysis with insights"
        )
        results = self.execute_tasks()
        return results[0] if results else "No analysis"
```

2. Add your agent to the API server:

```python
# In api_server.py
from agents.custom.my_agent import MyAnalystAgent

analyst_agent = MyAnalystAgent()

@app.post("/analyze")
async def analyze_data(data: str):
    result = analyst_agent.analyze(data)
    return {"analysis": result}
```

## Configuration Options

### Environment Variables

- `OLLAMA_HOST`: Ollama server address (default: localhost:11434)
- `MODEL_PATH`: LLM model to use (default: llama3.2:3b)
- `USE_MOCK_KB`: Use mock knowledge base (default: false)
- `API_PORT`: API server port (default: 8000)

### Available Models

The framework works with any Ollama-supported model:

```bash
# Faster, smaller model
ollama pull llama3.2:1b

# More capable model
ollama pull llama3.2:7b

# Update .env
MODEL_PATH=llama3.2:7b
```

## Troubleshooting

### API won't start
- Check if port 8000 is already in use
- Ensure Ollama is running: `ollama list`

### Slow responses
- First request pulls the model (can take time)
- Consider using a smaller model
- Ensure adequate RAM is available

### Docker issues
- Ensure Docker daemon is running
- Check Docker Compose version (2.0+ required)
- Verify port mappings in docker-compose.yml

## Next Steps

- Read the [Agent Development Guide](../knowledge_bases/examples/agent_development_guide.md)
- Explore example agents in `agents/examples/`
- Join our [Discord community](https://discord.gg/jeweledtech)
- Check out [JeweledTech Enterprise](https://jeweledtech.com/enterprise) for production features

## Getting Help

- 📖 [Documentation](https://github.com/jeweledtech/agentic-framework/wiki)
- 💬 [GitHub Discussions](https://github.com/jeweledtech/agentic-framework/discussions)
- 🐛 [Report Issues](https://github.com/jeweledtech/agentic-framework/issues)
- 📧 [Contact Support](mailto:admin@jeweledtech.com)