# 🔧 Supabase Array Fields Fix

## 🚨 **Issue Found:**
`malformed array literal: ""` - Supabase is receiving empty arrays incorrectly.

## 🎯 **Quick Fix for the Save to Supabase Node:**

In the Supabase node field mappings, change these array fields:

### **Current (causing errors):**
```javascript
"fieldValue": "={{ $json.communicationPlatforms }}"
"fieldValue": "={{ $json.aiCapabilities }}"
"fieldValue": "={{ $json.departmentsOfInterest }}"
```

### **Fixed (handles empty arrays):**
```javascript
"fieldValue": "={{ $json.communicationPlatforms.length > 0 ? $json.communicationPlatforms : null }}"
"fieldValue": "={{ $json.aiCapabilities.length > 0 ? $json.aiCapabilities : null }}"
"fieldValue": "={{ $json.departmentsOfInterest.length > 0 ? $json.departmentsOfInterest : null }}"
```

## 🛠️ **Manual Fix Steps:**

1. **Go to your n8n workflow**
2. **Open "Save to Supabase" node**
3. **Find these field mappings and update them:**

   - **communication_platforms**: `{{ $json.communicationPlatforms.length > 0 ? $json.communicationPlatforms : null }}`
   - **ai_capabilities**: `{{ $json.aiCapabilities.length > 0 ? $json.aiCapabilities : null }}`
   - **departments_of_interest**: `{{ $json.departmentsOfInterest.length > 0 ? $json.departmentsOfInterest : null }}`

4. **Save the workflow**

## ⚡ **Alternative: Simple Fix**

Or use this simpler approach:
```javascript
"fieldValue": "={{ $json.communicationPlatforms || [] }}"
"fieldValue": "={{ $json.aiCapabilities || [] }}"
"fieldValue": "={{ $json.departmentsOfInterest || ['General'] }}"
```

This ensures arrays are never completely empty.