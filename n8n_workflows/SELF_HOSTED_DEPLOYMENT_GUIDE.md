# 🚀 Self-Hosted N8N Deployment Guide

## 🎯 **Two Deployment Options**

Since self-hosted n8n handles environment variables differently, I've prepared **TWO solutions**:

### **Option A: Environment Variables Setup** (Recommended)
### **Option B: Hardcoded Values** (Quick & Easy)

---

## 🔧 **Option A: Environment Variables Setup**

### **Step 1: Configure Environment Variables**

#### **If using Docker Compose:**
Add to your `docker-compose.yml`:

```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      # N8N Basic Configuration
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your_password
      - WEBHOOK_URL=https://workflow.jeweledtech.com
      
      # Custom Workflow Variables
      - CREWAI_API_URL=https://api.jeweledtech.com
      - MONITORING_WEBHOOK_URL=https://api.jeweledtech.com/monitoring/workflow-execution
      - FROM_EMAIL=JeweledTech AI <ai@jeweledtech.com>
      - REPLY_TO_EMAIL=admin@jeweledtech.com
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

**Restart containers:**
```bash
docker-compose down
docker-compose up -d
```

#### **If using direct Docker:**
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e CREWAI_API_URL=https://api.jeweledtech.com \
  -e MONITORING_WEBHOOK_URL=https://api.jeweledtech.com/monitoring/workflow-execution \
  -e FROM_EMAIL="JeweledTech AI <ai@jeweledtech.com>" \
  -e REPLY_TO_EMAIL=admin@jeweledtech.com \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

#### **If running directly (npm/binary):**
```bash
# Set environment variables before starting n8n
export CREWAI_API_URL=https://api.jeweledtech.com
export MONITORING_WEBHOOK_URL=https://api.jeweledtech.com/monitoring/workflow-execution
export FROM_EMAIL="JeweledTech AI <ai@jeweledtech.com>"
export REPLY_TO_EMAIL=admin@jeweledtech.com

# Start n8n
n8n start
```

### **Step 2: Import Enhanced Workflows**
Use these files with environment variable support:
- ✅ `NEW_CLIENT_ASSESSMENT_TEMPLATE_WITH_RESEND.json`
- ✅ `NEW_CLIENT_ASSESSMENT_TEMPLATE.json`

---

## 🎯 **Option B: Hardcoded Values** (No Environment Variables)

### **Step 1: Use Hardcoded Workflows**
I've created special versions with hardcoded values:
- ✅ `NEW_CLIENT_ASSESSMENT_TEMPLATE_WITH_RESEND_HARDCODED.json`

### **Step 2: Customize URLs Before Import**
Before importing, edit these values in the hardcoded files:

```json
// Change these URLs to match your setup:
"url": "https://api.jeweledtech.com/workflow/trigger"
"url": "https://api.jeweledtech.com/monitoring/workflow-execution"

// Change these email addresses:
"from": "JeweledTech AI <ai@jeweledtech.com>"
"reply_to": "admin@jeweledtech.com"
```

### **Step 3: Import Directly**
1. Go to https://workflow.jeweledtech.com
2. Navigate to **Workflows** → **Import**
3. Upload the `*_HARDCODED.json` files
4. Activate the workflows

---

## 🔍 **Verify Setup**

### **Test Environment Variables** (Option A)
Create a test workflow with a Code node:

```javascript
return [{
  json: {
    crewai_url: $env.CREWAI_API_URL || 'NOT_SET',
    monitoring_url: $env.MONITORING_WEBHOOK_URL || 'NOT_SET', 
    from_email: $env.FROM_EMAIL || 'NOT_SET',
    all_vars: Object.keys(process.env).filter(k => 
      k.includes('CREWAI') || k.includes('MONITORING') || k.includes('FROM_')
    )
  }
}];
```

**Expected output:**
```json
{
  "crewai_url": "https://api.jeweledtech.com",
  "monitoring_url": "https://api.jeweledtech.com/monitoring/workflow-execution",
  "from_email": "JeweledTech AI <ai@jeweledtech.com>",
  "all_vars": ["CREWAI_API_URL", "MONITORING_WEBHOOK_URL", "FROM_EMAIL"]
}
```

### **Test Assessment Endpoint**
```bash
curl -X POST https://workflow.jeweledtech.com/webhook/new-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company",
    "email": "test@example.com", 
    "name": "Test User",
    "vertical": "Technology",
    "departments_of_interest": ["Sales"],
    "assessment_id": "test_'$(date +%s)'"
  }'
```

---

## 🚨 **Troubleshooting**

### **Environment Variables Not Working?**

1. **Check n8n logs:**
   ```bash
   # Docker
   docker logs n8n-container-name
   
   # Direct
   Check console output when starting n8n
   ```

2. **Verify in workflow:**
   ```javascript
   // Test Code node
   return [{ json: { env_test: $env.CREWAI_API_URL } }];
   ```

3. **Common issues:**
   - **Restart required**: Always restart n8n after adding environment variables
   - **Case sensitivity**: Variables are case-sensitive
   - **Quotes**: Use quotes for values with spaces
   - **Docker**: Make sure variables are in the correct service section

### **If Environment Variables Still Don't Work:**

✅ **Use Option B (Hardcoded)** - It's a perfectly valid solution!

**Advantages of hardcoded approach:**
- ✅ Works immediately without configuration
- ✅ No restart required
- ✅ Clear and predictable
- ✅ Easy to customize per workflow

**To customize hardcoded values:**

1. **Find and replace URLs:**
   ```bash
   # In the JSON file, change:
   "https://api.jeweledtech.com" → "https://your-api.yourdomain.com"
   ```

2. **Update email addresses:**
   ```bash
   # Change:
   "ai@jeweledtech.com" → "ai@yourdomain.com"
   "admin@jeweledtech.com" → "admin@yourdomain.com"
   ```

3. **Save and import the customized file**

---

## 📋 **Quick Start Checklist**

### **Option A (Environment Variables):**
- [ ] Update Docker Compose or export environment variables
- [ ] Restart n8n
- [ ] Verify environment variables with test Code node
- [ ] Import enhanced workflows
- [ ] Test assessment endpoint

### **Option B (Hardcoded):**
- [ ] Edit `*_HARDCODED.json` files with your URLs/emails
- [ ] Import customized hardcoded workflows
- [ ] Test assessment endpoint
- [ ] No restart required!

---

## 🎉 **Both Options Give You:**

- ✅ **Production-ready HTTP Request nodes** (no more fetch() issues)
- ✅ **Input validation** with proper error responses
- ✅ **Comprehensive monitoring** and execution tracking
- ✅ **Retry logic** for external API calls
- ✅ **Fixed Supabase field mappings**
- ✅ **All reliability improvements**

**Choose the option that works best for your setup!** 🚀