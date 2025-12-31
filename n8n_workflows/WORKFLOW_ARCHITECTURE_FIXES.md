# n8n Workflow Architecture Fixes

## Core Principle
- **CrewAI API**: The brain (makes decisions)
- **n8n**: The orchestrator (executes decisions)

## Key Changes Needed Across All Workflows

### 1. Main API Gateway (1_main_api_workflow.json)
**Current Issue**: Routes to other n8n workflows instead of CrewAI API
**Fix**: Should call CrewAI API directly

```javascript
// OLD: Routes to n8n webhook
"url": "={{ $env.N8N_WEBHOOK_URL }}/webhook/chief-ai-agent"

// NEW: Routes to CrewAI API
"url": "http://api-service.agentic-system:8000/chat"
```

### 2. Department Workflows (3_sales, 8_marketing, etc.)
**Current Issue**: Contains business logic and decision-making
**Fix**: Should only format data and execute actions returned by CrewAI

### 3. Chief AI Agent Workflow (2_chief_ai_agent_workflow.json)
**Current Issue**: Acts as a router/decision maker
**Fix**: Should be deprecated - routing happens in CrewAI API

### 4. Knowledge Base Integration (5_knowledge_base_integration_workflow.json)
**Current Issue**: Makes decisions about what to search
**Fix**: Should only execute search requests from CrewAI

### 5. Error Handling Workflow (13_error_handling_workflow.json)
**Current Issue**: Contains retry logic and error decisions
**Fix**: Should report errors to CrewAI and execute its recovery instructions

## Updated Architecture

### Simplified Flow:
1. **Webhook receives request** → 
2. **Call CrewAI API** → 
3. **Execute returned actions** → 
4. **Return response**

### What Each Workflow Should Do:

#### Main API Gateway
- Receive webhooks
- Forward to CrewAI API
- Return CrewAI response

#### Department Integration Workflows
- Parse CrewAI response for actions
- Execute tool APIs (HubSpot, Slack, etc.)
- Report results back

#### Monitoring Workflows
- Check system health
- Report to CrewAI for analysis
- Execute CrewAI's remediation actions

## Implementation Priority

1. **Fix Main API Gateway** - Critical path
2. **Fix All Departments Integration** - Already started
3. **Deprecate redundant workflows** - Clean up
4. **Update monitoring workflows** - Operational health
5. **Document new patterns** - Future maintenance