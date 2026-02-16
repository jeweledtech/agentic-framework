# Contributing to JeweledTech Agentic Framework

First off, thank you for considering contributing to the JeweledTech Agentic Framework! It's people like you that make this framework a great tool for the AI community.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- System information (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- A clear and descriptive title
- Detailed explanation of the proposed feature
- Use cases and examples
- Why this enhancement would be useful to most users

### Pull Requests

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Write or update tests as needed
5. Update documentation
6. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
7. Push to the branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

#### Pull Request Guidelines

- Follow the existing code style
- Include tests for new functionality
- Update documentation as needed
- Keep commits atomic and well-described
- Reference any related issues

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/agentic-framework.git
cd agentic-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install -r requirements.txt

# Optional: Install CrewAI for crew orchestration testing
pip install -r requirements-crewai.txt

# Run tests
pytest

# Run linting
flake8 .
black --check .
```

## Orchestration Modes

The framework supports three execution modes. **All contributions must work in all three modes:**

### 1. Direct LLM (Default)
Agents call Ollama/LiteLLM directly. No CrewAI dependency. This is the path most users will take.

```bash
# Test direct LLM mode
python api_server.py
curl http://localhost:8000/health
```

### 2. CrewAI (Optional)
Multi-agent crews using CrewAI's process orchestration. Only available when `crewai` is installed.

```bash
# Test CrewAI mode
pip install -r requirements-crewai.txt
python api_server.py
```

### 3. Mock (Testing)
No LLM required. Returns demo data. Used in CI/CD and local testing.

```bash
# Test mock mode
USE_MOCK_KB=true python api_server.py
USE_MOCK_KB=true pytest
```

### Writing Mode-Aware Code

When modifying `core/agent.py` or `core/crew.py`, follow this pattern:

```python
# Always check CREWAI_AVAILABLE before using CrewAI classes
if CREWAI_AVAILABLE and self.crew_agent:
    # CrewAI path
    ...
else:
    # Direct LLM path (must always work)
    ...
```

The `CREWAI_AVAILABLE` flag is set at import time in both `core/agent.py` and `core/crew.py`.

## Project Structure

```
agentic-framework/
├── agents/           # Agent implementations
│   └── examples/     # Example agents
├── core/            # Core framework components
├── knowledge_bases/ # Knowledge base system
├── tools/          # Agent tools
├── tests/          # Test suite
└── docs/           # Documentation
```

## Creating New Agents

When creating new example agents:

1. Follow the pattern in `agents/examples/`
2. Ensure agents work with both direct LLM and CrewAI modes
3. Add tests in `tests/agents/`
4. Update documentation

Example:
```python
class MyAgent(BaseAgent):
    """Clear description of what the agent does"""

    def __init__(self, config=None):
        # Agent initialization
        pass

    def perform_task(self, input_data):
        """
        Clear description of the task.
        Works in all execution modes (direct LLM, CrewAI, mock).

        Args:
            input_data: Description of input

        Returns:
            Description of output
        """
        pass
```

## Testing

- Write tests for all new functionality
- Test all three execution modes (direct, CrewAI, mock)
- Maintain test coverage above 80%
- Use meaningful test names
- Include both unit and integration tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_agents.py

# Run in mock mode (CI-friendly, no LLM needed)
USE_MOCK_KB=true pytest
```

## Documentation

- Update README.md for significant changes
- Add docstrings to all functions and classes
- Include examples in documentation
- Keep documentation in sync with code

## Community

- Join our [Discord](https://discord.gg/jeweledtech)
- Participate in [GitHub Discussions](https://github.com/jeweledtech/agentic-framework/discussions)
- Help others in issues and discussions

## Recognition

Contributors will be recognized in:
- The project README
- Release notes
- Our website (with permission)

## Questions?

Feel free to:
- Open an issue with the question label
- Ask in GitHub Discussions
- Reach out on Discord

Thank you for contributing to JeweledTech Agentic Framework!
