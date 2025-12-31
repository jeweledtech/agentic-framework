# Phase 5: Proposal Automation & CRM Integration Setup Guide

## Overview
This guide walks through setting up the enhanced assessment workflow with PDF generation, proposal emails, and CRM integration.

## Required Services & Credentials

### 1. PDF Generation Service
Choose one of these options:

#### Option A: PDFShift (Recommended for simplicity)
- Sign up at https://pdfshift.io
- Get API key from dashboard
- 100 free PDFs/month
- Add to n8n as HTTP Basic Auth credential:
  - Username: your API key
  - Password: leave empty

#### Option B: APITemplate.io (More templates)
- Sign up at https://apitemplate.io
- Create a proposal template
- Get API key
- Better for complex layouts

#### Option C: Code Node with Puppeteer (Free)
- No external service needed
- Requires n8n instance with puppeteer installed
- More complex but fully customizable

### 2. Resend API (Already configured)
- Existing credential should work
- Just need to ensure attachment support is enabled

### 3. HubSpot CRM
- Create a HubSpot account at https://hubspot.com
- Go to Settings > Integrations > Private Apps
- Create new private app with scopes:
  - `crm.objects.deals.read`
  - `crm.objects.deals.write`
  - `crm.objects.contacts.read`
  - `crm.objects.contacts.write`
  - `crm.objects.companies.read`
  - `crm.objects.companies.write`
- Copy the access token

### 4. Supabase (Already configured)
Create new table for proposals:

```sql
CREATE TABLE solution_proposals (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  assessment_id TEXT NOT NULL,
  company_name TEXT NOT NULL,
  contact_email TEXT NOT NULL,
  proposal_content JSONB,
  proposal_status TEXT DEFAULT 'draft',
  sent_at TIMESTAMP WITH TIME ZONE,
  approved_at TIMESTAMP WITH TIME ZONE,
  hubspot_deal_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add index for quick lookups
CREATE INDEX idx_proposals_assessment_id ON solution_proposals(assessment_id);
CREATE INDEX idx_proposals_status ON solution_proposals(proposal_status);
```

## Workflow Setup Steps

### 1. Import the Enhanced Workflow
```bash
# Copy the new workflow
cp PHASE5_ASSESSMENT_WITH_PDF_CRM.json NEW_CLIENT_ASSESSMENT_PHASE5.json
```

### 2. Configure Credentials in n8n

1. **PDFShift Credential**:
   - Go to Credentials > Create New
   - Select "HTTP Request" > "Basic Auth"
   - Name: "PDFShift API"
   - Username: Your PDFShift API key
   - Password: (leave empty)

2. **HubSpot Credential**:
   - Go to Credentials > Create New
   - Select "HubSpot" > "Access Token"
   - Name: "HubSpot API"
   - Access Token: Your private app token

### 3. Update Environment Variables
Add to your Kubernetes ConfigMap:

```yaml
data:
  PDF_SERVICE_URL: "https://api.pdfshift.io/v3/convert/pdf"
  CALENDLY_URL: "https://calendly.com/jeweledtech/strategy-call"
  PROPOSAL_VALIDITY_DAYS: "30"
  DEFAULT_DEAL_AMOUNT: "50000"
```

### 4. Test the Workflow

```bash
# Test with a sample assessment
curl -X POST https://workflow.jeweledtech.com/webhook/new-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Phase 5 Test Corp",
    "email": "your-test-email@example.com",
    "name": "Test User",
    "vertical": "Technology",
    "company_size": "50-200",
    "strategic_priorities": "Automate sales processes",
    "operational_bottlenecks": "Manual lead qualification",
    "departments_of_interest": ["Sales", "Marketing"],
    "ai_capabilities": ["Lead Scoring", "Email Automation"],
    "key_automation_task": "Automate lead qualification",
    "assessment_id": "phase5_test_'$(date +%s)'"
  }'
```

## Alternative PDF Generation (Code Node)

If you prefer not to use an external service, replace the PDFShift node with this Code node:

```javascript
// Generate PDF using jsPDF (requires adding to n8n)
const { jsPDF } = require("jspdf");

// Create new PDF
const doc = new jsPDF();

// Add content
doc.setFontSize(20);
doc.text("AI Workforce Proposal", 20, 20);

doc.setFontSize(14);
doc.text(`Company: ${$json.companyName}`, 20, 40);
doc.text(`Prepared for: ${$json.contactName}`, 20, 50);

// Add proposal content
doc.setFontSize(12);
const proposalLines = $json.proposalContent.split('\n');
let yPosition = 70;
proposalLines.forEach(line => {
  if (yPosition > 250) {
    doc.addPage();
    yPosition = 20;
  }
  doc.text(line, 20, yPosition);
  yPosition += 10;
});

// Convert to base64
const pdfBase64 = doc.output('datauristring').split(',')[1];

return [{
  json: {
    pdfData: pdfBase64,
    filename: `proposal_${$json.assessmentId}.pdf`
  }
}];
```

## Monitoring & Troubleshooting

### Check Execution Status
1. Go to n8n workflow executions
2. Look for these key nodes:
   - ✅ Solutions Architect Agent - Should return proposal content
   - ✅ Generate PDF - Should create PDF file
   - ✅ Send Proposal Email - Should send with attachment
   - ✅ Create HubSpot Deal - Should return deal ID

### Common Issues

1. **PDF Generation Fails**
   - Check API key is correct
   - Verify HTML is valid
   - Check service quotas

2. **Email Not Sending**
   - Verify Resend API key
   - Check attachment size (< 10MB)
   - Verify email addresses

3. **HubSpot Deal Not Created**
   - Check API token permissions
   - Verify deal stage exists
   - Check required fields

## Next Steps

After this workflow is working:

1. **Build Admin Interface** (app.jeweledtech.com)
   - List proposals from Supabase
   - Approve/Reject buttons
   - Trigger follow-up workflows

2. **Create Nurturing Workflow**
   - Triggered by "Proposal Sent" event
   - Schedule follow-ups at 3, 7, 14 days
   - Track engagement metrics

3. **Add Analytics**
   - Proposal open rates
   - CTA click tracking
   - Conversion metrics