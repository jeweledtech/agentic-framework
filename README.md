# JeweledTech Agentic OS: Your Business-in-a-Box

Build, automate, and scale your entire company with a digital workforce. JeweledTech's Agentic OS is an open-source framework for scaffolding a complete enterprise, from sales and marketing to product development and back-office operations, and a complete security as a service department using a hierarchy of collaborative AI agents.

This isn't just another AI agent creation tool. It's a blueprint for architecting a fully functional, scalable business where AI agents act as department heads, managers, and specialized workers, all orchestrated to achieve your strategic goals. It's designed for entrepreneurs, startups, and SMBs who need to scale efficiently without the immediate overhead of a large human workforce.

## The Vision: From Startup Idea to Scaled Enterprise, Instantly

Imagine starting a new company. Instead of hiring a full C-suite, department heads, and operational staff, you deploy a pre-built digital enterprise. Your company starts with a fully functional structure, ready to execute on day one:

- **A Head of Sales** that analyzes inbound leads and directs a team of AI agents to qualify them.
- **A Marketing Department** that generates content, manages social media, and nurtures leads.
- **A Product & Engineering Team** that can architect, develop, and test software solutions autonomously.
- **A Back Office** that handles financial reporting and payroll.
- **A Customer Success Team** that onboards new clients and manages support.

This is the power of the JeweledTech Agentic OS. It provides the foundational scaffolding to build this digital workforce, allowing you to focus on strategy and growth while your AI team handles the operations.

## Key Features of the Community Edition

The open-source version provides the core engine for you to start building your digital enterprise:

- **Enterprise Scaffolding**: A complete, hierarchical structure for defining departments, managers, and specialized agents that mirrors a real-world company.
- **Core Agent Engine**: Based on a powerful BaseAgent class and orchestrated with CrewAI, allowing for complex, multi-agent collaboration.
- **Generalist Business Agent**: Includes a pre-built "Business Process Analyst" agent capable of general reasoning, analysis, and tool use to get you started.
- **Local Knowledge Base (RAG)**: Integrated with privateGPT and ChromaDB, allowing your agents to securely learn from your private documents (.pdf, .txt, .md) and build a company-specific knowledge core.
- **Simple Deployment**: A docker-compose.yml setup for a one-command launch of the entire local environment, including the FastAPI server, Ollama for local LLM inference, and a basic chat UI.
- **Extensible by Design**: A clear framework for you to build out your own specialized departments and agents, tailored to your unique business needs.

## How It Works: The Agentic Hierarchy

The system is designed around a familiar corporate structure:

1. **The Chief AI Agent**: The central orchestrator that receives high-level goals.
2. **Department Heads**: Specialized agents (e.g., Head of Sales) that break down goals into department-specific strategies.
3. **Managers & Workers**: Further specialized agents that execute specific tasks (e.g., Inbound Lead Qualifier, Content Writer).
4. **Tools & Knowledge**: All agents have access to a shared set of tools (via MCP-SuperAssistant) and the private knowledge base to ensure they are working with the correct information and capabilities.

This structure allows for complex tasks to be broken down and delegated, just like in a human organization, enabling a level of autonomous operation that goes far beyond simple chatbots.

## Getting Started in 5 Minutes

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jeweledtech/agentic-framework.git
   cd agentic-framework
   ```

2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```
   This will guide you through creating your `.env` file and downloading the necessary models.

3. **Launch your digital enterprise:**
   ```bash
   docker-compose up -d
   ```

4. **Interact with your AI team:**
   Open your browser to `http://localhost:3000` and start giving high-level directives to your new Chief AI Agent.

## The Path to a Fully Autonomous Enterprise

The Community Edition provides the foundational engine. For businesses ready to scale, we offer premium solutions:

- **JeweledTech Enterprise**: The complete, multi-department digital workforce with all specialized agents, advanced autonomous capabilities (AgenticSeek for web research, ACI.dev for software development), and the full suite of n8n automation workflows for a turnkey solution.

- **JeweledTech SaaS Platform**: A fully managed, multi-tenant cloud platform that eliminates the need for you to manage any infrastructure. Get all the power of the Enterprise edition with the convenience of SaaS. Visit [jeweledtech.com](https://jeweledtech.com) for more information!

Learn more about our Enterprise and SaaS offerings at [jeweledtech.com](https://jeweledtech.com)

## Join the Community & Contribute

This is just the beginning. We envision a future where anyone can launch a scalable, efficient, and automated business. We welcome contributions from the community to help us build the future of work.

- **Contribute on GitHub**: Check out our [CONTRIBUTING.md](CONTRIBUTING.md) to get started.
- **Report Issues**: Find a bug? Let us know in the [GitHub Issues](https://github.com/jeweledtech/agentic-framework/issues).
- **Share Your Creations**: Built a new department or a powerful new agent? Share it with the community!

Let's build the future of the enterprise, together.