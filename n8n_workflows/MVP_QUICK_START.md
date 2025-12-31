# n8n MVP Quick Start Guide

## 🚀 Essential Integrations for Day 1

### Prerequisites Checklist
- [ ] n8n instance running (self-hosted or cloud)
- [ ] PostgreSQL database set up
- [ ] Supabase project created
- [ ] Ollama installed with llama3:8b model
- [ ] SSL certificate for OAuth callbacks

### 🎯 Top 10 Must-Have Integrations

1. **Email (Gmail)** - All departments need this
   ```bash
   # Get app password from: https://myaccount.google.com/apppasswords
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

2. **CRM (HubSpot Free)** - Sales department
   ```bash
   # Sign up: https://app.hubspot.com/signup/crm
   # Get API key: Settings > Integrations > Private Apps
   HUBSPOT_API_KEY=your-api-key
   ```

3. **Calendar (Google Calendar)** - Sales & Admin
   ```bash
   # Enable API: https://console.cloud.google.com
   # Create OAuth credentials
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-secret
   ```

4. **Code Repository (GitHub)** - Engineering
   ```bash
   # Create token: https://github.com/settings/tokens
   GITHUB_TOKEN=your-personal-access-token
   ```

5. **Help Desk (Freshdesk)** - Customer Support
   ```bash
   # Sign up: https://freshdesk.com/signup
   # Get API key: Profile Settings > API Key
   FRESHDESK_DOMAIN=yourcompany.freshdesk.com
   FRESHDESK_API_KEY=your-api-key
   ```

6. **Accounting (Wave)** - Back Office
   ```bash
   # Sign up: https://www.waveapps.com
   # Create OAuth app: Settings > API Access
   WAVE_API_KEY=your-api-key
   WAVE_BUSINESS_ID=your-business-id
   ```

7. **SIEM (Wazuh)** - Security
   ```bash
   # Quick Docker setup:
   git clone https://github.com/wazuh/wazuh-docker.git
   cd wazuh-docker/single-node && docker-compose up -d
   # Default: admin/admin at https://localhost
   ```

8. **Communication (Slack Free)** - All departments
   ```bash
   # Create app: https://api.slack.com/apps
   # Install to workspace and get tokens
   SLACK_BOT_TOKEN=xoxb-your-token
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/URL
   ```

9. **Knowledge Base (Notion Free)** - All departments
   ```bash
   # Create integration: https://www.notion.so/my-integrations
   # Share databases with integration
   NOTION_API_KEY=your-integration-token
   ```

10. **Database (Supabase)** - Core infrastructure
    ```bash
    # Create project: https://app.supabase.com
    # Get from Settings > API
    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_ANON_KEY=your-anon-key
    ```

## ⚡ 30-Minute Setup Plan

### Step 1: Core Infrastructure (10 min)
1. Run `./merge_env_vars.sh` to add n8n variables to your existing `../.env`
2. Fill in the new n8n-specific credentials in `../.env`
3. Start services with Docker Compose:
   ```bash
   docker-compose -f docker-compose.n8n.yml --env-file ../.env up -d
   ```
4. Pull Ollama models:
   ```bash
   docker exec -it n8n-ollama ollama pull llama3:8b
   ```

### Step 2: Communication & Auth (10 min)
1. Set up Gmail app password
2. Create Slack app and get tokens
3. Set up Google OAuth for Calendar
4. Test email sending

### Step 3: Department Tools (10 min)
1. Sign up for HubSpot Free
2. Create GitHub personal access token
3. Set up Freshdesk account
4. Install Wazuh with Docker

## 🔑 Critical First Workflows

### 1. Welcome Email Automation
**Trigger**: New contact in HubSpot
**Actions**: 
- Send Gmail welcome email
- Create Notion onboarding checklist
- Notify team in Slack

### 2. Support Ticket Routing
**Trigger**: New Freshdesk ticket
**Actions**:
- Analyze with Ollama
- Route to department
- Create GitHub issue if bug

### 3. Security Alert Handler
**Trigger**: Wazuh high severity alert
**Actions**:
- Create incident in Notion
- Alert security team in Slack
- Log to PostgreSQL

### 4. Daily Standup Bot
**Trigger**: Schedule (9 AM daily)
**Actions**:
- Poll GitHub for updates
- Check Freshdesk queue
- Post summary to Slack

## 🚨 Common Setup Issues

### Gmail: "Less secure app" error
**Solution**: Use App Password, not regular password
1. Enable 2FA on Google account
2. Generate app-specific password
3. Use app password in SMTP_PASSWORD

### HubSpot: API limit reached
**Solution**: Free tier has 160 calls/10 seconds
- Implement rate limiting in n8n
- Cache frequently accessed data
- Use webhooks instead of polling

### Wazuh: Connection refused
**Solution**: Check Docker networking
```bash
docker network ls
docker network inspect wazuh-docker_default
# Ensure n8n can reach Wazuh network
```

### Slack: Invalid auth
**Solution**: Bot needs proper scopes
- chat:write
- channels:read
- users:read
- incoming-webhook

## 📊 Success Metrics

After setup, you should be able to:
- [ ] Send automated emails via Gmail
- [ ] Create/update contacts in HubSpot
- [ ] Receive Slack notifications
- [ ] Create support tickets in Freshdesk
- [ ] See security events in Wazuh
- [ ] Access all APIs via n8n HTTP nodes

## 🎉 Next Steps

1. **Test Each Integration**: Use n8n's test feature
2. **Create First Workflow**: Start with email automation
3. **Set Up Monitoring**: Use Uptime Kuma for API health
4. **Document Everything**: Keep credentials secure
5. **Plan Upgrades**: Track usage for paid tier needs

## 🆘 Quick Help

- **n8n Issues**: https://community.n8n.io
- **Integration Docs**: Check each service's API docs
- **Security Questions**: Wazuh/OWASP communities
- **General Setup**: See `INTEGRATION_SETUP_GUIDE.md`

Remember: Start simple, test thoroughly, scale gradually! 🚀