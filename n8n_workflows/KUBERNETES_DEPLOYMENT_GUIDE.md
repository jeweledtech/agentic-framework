# 🚢 Kubernetes N8N Environment Variables Deployment Guide

## 🎯 **Step-by-Step Kubernetes Setup**

### **Step 1: Update Configuration Files**

First, update the namespace in the configuration files to match your setup:

```bash
# Check your current n8n namespace
kubectl get pods -A | grep n8n

# Update the namespace in config files
sed -i 's/namespace: agentic-system/namespace: YOUR-NAMESPACE/g' k8s-n8n-environment-config.yaml
sed -i 's/namespace: agentic-system/namespace: YOUR-NAMESPACE/g' k8s-deployment-patch.yaml
```

### **Step 2: Encode Sensitive Values**

Create base64 encoded values for secrets:

```bash
# Encode your API keys
echo -n "your-actual-webhook-api-key" | base64
echo -n "your-actual-resend-api-key" | base64

# Update the secret in k8s-n8n-environment-config.yaml with the encoded values
```

### **Step 3: Apply ConfigMap and Secret**

```bash
# Apply the ConfigMap and Secret
kubectl apply -f k8s-n8n-environment-config.yaml

# Verify they were created
kubectl get configmap n8n-workflow-config -n YOUR-NAMESPACE
kubectl get secret n8n-workflow-secrets -n YOUR-NAMESPACE
```

### **Step 4: Update Your N8N Deployment**

#### **Option A: Patch Existing Deployment**
```bash
# Get your current n8n deployment name
kubectl get deployments -n YOUR-NAMESPACE | grep n8n

# Patch the deployment to add environment variables
kubectl patch deployment n8n -n YOUR-NAMESPACE --patch-file k8s-deployment-patch.yaml
```

#### **Option B: Edit Deployment Directly**
```bash
# Edit your deployment directly
kubectl edit deployment n8n -n YOUR-NAMESPACE

# Add the envFrom section under spec.template.spec.containers[0]:
#   envFrom:
#   - configMapRef:
#       name: n8n-workflow-config
#   - secretRef:
#       name: n8n-workflow-secrets
```

#### **Option C: Full Deployment YAML** (if you have your own deployment file)
Add this to your n8n container specification:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: n8n
  namespace: YOUR-NAMESPACE
spec:
  template:
    spec:
      containers:
      - name: n8n
        image: n8nio/n8n:latest
        # Add environment variables
        envFrom:
        - configMapRef:
            name: n8n-workflow-config
        - secretRef:
            name: n8n-workflow-secrets
        # ... rest of your container config
```

### **Step 5: Verify Deployment**

```bash
# Check if the deployment updated successfully
kubectl rollout status deployment/n8n -n YOUR-NAMESPACE

# Check pod logs for any issues
kubectl logs deployment/n8n -n YOUR-NAMESPACE

# Get pod name and check environment variables
POD_NAME=$(kubectl get pods -n YOUR-NAMESPACE -l app=n8n -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n YOUR-NAMESPACE $POD_NAME -- env | grep -E "(CREWAI|MONITORING|FROM_EMAIL)"
```

### **Step 6: Test Environment Variables in N8N**

1. **Access your n8n instance** at https://workflow.jeweledtech.com
2. **Create a test workflow** with a Code node:

```javascript
return [{
  json: {
    crewai_url: $env.CREWAI_API_URL || 'NOT_SET',
    monitoring_url: $env.MONITORING_WEBHOOK_URL || 'NOT_SET',
    from_email: $env.FROM_EMAIL || 'NOT_SET',
    reply_to: $env.REPLY_TO_EMAIL || 'NOT_SET',
    webhook_key: $env.WEBHOOK_API_KEY ? 'SET' : 'NOT_SET',
    all_custom_vars: Object.keys(process.env).filter(k => 
      k.includes('CREWAI') || k.includes('MONITORING') || 
      k.includes('FROM_') || k.includes('REPLY_') || k.includes('WEBHOOK_')
    )
  }
}];
```

3. **Execute the test workflow** - you should see:
```json
{
  "crewai_url": "https://api.jeweledtech.com",
  "monitoring_url": "https://api.jeweledtech.com/monitoring/workflow-execution",
  "from_email": "JeweledTech AI <ai@jeweledtech.com>",
  "reply_to": "admin@jeweledtech.com",
  "webhook_key": "SET",
  "all_custom_vars": ["CREWAI_API_URL", "MONITORING_WEBHOOK_URL", "FROM_EMAIL", "REPLY_TO_EMAIL", "WEBHOOK_API_KEY"]
}
```

## 🔧 **Troubleshooting**

### **Environment Variables Not Showing Up?**

1. **Check pod restart:**
```bash
kubectl get pods -n YOUR-NAMESPACE -w
# Pods should restart after applying the patch
```

2. **Check ConfigMap/Secret mounting:**
```bash
kubectl describe pod $POD_NAME -n YOUR-NAMESPACE | grep -A 10 "Environment"
```

3. **Check logs for errors:**
```bash
kubectl logs deployment/n8n -n YOUR-NAMESPACE --tail=50
```

4. **Verify ConfigMap/Secret exist:**
```bash
kubectl get configmap n8n-workflow-config -n YOUR-NAMESPACE -o yaml
kubectl get secret n8n-workflow-secrets -n YOUR-NAMESPACE -o yaml
```

### **If Patch Fails:**

Try manual editing:
```bash
kubectl edit deployment n8n -n YOUR-NAMESPACE
```

Add under `spec.template.spec.containers[0]`:
```yaml
envFrom:
- configMapRef:
    name: n8n-workflow-config
- secretRef:
    name: n8n-workflow-secrets
```

### **Alternative: Individual Environment Variables**

If `envFrom` doesn't work, use individual `env` entries (see k8s-deployment-patch.yaml for examples).

## 🎯 **Next Steps After Successful Setup**

1. **Import Enhanced Workflows:**
   - `NEW_CLIENT_ASSESSMENT_TEMPLATE_WITH_RESEND.json`
   - `NEW_CLIENT_ASSESSMENT_TEMPLATE.json`

2. **Test Assessment Endpoint:**
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

3. **Monitor Execution Logs** in n8n interface

## 📋 **Configuration Summary**

**ConfigMap Variables:**
- `CREWAI_API_URL` - Your CrewAI API endpoint
- `MONITORING_WEBHOOK_URL` - Monitoring endpoint
- `FROM_EMAIL` - Email sender address
- `REPLY_TO_EMAIL` - Email reply-to address
- `WEBHOOK_URL` - N8N webhook base URL

**Secret Variables:**
- `WEBHOOK_API_KEY` - Webhook authentication
- `RESEND_API_KEY` - Resend email service key

**All variables will be available in workflows as `$env.VARIABLE_NAME`** 🚀