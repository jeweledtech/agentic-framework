# n8n Integration Setup Guide for Agentic System

This guide provides step-by-step instructions for setting up all the integrations needed for your n8n workflows, organized by department and prioritized for MVP implementation.

## 📋 Table of Contents

1. [MVP Phase - Essential Free Tools](#mvp-phase---essential-free-tools)
2. [Department-Specific Setup](#department-specific-setup)
3. [Security Tools Setup](#security-tools-setup)
4. [Testing Your Integrations](#testing-your-integrations)
5. [Troubleshooting](#troubleshooting)
6. [Future Upgrades](#future-upgrades)

## 🎯 MVP Phase - Essential Free Tools

### Prerequisites

1. **n8n Instance**: Either self-hosted or n8n.cloud
2. **Domain**: For webhooks and OAuth callbacks
3. **SSL Certificate**: Required for OAuth and webhooks

### Core Infrastructure Setup

#### 1. PostgreSQL Database
```bash
# Using Docker
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=agentic_db \
  -p 5432:5432 \
  postgres:14

# Connect via PostgreSQL Command Line (psql)
docker exec -it postgres psql -U postgres -d agentic_db

# Create database schema
psql -h localhost -U postgres -d agentic_db < database/schema.sql
```

#### 2. Supabase Setup
1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Get credentials from Settings > API:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_KEY`

#### 3. Ollama (Local LLM) - Docker Compose Setup (Recommended)

**Option A: Docker Compose with n8n (Recommended)**

Create a `docker-compose.yml` file to manage all services together:

```yaml
version: '3.8'
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    environment:
      - OLLAMA_ORIGINS=http://localhost:5678,http://n8n:5678
      - OLLAMA_HOST=0.0.0.0:11434
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - WEBHOOK_URL=http://localhost:5678/
      - OLLAMA_HOST=http://ollama:11434  # Internal connection
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - ollama
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:14
    container_name: postgres
    environment:
      - POSTGRES_PASSWORD=yourpassword
      - POSTGRES_DB=agentic_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  ollama_data:
  n8n_data:
  postgres_data:
```

Then run:
```bash
# Start all services
docker-compose up -d

# Pull required models
docker exec -it ollama ollama pull llama3:8b
docker exec -it ollama ollama pull codellama:34b

# Verify Ollama is accessible
curl http://localhost:11434/api/tags

# Test from n8n container
docker exec -it n8n curl http://ollama:11434/api/tags
```

**Option B: Standalone Installation**

If you prefer to run Ollama outside Docker:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Configure to accept external connections
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS=http://localhost:5678

# Start Ollama service
ollama serve

# In another terminal, pull models
ollama pull llama3:8b
ollama pull codellama:34b
```

**n8n Configuration for Ollama:**
- When using Docker Compose: Use `http://ollama:11434` as the base URL
- When using standalone: Use `http://host.docker.internal:11434` (Mac/Windows) or `http://172.17.0.1:11434` (Linux)

## 📧 Email Services Setup

### Understanding Email Usage in the System

**1. Transactional Emails (Resend)**
- **Purpose**: Automated emails from jeweledtech.com (assessment confirmations, proposals)
- **Triggered by**: Supabase database events
- **Configuration**: Already in your jeweledtech.com backend
- **n8n Integration**: Optional - for webhook processing and advanced workflows

**2. Department Emails (Gmail SMTP)**
- **Purpose**: Internal communications, sales outreach, support responses
- **Used by**: Sales, Support, Marketing departments in n8n workflows
- **Configuration**: Required for n8n email nodes

### Resend Setup (For jeweledtech.com)
If you want n8n to process Resend webhooks or send additional emails:

1. Get your Resend API key from [resend.com/api-keys](https://resend.com/api-keys)
2. Configure webhook endpoint (optional):
   ```
   https://your-n8n-domain.com/webhook/resend-events
   ```
3. Add to environment:
   ```
   RESEND_API_KEY=re_your_api_key
   RESEND_FROM_EMAIL=noreply@jeweledtech.com
   RESEND_WEBHOOK_SECRET=your_webhook_secret
   ```

### Gmail SMTP (For Department Emails)
1. Enable 2-factor authentication on your Gmail account
2. Generate App Password:
   - Go to [Google Account Settings](https://myaccount.google.com)
   - Security > 2-Step Verification > App passwords
   - Generate password for "Mail"
3. Configure in n8n:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

## 📧 Sales Department Setup

### HubSpot CRM (Free)
1. Sign up at [hubspot.com](https://www.hubspot.com/products/get-started)
2. Navigate to Settings > Integrations > API Key
3. Generate Private App:
   - Name: "n8n Integration"
   - Scopes: CRM (all), Marketing (read)
4. Copy API Key to `HUBSPOT_API_KEY`

### Google Calendar
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable Calendar API:
   ```
   APIs & Services > Library > Search "Calendar API" > Enable
   ```
4. Create OAuth2 credentials:
   - APIs & Services > Credentials > Create Credentials > OAuth client ID
   - Application type: Web application
   - Authorized redirect URIs: `https://your-n8n-domain.com/oauth2/callback`
5. Download credentials and extract:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`

## 📱 Marketing Department Setup

### Buffer (Free Plan)
1. Sign up at [buffer.com](https://buffer.com)
2. Go to Account > Apps > Create New App
3. Get Access Token from app settings
4. Add to `BUFFER_ACCESS_TOKEN`

### Google Analytics
1. Go to [Google Analytics](https://analytics.google.com)
2. Admin > Property > Data Streams
3. Create API credentials:
   - [Google Cloud Console](https://console.cloud.google.com)
   - Enable Analytics Reporting API
   - Create Service Account
   - Download JSON key
4. Extract `GA_API_KEY` from JSON

### WordPress.com (Free)
1. Create account at [wordpress.com](https://wordpress.com)
2. My Sites > Manage > Settings > Security
3. Generate Application Password
4. Use as `WORDPRESS_API_KEY`

### Mailchimp (Free - up to 500 contacts)
1. Sign up at [mailchimp.com](https://mailchimp.com)
2. Account > Extras > API keys
3. Create new API key
4. Server prefix is in your account URL (e.g., us1, us2)

## 💻 Engineering Department Setup

### GitHub
1. Go to [GitHub Settings](https://github.com/settings/tokens)
2. Generate new token (classic)
3. Select scopes:
   - repo (all)
   - workflow
   - read:org
4. Copy token to `GITHUB_TOKEN`

### Uptime Kuma (Self-hosted)
```bash
# Using Docker
docker run -d \
  --name uptime-kuma \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  louislam/uptime-kuma:1

# Access at http://localhost:3001
# Create admin account
# Generate API key in Settings
```

### Sentry (Free tier)
1. Sign up at [sentry.io](https://sentry.io)
2. Create new project
3. Settings > Projects > Your Project > Client Keys
4. Copy DSN to `SENTRY_DSN`

## 🎧 Customer Support Setup

### Freshdesk (Free)
1. Sign up at [freshdesk.com](https://freshdesk.com/signup)
2. Choose subdomain (yourcompany.freshdesk.com)
3. Profile > Profile Settings > API Key
4. Copy to `FRESHDESK_API_KEY`

### Tawk.to (Completely Free)
1. Sign up at [tawk.to](https://www.tawk.to)
2. Add website property
3. Administration > API
4. Get Property ID and Widget ID

### GitBook (Free Plan)
1. Sign up at [gitbook.com](https://www.gitbook.com)
2. Create space for knowledge base
3. Settings > Integrations > Create token
4. Note Space ID from URL

## 💰 Back Office Setup

### Wave Accounting (Free)
1. Sign up at [waveapps.com](https://www.waveapps.com)
2. Settings > API Access
3. Create OAuth application
4. Generate API credentials

### Invoice Ninja (Self-hosted)
```bash
# Using Docker
git clone https://github.com/invoiceninja/dockerfiles.git
cd dockerfiles
docker-compose up -d

# Access at http://localhost:8000
# Complete setup wizard
# Settings > API Tokens > Create
```

### Notion (Free Personal Plan)
1. Create workspace at [notion.so](https://www.notion.so)
2. Settings & Members > Integrations
3. Develop your own integration
4. Get Internal Integration Token
5. Share databases with integration

## 🔒 Security Tools Setup

### Wazuh SIEM (Free & Open Source)
```bash
# Quick deployment with Docker
git clone https://github.com/wazuh/wazuh-docker.git
cd wazuh-docker/single-node
docker-compose up -d

# Access Wazuh dashboard at https://localhost:443
# Default credentials: admin/admin (change immediately!)
# Get API credentials from Management > Security > Roles mapping
```

### OWASP ZAP
```bash
# Using Docker
docker run -d \
  --name zap \
  -p 8090:8090 \
  -p 8080:8080 \
  owasp/zap2docker-stable \
  zap-webswing.sh

# Access at http://localhost:8090
# Generate API key in Tools > Options > API
```

### OpenVAS
```bash
# Using Docker (Greenbone Community Edition)
docker run -d \
  --name openvas \
  -p 9390:9390 \
  -p 443:443 \
  -e PASSWORD=admin \
  mikesplain/openvas

# Access at https://localhost
# Login with admin/admin
```

### Trivy
```bash
# Install Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Run Trivy server
trivy server --listen localhost:4954

# Test connection
curl http://localhost:4954/health
```

### Additional Security Tools

#### Prowler (Cloud Security)
```bash
# Clone repository
git clone https://github.com/prowler-cloud/prowler.git
cd prowler

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

#### Gitleaks (Secrets Detection)
```bash
# Install Gitleaks
brew install gitleaks  # macOS
# or
wget https://github.com/zricethezav/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz
tar -xzf gitleaks_8.18.0_linux_x64.tar.gz

# Create config file
cat > gitleaks.toml << EOF
title = "Gitleaks Config"
[[rules]]
description = "AWS Access Key"
regex = '''AKIA[0-9A-Z]{16}'''
EOF
```

#### Garak (LLM Security)
```bash
# Install Garak
pip install garak

# Run basic scan
garak --model huggingface --model-name gpt2 --probes all
```

## 🧪 Testing Your Integrations

### 1. Test Core Connectivity
```bash
# Test PostgreSQL
psql -h localhost -U postgres -c "SELECT version();"

# Test Ollama
curl http://localhost:11434/api/tags

# Test Supabase
curl https://your-project.supabase.co/rest/v1/ \
  -H "apikey: your-anon-key" \
  -H "Authorization: Bearer your-anon-key"
```

### 2. Test n8n Webhooks
```bash
# Create test webhook in n8n
# Then test with:
curl -X POST https://your-n8n.com/webhook-test/your-webhook-id \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### 3. Test Department Integrations

#### Sales - Test Email
```javascript
// n8n Function node
const nodemailer = require('nodemailer');
const transporter = nodemailer.createTransport({
  host: $env.SMTP_HOST,
  port: $env.SMTP_PORT,
  auth: {
    user: $env.SMTP_USER,
    pass: $env.SMTP_PASSWORD
  }
});

return await transporter.verify();
```

#### Marketing - Test Buffer
```bash
curl https://api.bufferapp.com/1/user.json \
  -H "Authorization: Bearer your-access-token"
```

#### Security - Test Wazuh
```bash
curl -k -u wazuh_api_user:password \
  https://localhost:55000/agents?pretty
```

## 🔧 Troubleshooting

### Common Issues

1. **OAuth Redirect Errors**
   - Ensure redirect URI matches exactly
   - Use HTTPS for production
   - Check domain whitelist in service settings

2. **API Rate Limits**
   - Implement exponential backoff
   - Cache responses where possible
   - Use webhook triggers instead of polling

3. **Connection Timeouts**
   - Check firewall rules
   - Verify service is running
   - Test with curl/postman first

4. **Authentication Failures**
   - Regenerate API keys/tokens
   - Check token expiration
   - Verify correct scopes/permissions

### Debug Mode

Enable n8n debug logging:
```bash
export N8N_LOG_LEVEL=debug
n8n start
```

## 🚀 Future Upgrades

As your business grows, consider upgrading to:

### Sales
- **Salesforce**: Full CRM suite with advanced automation
- **Outreach.io**: AI-powered sales engagement
- **Gong.io**: Revenue intelligence platform

### Marketing
- **HubSpot Marketing Hub**: Complete marketing automation
- **Marketo**: Enterprise marketing platform
- **SEMrush**: Professional SEO toolkit

### Engineering
- **Jira**: Advanced project management
- **Datadog**: Full-stack monitoring
- **GitLab**: Complete DevOps platform

### Customer Support
- **Zendesk**: Enterprise help desk
- **Intercom**: Conversational support platform
- **Gainsight**: Customer success platform

### Back Office
- **NetSuite**: Complete ERP solution
- **Workday**: HR and finance platform
- **SAP**: Enterprise resource planning

### Security
- **Splunk**: Enterprise SIEM
- **CrowdStrike**: EDR platform
- **Qualys**: Cloud security platform

## 📝 Best Practices

1. **Security**
   - Use OAuth2 over API keys when possible
   - Rotate credentials regularly
   - Implement least privilege access
   - Use environment-specific credentials

2. **Performance**
   - Cache frequently accessed data
   - Use webhooks instead of polling
   - Implement rate limiting
   - Monitor API usage

3. **Reliability**
   - Implement retry logic
   - Set up monitoring alerts
   - Create fallback mechanisms
   - Regular backup credentials

4. **Documentation**
   - Document all custom integrations
   - Keep credentials in secure vault
   - Maintain integration inventory
   - Track API version changes

## 🆘 Getting Help

- **n8n Community**: [community.n8n.io](https://community.n8n.io)
- **n8n Documentation**: [docs.n8n.io](https://docs.n8n.io)
- **Service-Specific Docs**: Check each service's API documentation
- **Security Tools**: Most have active communities and forums

Remember to start with the free tools for MVP and gradually upgrade as your needs and budget grow!