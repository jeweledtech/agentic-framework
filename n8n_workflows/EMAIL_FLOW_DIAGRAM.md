# Email Flow Architecture

## 📧 Email Services Overview

Your system uses two separate email services for different purposes:

```
┌─────────────────────────────────────────────────────────────────┐
│                     jeweledtech.com Website                      │
│                                                                  │
│  Customer fills    →    Stored in    →    Triggers Resend API   │
│  Assessment Form        Supabase           (Confirmation Email)  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                         n8n Workflows                            │
│                                                                  │
│  1. Can listen to Resend webhooks (delivery status, clicks)     │
│  2. Can send follow-up emails via Resend API                    │
│  3. Department emails use Gmail SMTP (sales, support, etc.)     │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Email Types and Their Configuration

### 1. **Customer-Facing Transactional Emails** (via Resend)
- **What**: Assessment confirmations, proposal delivery, password resets
- **From**: noreply@jeweledtech.com or hello@jeweledtech.com
- **Configured in**: Your jeweledtech.com backend
- **n8n Role**: Optional - process webhooks, send follow-ups

### 2. **Internal Department Emails** (via Gmail SMTP)
- **What**: Sales outreach, support tickets, team notifications
- **From**: sales@yourcompany.com, support@yourcompany.com
- **Configured in**: n8n workflows
- **n8n Role**: Primary - all department email automation

### 3. **Marketing Emails** (via Mailchimp/Buffer)
- **What**: Newsletters, campaigns, social posts
- **From**: marketing@yourcompany.com
- **Configured in**: Marketing platforms + n8n
- **n8n Role**: Trigger campaigns, sync contacts

## 🚀 Common n8n Email Workflows

### Workflow 1: Assessment Follow-Up Sequence
```
Trigger: Supabase webhook (new assessment)
     ↓
Check: Has proposal been generated?
     ↓
Action 1: Send follow-up via Resend (branded email)
Action 2: Create task in HubSpot CRM
Action 3: Notify sales team via Gmail SMTP
```

### Workflow 2: Support Ticket Response
```
Trigger: Freshdesk new ticket
     ↓
Action 1: Auto-acknowledge via Gmail SMTP
Action 2: If high priority → SMS via Twilio
Action 3: Log in internal Slack channel
```

### Workflow 3: Sales Outreach Campaign
```
Trigger: New lead in HubSpot
     ↓
Action 1: Personalized outreach via Gmail SMTP
Action 2: Schedule follow-up in Google Calendar
Action 3: Track opens/clicks in HubSpot
```

## 🔧 Configuration Requirements

### For Resend Integration (Optional in n8n)
```env
# Only needed if you want n8n to:
# - Process Resend webhooks
# - Send additional emails via Resend
# - Track email analytics in n8n
RESEND_API_KEY=re_your_api_key
RESEND_FROM_EMAIL=noreply@jeweledtech.com
```

### For Department Emails (Required in n8n)
```env
# Essential for most n8n workflows
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-business@gmail.com
SMTP_PASSWORD=app-specific-password
```

## 💡 Best Practices

1. **Use Resend for**:
   - Customer-facing transactional emails
   - Branded communications
   - High deliverability requirements
   - Email tracking and analytics

2. **Use Gmail SMTP for**:
   - Internal team notifications
   - Low-volume personal outreach
   - Support responses
   - Testing and development

3. **Separation Benefits**:
   - Different sending reputations
   - Appropriate rate limits
   - Cost optimization
   - Clear audit trails

## 🎯 Quick Decision Guide

**Q: Do I need to configure Resend in n8n?**
- If you only send assessment confirmations from jeweledtech.com: **No**
- If you want n8n to send follow-up sequences: **Yes**
- If you want to track email analytics in n8n: **Yes**
- If you want to process bounces/complaints: **Yes**

**Q: Do I need Gmail SMTP in n8n?**
- If you have any department workflows: **Yes**
- If you need internal notifications: **Yes**
- If you do sales outreach: **Yes**
- If you handle support tickets: **Yes**

## 📊 Monitoring & Analytics

```
Resend Dashboard → Customer email metrics
     ↓
n8n Webhooks → Process events → Update CRM
     ↓
Gmail → Department email tracking → HubSpot/Freshdesk
```

This architecture gives you professional customer communications via Resend while maintaining flexibility for department operations via Gmail SMTP.