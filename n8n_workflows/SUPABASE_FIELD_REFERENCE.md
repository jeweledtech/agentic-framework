# Supabase Field Reference - Enhanced Assessments

## Complete Field Mapping for `enhanced_assessments` Table

This reference shows the correct field structure for Supabase nodes in n8n workflows.

### Required Field Structure

Each field in the Supabase node must have THREE properties:
1. **fieldId** - The actual database column name (snake_case)
2. **fieldName** - The display name (same as fieldId)
3. **fieldValue** - The n8n expression to get the value

### Complete Field List

```json
{
  "parameters": {
    "resource": "row",
    "operation": "create",
    "tableId": "enhanced_assessments",
    "dataToSend": "defineBelow",
    "fieldsUi": {
      "fieldValues": [
        {
          "fieldId": "company_name",
          "fieldName": "company_name",
          "fieldValue": "={{ $json.companyName }}"
        },
        {
          "fieldId": "vertical",
          "fieldName": "vertical",
          "fieldValue": "={{ $json.industry }}"
        },
        {
          "fieldId": "company_size",
          "fieldName": "company_size",
          "fieldValue": "={{ $json.companySize }}"
        },
        {
          "fieldId": "company_description",
          "fieldName": "company_description",
          "fieldValue": "={{ $json.companyDescription }}"
        },
        {
          "fieldId": "strategic_priorities",
          "fieldName": "strategic_priorities",
          "fieldValue": "={{ $json.strategicPriorities }}"
        },
        {
          "fieldId": "operational_bottlenecks",
          "fieldName": "operational_bottlenecks",
          "fieldValue": "={{ $json.operationalBottlenecks }}"
        },
        {
          "fieldId": "departments_of_interest",
          "fieldName": "departments_of_interest",
          "fieldValue": "={{ $json.departmentsOfInterest }}"
        },
        {
          "fieldId": "crm_platforms",
          "fieldName": "crm_platforms",
          "fieldValue": "={{ [$json.crmPlatform] }}"
        },
        {
          "fieldId": "communication_platforms",
          "fieldName": "communication_platforms",
          "fieldValue": "={{ $json.communicationPlatforms }}"
        },
        {
          "fieldId": "project_management_platforms",
          "fieldName": "project_management_platforms",
          "fieldValue": "={{ [$json.projectManagement] }}"
        },
        {
          "fieldId": "knowledge_base_status",
          "fieldName": "knowledge_base_status",
          "fieldValue": "={{ $json.knowledgeBaseStatus }}"
        },
        {
          "fieldId": "api_experience",
          "fieldName": "api_experience",
          "fieldValue": "={{ $json.apiExperience }}"
        },
        {
          "fieldId": "ai_capabilities",
          "fieldName": "ai_capabilities",
          "fieldValue": "={{ $json.aiCapabilities }}"
        },
        {
          "fieldId": "key_automation_task",
          "fieldName": "key_automation_task",
          "fieldValue": "={{ $json.automationTask }}"
        },
        {
          "fieldId": "name",
          "fieldName": "name",
          "fieldValue": "={{ $json.contactName }}"
        },
        {
          "fieldId": "email",
          "fieldName": "email",
          "fieldValue": "={{ $json.contactEmail }}"
        },
        {
          "fieldId": "phone",
          "fieldName": "phone",
          "fieldValue": "={{ $json.contactPhone }}"
        },
        {
          "fieldId": "consent",
          "fieldName": "consent",
          "fieldValue": "=true"
        }
      ]
    }
  }
}
```

## Important Notes

### Array Fields
These fields expect arrays in the database, so single values must be wrapped:
- `crm_platforms` - Wrapped as `={{ [$json.crmPlatform] }}`
- `project_management_platforms` - Wrapped as `={{ [$json.projectManagement] }}`

### Field Name Conventions
- **Database columns**: snake_case (e.g., `company_name`)
- **JSON properties**: camelCase (e.g., `companyName`)
- **n8n expressions**: Convert from camelCase to snake_case

### Common Issues
1. **Missing fieldId** - Causes "empty column" error
2. **Wrong case** - PostgreSQL is case-sensitive
3. **Missing array wrapping** - Single values need `[...]` for array columns

## Using in n8n UI

When adding fields manually in n8n:
1. Click "Add Field"
2. Select the field from dropdown (this sets fieldId and fieldName)
3. Enter the expression value
4. The UI will automatically add all three properties

## Updated Workflows

The following workflows have been fixed with proper field IDs:
- `NEW_CLIENT_ASSESSMENT_TEMPLATE.json`
- `NEW_CLIENT_ASSESSMENT_TEMPLATE_WITH_RESEND.json`

These can now be imported directly into n8n without manual field selection!