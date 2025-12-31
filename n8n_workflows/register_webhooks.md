# N8N Webhook Registration Guide

Based on the error logs, the following webhooks need to be registered in n8n:

## Required Webhooks

1. **Chat Webhook** (`/chat`)
   - Used by: Executive UI for chat functionality
   - Workflow: 1_main_api_workflow.json
   - Purpose: Handle chat messages from the executive interface

2. **Knowledge Base Webhook** (`/knowledge-base`)
   - Used by: PrivateGPT integration
   - Workflow: 5_knowledge_base_integration_workflow.json
   - Purpose: Handle document uploads and knowledge base queries

3. **Chief AI Agent Webhook** (`/chief-ai-agent`)
   - Used by: Central orchestration system
   - Workflow: 2_chief_ai_agent_workflow.json
   - Purpose: Route messages to appropriate departments

4. **API Bridge Webhook** (`/api-bridge`)
   - Used by: Kubernetes API connections
   - Workflow: 15_api_bridge_k8_connection.json
   - Purpose: Bridge between external APIs and internal services

5. **MCP Tools Webhook** (`/mcp-tools`)
   - Used by: Model Context Protocol integration
   - Workflow: 6_mcp_integration_workflow.json
   - Purpose: Handle MCP tool requests

## Current Status

- Assessment webhook (`/new-assessment`) is working and data is being saved to Supabase
- The above webhooks are showing as "not registered" in n8n logs
- This is causing "node execution output incorrect data" errors

## Next Steps

1. Import the required workflows into n8n
2. Activate each workflow to register its webhook
3. Test each webhook endpoint to ensure proper functionality

## Webhook URLs

Once registered, the webhooks will be available at:
- https://workflow.jeweledtech.com/webhook/chat
- https://workflow.jeweledtech.com/webhook/knowledge-base
- https://workflow.jeweledtech.com/webhook/chief-ai-agent
- https://workflow.jeweledtech.com/webhook/api-bridge
- https://workflow.jeweledtech.com/webhook/mcp-tools
- https://workflow.jeweledtech.com/webhook/new-assessment (already working)