# 🚀 N8N-MCP Workflow Import Guide

## 🎯 **Using n8n-mcp to Import Enhanced Workflows**

Perfect! You're absolutely right - we can use n8n-mcp to manage workflows directly through the API instead of manual import.

## **Step 1: Get Your N8N API Key**

### **Option A: From N8N Web Interface**
1. Go to https://workflow.jeweledtech.com
2. Click your **profile/avatar** (top right)
3. Go to **Settings** → **API**
4. Click **Create API Key**
5. Copy the generated API key

### **Option B: From N8N Database/Config** (if you have access)
```bash
# If using SQLite database
kubectl exec -n agentic-system n8n-fresh-xxx -- cat /home/node/.n8n/database.sqlite | grep api_key

# Or check n8n logs for any existing API keys
kubectl logs -n agentic-system deployment/n8n-fresh | grep -i api
```

## **Step 2: Set Environment Variables**

```bash
# Set the n8n API configuration
export N8N_API_URL="https://workflow.jeweledtech.com/api"
export N8N_API_KEY="your-actual-api-key-here"

# Verify configuration
echo "N8N_API_URL: $N8N_API_URL"
echo "N8N_API_KEY: ${N8N_API_KEY:0:10}..." # Shows first 10 chars only
```

## **Step 3: Run the MCP Import Script**

```bash
# Navigate to the n8n-mcp directory
cd /home/bren/agentic_system_project/n8n-mcp

# Make the script executable
chmod +x ../n8n_workflows/import-workflows-with-mcp.js

# Run the import script
node ../n8n_workflows/import-workflows-with-mcp.js
```

## **What the Script Does:**

### **🔍 Connection Test**
- ✅ Tests n8n API connectivity
- ✅ Validates authentication
- ✅ Lists existing workflows

### **📥 Workflow Import**
- ✅ **Test Environment Variables** - Verifies env vars are working
- ✅ **Enhanced Assessment Workflow (With Resend)** - Production-ready with all fixes
- ✅ **Enhanced Assessment Workflow** - Alternative version

### **🎯 Automatic Updates**
- ✅ **Creates new workflows** if they don't exist
- ✅ **Updates existing workflows** if they already exist
- ✅ **Preserves workflow IDs** and connections

### **🧪 Environment Variable Testing**
- ✅ **Automatic test execution** of environment variables
- ✅ **Webhook URL provided** for manual testing
- ✅ **Validation report** showing all env vars status

## **Expected Output:**

```bash
🚀 Starting workflow import with n8n-mcp...
✅ N8N API configured: https://workflow.jeweledtech.com/api
🔍 Testing n8n API connection...
✅ N8N Health Check: { status: 'ok' }
📋 Found 5 existing workflows

📥 Importing workflows...

🔄 Processing: Test Environment Variables
📝 Creating new workflow: Test Environment Variables
✅ Created workflow: Test Environment Variables (ID: 123)

🔄 Processing: New Client Assessment Workflow (With Resend)
📝 Updating existing workflow: New Client Assessment Workflow (With Resend) (ID: 456)
✅ Updated workflow: New Client Assessment Workflow (With Resend)

🎯 Testing environment variables workflow...
🧪 Found test workflow: 123
🌐 Test URL: https://workflow.jeweledtech.com/webhook/test-env-vars

🎉 Workflow import completed successfully!

📋 Summary:
✅ Environment variables configured in Kubernetes
✅ Enhanced workflows imported with HTTP Request nodes
✅ Input validation and monitoring added
✅ Ready for production use!
```

## **Step 4: Verify Environment Variables**

After import, test the environment variables:

```bash
# Test the environment variables endpoint
curl https://workflow.jeweledtech.com/webhook/test-env-vars

# Expected response:
{
  "summary": {
    "test_name": "Environment Variables Validation",
    "test_time": "2025-07-13T00:45:00.000Z",
    "total_custom_vars_found": 6
  },
  "workflow_variables": {
    "crewai_api_url": {
      "value": "https://api.jeweledtech.com",
      "status": "PASS"
    },
    "monitoring_webhook_url": {
      "status": "PASS"
    }
  },
  "overall_status": "PASS - All environment variables loaded successfully!"
}
```

## **Step 5: Test Assessment Workflow**

```bash
# Test the enhanced assessment endpoint
curl -X POST https://workflow.jeweledtech.com/webhook/new-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "email": "test@example.com",
    "name": "Test User",
    "vertical": "Technology",
    "departments_of_interest": ["Sales"],
    "assessment_id": "test_'$(date +%s)'"
  }'
```

## **🔧 Troubleshooting**

### **API Key Issues:**
```bash
# If API key is invalid
❌ Error: 401 Unauthorized

# Solution: Regenerate API key in n8n settings
```

### **Connection Issues:**
```bash
# If connection fails
❌ Error: ECONNREFUSED

# Check n8n is accessible:
curl -I https://workflow.jeweledtech.com/api/v1/workflows
```

### **Import Errors:**
```bash
# If workflow import fails
❌ Error: Workflow validation failed

# Check the workflow JSON files are valid
node -e "console.log(JSON.parse(require('fs').readFileSync('TEST_ENVIRONMENT_VARIABLES.json')))"
```

## **🎉 Benefits of Using N8N-MCP:**

### **✅ Automated Management:**
- No manual clicking through n8n interface
- Batch import/update multiple workflows
- Version control and repeatability

### **✅ Intelligent Updates:**
- Preserves existing workflow IDs
- Updates only when changes detected
- Maintains webhook URLs and connections

### **✅ Built-in Validation:**
- API connectivity testing
- Environment variable verification
- Workflow structure validation

### **✅ Production Ready:**
- All fixes applied automatically
- HTTP Request nodes configured
- Monitoring and validation included

**This approach is much more efficient and maintainable than manual imports!** 🚀