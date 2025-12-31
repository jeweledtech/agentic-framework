# Self-Hosted N8N Environment Variables Setup

## 🐳 Method 1: Docker Compose (Recommended)

### Update your `docker-compose.yml`:

```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      # Database
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=your_password
      
      # N8N Configuration
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your_admin_password
      - WEBHOOK_URL=https://workflow.jeweledtech.com
      
      # Custom Environment Variables for Workflows
      - CREWAI_API_URL=https://api.jeweledtech.com
      - MONITORING_WEBHOOK_URL=https://api.jeweledtech.com/monitoring/workflow-execution
      - FROM_EMAIL=JeweledTech AI <ai@jeweledtech.com>
      - REPLY_TO_EMAIL=admin@jeweledtech.com
      - WEBHOOK_API_KEY=your-secure-api-key
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres

  postgres:
    image: postgres:13
    restart: always
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=your_password
      - POSTGRES_DB=n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  n8n_data:
  postgres_data:
```

### Restart your containers:
```bash
docker-compose down
docker-compose up -d
```

## 🖥️ Method 2: Direct Docker Run

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e CREWAI_API_URL=https://api.jeweledtech.com \
  -e MONITORING_WEBHOOK_URL=https://api.jeweledtech.com/monitoring/workflow-execution \
  -e FROM_EMAIL="JeweledTech AI <ai@jeweledtech.com>" \
  -e REPLY_TO_EMAIL=admin@jeweledtech.com \
  -e WEBHOOK_API_KEY=your-secure-api-key \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

## 🔧 Method 3: System Environment Variables

### Linux/macOS:
```bash
# Add to ~/.bashrc or ~/.zshrc
export CREWAI_API_URL=https://api.jeweledtech.com
export MONITORING_WEBHOOK_URL=https://api.jeweledtech.com/monitoring/workflow-execution
export FROM_EMAIL="JeweledTech AI <ai@jeweledtech.com>"
export REPLY_TO_EMAIL=admin@jeweledtech.com

# Reload shell
source ~/.bashrc

# Start n8n
n8n start
```

### Windows:
```cmd
# Set environment variables
set CREWAI_API_URL=https://api.jeweledtech.com
set MONITORING_WEBHOOK_URL=https://api.jeweledtech.com/monitoring/workflow-execution
set FROM_EMAIL=JeweledTech AI <ai@jeweledtech.com>
set REPLY_TO_EMAIL=admin@jeweledtech.com

# Start n8n
n8n start
```

## 🎯 Method 4: .env File (If supported)

Create a `.env` file in your n8n directory:

```bash
# .env file
CREWAI_API_URL=https://api.jeweledtech.com
MONITORING_WEBHOOK_URL=https://api.jeweledtech.com/monitoring/workflow-execution
FROM_EMAIL=JeweledTech AI <ai@jeweledtech.com>
REPLY_TO_EMAIL=admin@jeweledtech.com
WEBHOOK_API_KEY=your-secure-api-key
```

## 🔍 Verify Environment Variables

After setup, test in a workflow Code node:
```javascript
return [{
  json: {
    crewai_url: $env.CREWAI_API_URL,
    monitoring_url: $env.MONITORING_WEBHOOK_URL,
    from_email: $env.FROM_EMAIL,
    all_env: Object.keys(process.env).filter(key => key.includes('CREWAI') || key.includes('MONITORING'))
  }
}];
```

## ⚠️ Troubleshooting

### Environment Variables Not Working?
1. **Restart n8n completely** after adding environment variables
2. **Check Docker logs**: `docker logs n8n-container-name`
3. **Verify in workflow**: Use Code node to check `$env.VARIABLE_NAME`
4. **Case sensitivity**: Environment variables are case-sensitive
5. **Special characters**: Quote values with spaces or special characters

### Still Not Working?
Use the hardcoded fallback workflows provided in the next section.