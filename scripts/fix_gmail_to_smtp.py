#!/usr/bin/env python3
"""
Convert Gmail OAuth2 nodes to SMTP Email nodes in n8n workflows.

This makes the workflows easier to configure since SMTP with App Password
is much simpler than Google OAuth2.

Changes:
- "n8n-nodes-base.gmail" -> "n8n-nodes-base.emailSend"
- "gmailOAuth2" credentials -> "smtp" credentials
- Updates parameter structure for SMTP compatibility

Usage: python scripts/fix_gmail_to_smtp.py
"""

import os
import json
import re
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).parent.parent / "n8n_workflows"

def fix_gmail_to_smtp(file_path: Path) -> bool:
    """Convert Gmail nodes to SMTP in a single file. Returns True if changes were made."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Replace node type
        content = content.replace('"type": "n8n-nodes-base.gmail"', '"type": "n8n-nodes-base.emailSend"')
        content = content.replace('"type":"n8n-nodes-base.gmail"', '"type":"n8n-nodes-base.emailSend"')

        # Replace credential type and name
        content = content.replace('"gmailOAuth2":', '"smtp":')
        content = content.replace('"name": "Gmail OAuth2"', '"name": "SMTP Gmail"')
        content = content.replace('"name":"Gmail OAuth2"', '"name":"SMTP Gmail"')

        # Replace credential id
        content = content.replace('"id": "gmailOAuth2"', '"id": "smtp_gmail"')
        content = content.replace('"id":"gmailOAuth2"', '"id":"smtp_gmail"')

        # Update parameter names for SMTP compatibility
        # sendTo -> toEmail
        content = content.replace('"sendTo":', '"toEmail":')

        # message -> text (for plain text emails)
        # But be careful not to replace "messageType" or other message-related fields
        content = re.sub(r'"message":\s*"([^"]*)"', r'"text": "\1"', content)

        # Update typeVersion for emailSend (use version 2.1)
        content = re.sub(
            r'("type":\s*"n8n-nodes-base\.emailSend",\s*"typeVersion":\s*)\d+(\.\d+)?',
            r'\g<1>2.1',
            content
        )

        # Also update node names to reflect SMTP
        content = content.replace('"name": "Send Email"', '"name": "Send Email (SMTP)"')
        content = content.replace('"name": "Gmail Send"', '"name": "Send Email (SMTP)"')
        content = content.replace('"name": "Send Gmail"', '"name": "Send Email (SMTP)"')

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"  Error processing {file_path.name}: {e}")
        return False


def update_readme_docs(file_path: Path) -> bool:
    """Update documentation files to reference SMTP instead of Gmail OAuth."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Update credential references in docs
        content = content.replace('Gmail OAuth2', 'SMTP (Gmail App Password)')
        content = content.replace('### Gmail OAuth2', '### SMTP Email (Gmail)')
        content = content.replace('- **Type**: Gmail OAuth2', '- **Type**: SMTP')
        content = content.replace('- **OAuth Client**: From Google Cloud Console',
                                  '- **Host**: smtp.gmail.com\n- **Port**: 465\n- **User**: your Gmail\n- **Password**: App Password from Google')

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
    print("Converting Gmail OAuth2 to SMTP in n8n Workflows")
    print("=" * 60)
    print(f"\nScanning: {WORKFLOWS_DIR}\n")

    json_updated = []
    md_updated = []
    files_skipped = []

    # Process JSON workflow files
    for json_file in WORKFLOWS_DIR.rglob("*.json"):
        if fix_gmail_to_smtp(json_file):
            json_updated.append(json_file.name)
            print(f"  [UPDATED] {json_file.relative_to(WORKFLOWS_DIR)}")

    # Process markdown documentation
    for md_file in WORKFLOWS_DIR.rglob("*.md"):
        if update_readme_docs(md_file):
            md_updated.append(md_file.name)
            print(f"  [DOCS] {md_file.relative_to(WORKFLOWS_DIR)}")

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Workflow files updated: {len(json_updated)}")
    print(f"Documentation updated: {len(md_updated)}")

    if json_updated:
        print("\nUpdated workflow files:")
        for f in json_updated:
            print(f"  - {f}")

    print("\nChanges made:")
    print("  - 'n8n-nodes-base.gmail' -> 'n8n-nodes-base.emailSend'")
    print("  - 'gmailOAuth2' credentials -> 'smtp' credentials")
    print("  - 'Gmail OAuth2' -> 'SMTP Gmail'")
    print("  - Parameter updates for SMTP compatibility")

    print("\n" + "=" * 60)
    print("SMTP Credential Setup in n8n")
    print("=" * 60)
    print("""
To configure SMTP in n8n:

1. Go to Credentials -> Add Credential -> SMTP
2. Enter:
   - Host: smtp.gmail.com
   - Port: 465
   - SSL/TLS: true
   - User: your-email@gmail.com
   - Password: [16-char App Password from Google]

3. Name it: "SMTP Gmail"
4. Save

Get App Password: https://myaccount.google.com/apppasswords
""")

if __name__ == "__main__":
    main()
