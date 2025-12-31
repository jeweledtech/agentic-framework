#!/usr/bin/env python3
"""
n8n MCP Integration Test Script

Tests the connection to your n8n Cloud instance via Instance-level MCP.
Usage: python scripts/test_n8n_mcp.py
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

N8N_MCP_URL = os.getenv('N8N_MCP_SERVER_URI', 'https://jtsinc.app.n8n.cloud/mcp-server/http')
N8N_MCP_TOKEN = os.getenv('N8N_MCP_TOKEN', '')

def get_headers():
    """Get headers for n8n MCP requests."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': f'Bearer {N8N_MCP_TOKEN}'
    }

def parse_sse_response(response_text):
    """Parse SSE response from n8n MCP."""
    for line in response_text.split('\n'):
        if line.startswith('data: '):
            return json.loads(line[6:])
    return None

def list_tools():
    """List available MCP tools."""
    print("\n=== Listing MCP Tools ===")

    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }

    response = requests.post(N8N_MCP_URL, headers=get_headers(), json=payload)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None

    result = parse_sse_response(response.text)

    if result and 'result' in result:
        tools = result['result'].get('tools', [])
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
        return tools

    return None

def search_workflows(query=""):
    """Search for workflows in n8n."""
    print(f"\n=== Searching Workflows (query: '{query}') ===")

    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "search_workflows",
            "arguments": {
                "searchQuery": query
            }
        },
        "id": 2
    }

    response = requests.post(N8N_MCP_URL, headers=get_headers(), json=payload)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None

    result = parse_sse_response(response.text)

    if result and 'result' in result:
        content = result['result'].get('content', [])
        if content:
            text = content[0].get('text', '{}')
            workflows_data = json.loads(text)

            # Handle n8n response format: {"data": [...], "count": N}
            if isinstance(workflows_data, dict) and 'data' in workflows_data:
                workflows = workflows_data.get('data', [])
                count = workflows_data.get('count', len(workflows))
                print(f"Found {count} workflows:")
                for wf in workflows:
                    if isinstance(wf, dict):
                        status = "Active" if wf.get('active') else "Inactive"
                        print(f"  [{wf.get('id')}] {wf.get('name')} ({status})")
                return workflows
            # Handle direct list format
            elif isinstance(workflows_data, list):
                print(f"Found {len(workflows_data)} workflows:")
                for wf in workflows_data:
                    if isinstance(wf, dict):
                        status = "Active" if wf.get('active') else "Inactive"
                        print(f"  [{wf.get('id')}] {wf.get('name')} ({status})")
                    else:
                        print(f"  - {wf}")
                return workflows_data

    print("No workflows found. Import workflows from n8n_workflows/ folder.")
    return []

def get_workflow_details(workflow_id):
    """Get details of a specific workflow."""
    print(f"\n=== Getting Workflow Details (ID: {workflow_id}) ===")

    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_workflow_details",
            "arguments": {
                "workflowId": workflow_id
            }
        },
        "id": 3
    }

    response = requests.post(N8N_MCP_URL, headers=get_headers(), json=payload)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None

    result = parse_sse_response(response.text)

    if result and 'result' in result:
        content = result['result'].get('content', [])
        if content:
            text = content[0].get('text', '{}')
            details = json.loads(text)
            print(f"Workflow: {details.get('name')}")
            print(f"  ID: {details.get('id')}")
            print(f"  Active: {details.get('active')}")
            print(f"  Input Schema: {json.dumps(details.get('inputSchema', {}), indent=2)}")
            return details

    return None

def execute_workflow(workflow_id, input_data=None):
    """Execute a workflow by ID."""
    print(f"\n=== Executing Workflow (ID: {workflow_id}) ===")

    if input_data is None:
        input_data = {"test": True, "source": "mcp_test_script"}

    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "execute_workflow",
            "arguments": {
                "workflowId": workflow_id,
                "inputData": input_data
            }
        },
        "id": 4
    }

    response = requests.post(N8N_MCP_URL, headers=get_headers(), json=payload)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None

    result = parse_sse_response(response.text)

    if result and 'result' in result:
        content = result['result'].get('content', [])
        if content:
            text = content[0].get('text', '{}')
            execution_result = json.loads(text)
            print(f"Execution Result:")
            print(json.dumps(execution_result, indent=2))
            return execution_result

    return None

def main():
    """Main test function."""
    print("=" * 60)
    print("n8n MCP Integration Test")
    print("=" * 60)
    print(f"MCP URL: {N8N_MCP_URL}")
    print(f"Token: {'*' * 20}...{N8N_MCP_TOKEN[-10:] if len(N8N_MCP_TOKEN) > 10 else '(not set)'}")

    if not N8N_MCP_TOKEN:
        print("\nError: N8N_MCP_TOKEN not set in .env")
        print("Get your token from n8n Settings > Instance-level MCP")
        sys.exit(1)

    # Test 1: List available tools
    tools = list_tools()
    if not tools:
        print("\nFailed to connect to n8n MCP. Check your token.")
        sys.exit(1)

    # Test 2: Search for workflows
    workflows = search_workflows()

    # Test 3: If workflows exist, get details of first one
    if workflows:
        first_wf = workflows[0]
        get_workflow_details(first_wf['id'])

        # Ask if user wants to execute
        print(f"\nWould you like to execute workflow '{first_wf['name']}'?")
        print("(This is a test - be careful with production workflows)")
        # Uncomment below to enable execution test:
        # execute_workflow(first_wf['id'])

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Import workflows from n8n_workflows/ folder in n8n UI")
    print("2. Configure credentials (HubSpot, Gmail, Supabase)")
    print("3. Activate workflows")
    print("4. Run this script again to verify")

if __name__ == "__main__":
    main()
