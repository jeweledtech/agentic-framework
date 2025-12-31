#!/usr/bin/env python3
"""
Fix HubSpot credentials in all n8n workflow files.

Changes:
- "hubspotApi" -> "hubspotAppToken"
- "HubSpot API" -> "HubSpot Private App"

Usage: python scripts/fix_hubspot_credentials.py
"""

import os
import json
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).parent.parent / "n8n_workflows"

def fix_hubspot_credentials(file_path: Path) -> bool:
    """Fix HubSpot credentials in a single file. Returns True if changes were made."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Replace credential type
        content = content.replace('"hubspotApi":', '"hubspotAppToken":')
        content = content.replace("'hubspotApi':", "'hubspotAppToken':")

        # Replace credential name
        content = content.replace('"name": "HubSpot API"', '"name": "HubSpot Private App"')
        content = content.replace('"name":"HubSpot API"', '"name":"HubSpot Private App"')

        # Also fix the id reference if it exists
        content = content.replace('"id": "hubspotApi"', '"id": "hubspot_private_app"')
        content = content.replace('"id":"hubspotApi"', '"id":"hubspot_private_app"')

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"  Error processing {file_path.name}: {e}")
        return False

def main():
    print("=" * 60)
    print("Fixing HubSpot Credentials in n8n Workflows")
    print("=" * 60)
    print(f"\nScanning: {WORKFLOWS_DIR}\n")

    files_updated = []
    files_skipped = []

    # Process all JSON files
    for json_file in WORKFLOWS_DIR.rglob("*.json"):
        if fix_hubspot_credentials(json_file):
            files_updated.append(json_file.name)
            print(f"  [UPDATED] {json_file.relative_to(WORKFLOWS_DIR)}")
        else:
            files_skipped.append(json_file.name)

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Files updated: {len(files_updated)}")
    print(f"Files unchanged: {len(files_skipped)}")

    if files_updated:
        print("\nUpdated files:")
        for f in files_updated:
            print(f"  - {f}")

    print("\nChanges made:")
    print("  - 'hubspotApi' -> 'hubspotAppToken'")
    print("  - 'HubSpot API' -> 'HubSpot Private App'")
    print("\nDone! You can now re-import these workflows into n8n.")

if __name__ == "__main__":
    main()
