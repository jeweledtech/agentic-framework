# n8n Workflow Migration Guide

## Migration Strategy

### Phase 1: Update Core Workflows (Priority)

1. **Main API Gateway** (`1_main_api_workflow.json`)
   - Remove routing logic
   - Direct all requests to CrewAI API
   - Use `1_main_api_workflow_fixed.json`

2. **All Departments Integration** (`all_departments_integration.json`)
   - Already updated to parse CrewAI responses
   - Executes actions based on CrewAI decisions

### Phase 2: Deprecate Redundant Workflows

These workflows contain business logic that belongs in CrewAI:
- `2_chief_ai_agent_workflow.json` - Routing logic (move to CrewAI)
- `4_outbound_sales_manager_workflow.json` - Sales logic (move to CrewAI)
- `7_inbound_sales_manager_workflow.json` - Sales logic (move to CrewAI)

### Phase 3: Simplify Department Workflows

Convert these to simple action executors:
- `3_sales_department_workflow.json` → Use pattern from `3_sales_department_workflow_fixed.json`
- `8_marketing_department_workflow.json` → Apply unified pattern
- `9_engineering_department_workflow.json` → Apply unified pattern
- `10_customer_department_workflow.json` → Apply unified pattern
- `11_backoffice_department_workflow.json` → Apply unified pattern
- `12_security_department_workflow.json` → Apply unified pattern

### Phase 4: Update Support Workflows

- `5_knowledge_base_integration_workflow.json` - Should only execute KB queries from CrewAI
- `6_mcp_integration_workflow.json` - Should only relay MCP requests from CrewAI
- `13_error_handling_workflow.json` - Should report errors to CrewAI and execute recovery
- `14_monitoring_logging_workflow.json` - Should send metrics to CrewAI for analysis

## Implementation Steps

### Step 1: Deploy Fixed Main Gateway
```bash
# Import the fixed main API workflow
# This ensures all requests go to CrewAI first
```

### Step 2: Update CrewAI API
Ensure your API returns structured responses:
```json
{
  "department": "sales",
  "agent": "HeadOfSales",
  "text": "I'll help you with that request",
  "actions": [
    {
      "type": "hubspot_contact",
      "parameters": {...}
    }
  ]
}
```

### Step 3: Test Integration
1. Send request to n8n webhook
2. Verify it calls CrewAI API
3. Check actions are executed
4. Confirm response returned

### Step 4: Monitor and Iterate
- Watch for errors in n8n execution logs
- Ensure CrewAI responses include necessary action details
- Refine action parameters as needed

## Benefits After Migration

1. **Clear Separation of Concerns**
   - CrewAI: Intelligence and decisions
   - n8n: Execution and integration

2. **Easier Maintenance**
   - Update agent logic without touching workflows
   - Add new tools by updating action executor

3. **Better Scalability**
   - CrewAI can be scaled independently
   - n8n handles concurrent executions

4. **Improved Debugging**
   - Clear data flow
   - Easy to trace decisions vs executions

## Quick Reference

### What n8n Should Do:
- ✅ Receive webhooks
- ✅ Call CrewAI API
- ✅ Execute tool APIs
- ✅ Format responses
- ✅ Handle errors gracefully

### What n8n Should NOT Do:
- ❌ Make business decisions
- ❌ Route between departments
- ❌ Generate content
- ❌ Analyze data
- ❌ Determine actions