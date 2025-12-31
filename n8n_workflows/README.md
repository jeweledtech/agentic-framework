# n8n Workflow Templates for JeweledTech Agentic Framework

## Quick Start

Your n8n instance: **https://jtsinc.app.n8n.cloud**

### Import Order (IMPORTANT)

Follow this order to ensure dependencies are met:

```
1. Infrastructure (import first)
   - 13_error_handling_workflow.json
   - 15_api_bridge_k8_connection.json

2. Main Gateway
   - 1_main_api_workflow.json

3. Core Services
   - 2_chief_ai_agent_workflow.json
   - 5_knowledge_base_integration_workflow.json
   - 6_mcp_integration_workflow.json

4. Department Workflows (Sales & Marketing focus)
   - 3_sales_department_workflow.json
   - 4_outbound_sales_manager_workflow.json
   - 7_inbound_sales_manager_workflow.json
   - 8_marketing_department_workflow.json

5. Phase 5 (Advanced Sales Automation)
   - phase5/PHASE5_NURTURING_SEQUENCE.json
   - phase5/PHASE5_NURTURE_EMAIL_SENDER.json
   - phase5/PHASE5_PROPOSAL_APPROVAL_WEBHOOK.json
```

---

## Import Methods

### Method 1: n8n Web UI (Recommended for first-time)

1. Go to https://jtsinc.app.n8n.cloud
2. Click **Workflows** in the sidebar
3. Click **Import from File** (or drag-drop)
4. Select the JSON file
5. Click **Import**
6. Configure credentials (see Credentials section below)
7. Click **Activate** toggle

### Method 2: n8n MCP API (Programmatic)

Use the Instance-level MCP endpoint we configured:

```python
import requests
import json

N8N_MCP_URL = "https://jtsinc.app.n8n.cloud/mcp-server/http"
N8N_MCP_TOKEN = "your_jwt_token"  # From .env

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream',
    'Authorization': f'Bearer {N8N_MCP_TOKEN}'
}

# Execute a workflow by ID
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "execute_workflow",
        "arguments": {
            "workflowId": "YOUR_WORKFLOW_ID",
            "inputData": {"message": "Test"}
        }
    },
    "id": 1
}

response = requests.post(N8N_MCP_URL, headers=headers, json=payload)
```

---

## Workflow Catalog

### Sales Department

| Workflow | Webhook Path | Description |
|----------|--------------|-------------|
| Sales Department | `/webhook/sales-actions` | Execute HubSpot/email actions from CrewAI |
| Outbound Sales Manager | `/webhook/outbound-sales-manager` | Email campaigns, lead gen, sequences |
| Inbound Sales Manager | `/webhook/inbound-sales-manager` | Qualify inbound leads, route to reps |
| Sales HubSpot Integration | `/webhook/sales-hubspot` | CRM sync and deal management |

### Marketing Department

| Workflow | Webhook Path | Description |
|----------|--------------|-------------|
| Marketing Department | `/webhook/marketing-department` | Content gen, campaign execution |
| Content Distribution | `/webhook/content-distribute` | Multi-channel publishing |

### Phase 5 (Nurture Automation)

| Workflow | Webhook Path | Description |
|----------|--------------|-------------|
| Nurturing Sequence | `/webhook/proposal-sent` | 4-stage follow-up sequence (3/7/14/28 days) |
| Nurture Email Sender | `/webhook/send-nurture-email` | Template-based email sending |
| Proposal Approval | `/webhook/proposal-approved` | Post-approval automation |

---

## Required Credentials

Configure these in n8n Settings > Credentials:

### HubSpot API
- **Type**: HubSpot API
- **API Key**: From HubSpot Settings > Integrations > API Key
- **Used by**: Sales workflows, lead management

### Gmail OAuth2
- **Type**: Gmail OAuth2
- **OAuth Client**: From Google Cloud Console
- **Used by**: Email sending, follow-ups

### Supabase (Phase 5)
- **Type**: Supabase API
- **Project URL**: Your Supabase project URL
- **Service Role Key**: From Supabase Settings > API
- **Used by**: Nurture queue, assessment storage

