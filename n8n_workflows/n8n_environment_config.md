# n8n Environment Variables Configuration

## Required Environment Variables for n8n Instance

These environment variables need to be configured in your n8n instance at https://workflow.jeweledtech.com

### Core Service URLs (Internal Kubernetes DNS)

```
API_BASE_URL=http://api-service.agentic-system:8000
MCP_SERVICE_URL=http://mcp-service.agentic-system:8002
PRIVATEGPT_URL=http://privategpt-service.agentic-system:8001
OLLAMA_URL=http://ollama-service.agentic-system:11434
```

### n8n Webhook Configuration

```
N8N_WEBHOOK_URL=https://workflow.jeweledtech.com
```

### PostgreSQL Database (if needed by workflows)

```
POSTGRES_HOST=postgres-service.agentic-system
POSTGRES_PORT=5432
POSTGRES_DB=agentic_system
POSTGRES_USER=agentic_user
```

## How to Configure in n8n

1. Log in to n8n at https://workflow.jeweledtech.com
2. Go to Settings → Environment Variables
3. Add each variable with its corresponding value
4. Save the configuration
5. Restart any active workflows to pick up the new variables

## Testing the Configuration

After setting the environment variables, test connectivity:

1. Create a test workflow with an HTTP Request node
2. Use `{{ $env.API_BASE_URL }}/health` as the URL
3. Execute the workflow to verify connectivity

## Notes

- These URLs use Kubernetes internal DNS for service discovery
- The `.agentic-system` suffix is the namespace
- All services are accessible within the cluster without external exposure
- privateGPT is intentionally not exposed externally for security