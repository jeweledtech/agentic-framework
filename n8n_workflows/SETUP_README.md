# n8n Workflows Setup for Agentic System

This directory contains everything needed to run n8n workflows with your agentic system, using your existing `.env` configuration.

## 📁 Directory Contents

- **Workflow Files** (`*.json`) - Pre-built n8n workflows for each department
- **`.env.n8n.example`** - Template with all n8n-specific environment variables
- **`docker-compose.n8n.yml`** - Complete Docker stack for n8n + dependencies
- **`merge_env_vars.sh`** - Script to merge n8n variables into your existing `.env`
- **`department_integrations.json`** - Complete mapping of departments to tools
- **`INTEGRATION_SETUP_GUIDE.md`** - Detailed setup instructions for each service
- **`MVP_QUICK_START.md`** - 30-minute quick start guide

## 🚀 Quick Setup (Using Existing .env)

Since you already have an `.env` file in the parent directory, here's the streamlined setup:

### 1. Merge n8n Variables
```bash
cd n8n_workflows
./merge_env_vars.sh
```

This will:
- Backup your existing `../.env` file
- Add all n8n-specific variables from `.env.n8n.example`
- Preserve your existing configuration

### 2. Configure Essential Services
Edit `../.env` and add credentials for at least these MVP services:

```bash
# Email (Required for most workflows)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password  # Get from Google App Passwords

# n8n Security (Change these!)
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-secure-password

# Already in your .env (verify these exist):
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
```

### 3. Start Everything
```bash
# From n8n_workflows directory
docker-compose -f docker-compose.n8n.yml --env-file ../.env up -d

# Pull Ollama models
docker exec -it n8n-ollama ollama pull llama3:8b
docker exec -it n8n-ollama ollama pull codellama:34b
```

### 4. Access Services
- **n8n**: http://localhost:5678 (login with N8N_BASIC_AUTH credentials)
- **Ollama API**: http://localhost:11434/api/tags
- **PostgreSQL**: localhost:5432
- **Uptime Kuma**: http://localhost:3001 (optional monitoring)

### 5. Import Workflows
1. Open n8n at http://localhost:5678
2. Go to Workflows → Import from File
3. Import workflows in this order:
   - `1_main_api_workflow.json`
   - `2_chief_ai_agent_workflow.json`
   - Then department workflows as needed

## 🔧 Integration Priority

Start with these free tools for MVP:

1. **Gmail** - Email for all departments (already configured above)
2. **HubSpot Free** - CRM for Sales
3. **GitHub** - Code management for Engineering
4. **Freshdesk Free** - Customer support
5. **Wazuh** - Security monitoring (optional but recommended)

See `MVP_QUICK_START.md` for the complete top 10 list.

## 📋 Common Commands

```bash
# View logs
docker-compose -f docker-compose.n8n.yml logs -f n8n

# Restart n8n after .env changes
docker-compose -f docker-compose.n8n.yml restart n8n

# Stop all services
docker-compose -f docker-compose.n8n.yml down

# Remove all data and start fresh
docker-compose -f docker-compose.n8n.yml down -v
```

## 🔍 Troubleshooting

### Can't connect to Ollama from n8n
- In n8n Ollama credentials, use: `http://ollama:11434`
- Test: `docker exec -it n8n curl http://ollama:11434/api/tags`

### PostgreSQL connection issues
- Verify DATABASE_URL in your .env matches the docker-compose settings
- Default: `postgresql://agentic:yourpassword@postgres:5432/agentic_db`

### Environment variables not loading
- Ensure you're using `--env-file ../.env` flag
- Check for typos in variable names
- Restart services after .env changes

## 📚 Next Steps

1. **Read `INTEGRATION_SETUP_GUIDE.md`** for detailed setup of each service
2. **Follow `MVP_QUICK_START.md`** for the fastest path to a working system
3. **Check `department_integrations.json`** to understand which tools each department uses
4. **Monitor services** with Uptime Kuma at http://localhost:3001

## 🆘 Help & Support

- **n8n Community**: https://community.n8n.io
- **Workflow Issues**: Check the README.md in this directory
- **Integration Help**: See service-specific sections in INTEGRATION_SETUP_GUIDE.md

Remember: Start simple with free tools, test thoroughly, then scale up! 🚀