---

## Environment Variables

Set these in n8n Settings > Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `CREWAI_API_URL` | Framework API endpoint | `http://localhost:8000` or tunnel URL |
| `FRAMEWORK_API_KEY` | API authentication | From `.env` |

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     n8n Cloud Instance                          │
│              https://jtsinc.app.n8n.cloud                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │   Webhooks   │   │  Workflows   │   │ Credentials  │        │
│  │  /sales-*    │   │  87 total    │   │  HubSpot     │        │
│  │  /marketing  │   │              │   │  Gmail       │        │
│  │  /proposal   │   │              │   │  Supabase    │        │
│  └──────┬───────┘   └──────┬───────┘   └──────────────┘        │
│         │                  │                                    │
│         └────────┬─────────┘                                    │
│                  │                                              │
│         ┌────────▼────────┐                                     │
│         │  Instance MCP   │                                     │
│         │  /mcp-server/   │◄──── MCP Tools ────────────────────┤
│         └────────┬────────┘      search_workflows               │
│                  │               execute_workflow               │
│                  │               get_workflow_details           │
└──────────────────┼──────────────────────────────────────────────┘
                   │
          ┌────────▼────────┐
          │    Framework    │
          │   API Server    │
          │  (localhost or  │
          │   Cloudflare    │
          │    tunnel)      │
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │   CrewAI Agents │
          │  Sales/Marketing│
          │   Departments   │
          └─────────────────┘
```

---

## Bidirectional Flow

### Direction 1: n8n → Framework
External events trigger n8n webhooks, which call the Framework API:

```
[HubSpot Form] → [n8n Webhook] → [HTTP Request to Framework] → [Sales Agent]
```

### Direction 2: Framework → n8n
Agents trigger n8n workflows via MCP tools:

```
[User Request] → [Sales Agent] → [N8NMCPTool] → [execute_workflow] → [n8n Actions]
```

---

## Testing

### Test n8n Connection
```bash
curl -X POST https://jtsinc.app.n8n.cloud/mcp-server/http \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Test Sales Webhook (after importing)
```bash
curl -X POST https://jtsinc.app.n8n.cloud/webhook/sales-actions \
  -H "Content-Type: application/json" \
  -d '{"actions":[{"type":"hubspot_contact","parameters":{"email":"test@example.com"}}]}'
```

---

## File Reference

```
n8n_workflows/
├── README.md                    # This file
├── import_order.txt             # Import sequence
├── .env.n8n.example             # Environment template
│
├── # Infrastructure
├── 13_error_handling_workflow.json
├── 15_api_bridge_k8_connection.json
│
├── # Main Gateway
├── 1_main_api_workflow.json
├── 2_chief_ai_agent_workflow.json
│
├── # Sales Department
├── 3_sales_department_workflow.json
├── 4_outbound_sales_manager_workflow.json
├── 7_inbound_sales_manager_workflow.json
├── sales_hubspot_integration.json
│
├── # Marketing Department
├── 8_marketing_department_workflow.json
│
├── # Other Departments
├── 9_engineering_department_workflow.json
├── 10_customer_department_workflow.json
├── 11_backoffice_department_workflow.json
├── 12_security_department_workflow.json
│
├── # Integration Workflows
├── 5_knowledge_base_integration_workflow.json
├── 6_mcp_integration_workflow.json
├── all_departments_integration.json
│
├── # Phase 5 (Nurture Automation)
└── phase5/
    ├── PHASE5_NURTURING_SEQUENCE.json
    ├── PHASE5_NURTURE_EMAIL_SENDER.json
    ├── PHASE5_PROPOSAL_APPROVAL_WEBHOOK.json
    └── PHASE5_ASSESSMENT_WITH_PDF_CRM_FIXED_V11.json  # Latest
```

---

## Next Steps

1. **Import core workflows** (follow import_order.txt)
2. **Configure credentials** (HubSpot, Gmail, Supabase)
3. **Set environment variables** (CREWAI_API_URL)
4. **Activate workflows**
5. **Test with curl or Postman**
6. **Start the Framework API** and test bidirectional flow
