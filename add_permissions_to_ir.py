#!/usr/bin/env python3
"""Add permissions from kilo_modes.yaml to IR prompt.md files."""

import yaml
from pathlib import Path
import subprocess

def get_kilo_modes_from_git():
    """Get kilo_modes.yaml content from git history."""
    result = subprocess.run(
        ["git", "show", "HEAD~7:promptosaurus/builders/legacy/kilo/kilo_modes.yaml"],
        capture_output=True,
        text=True,
        check=True
    )
    return yaml.safe_load(result.stdout)

def map_groups_to_permissions(groups):
    """Map old groups format to Kilo permission YAML."""
    permissions = {}
    
    for group in groups:
        if isinstance(group, str):
            # Simple permission
            if group == "read":
                permissions["read"] = {"*": "allow"}
            elif group == "edit":
                permissions["edit"] = {"*": "allow"}
            elif group == "command":
                permissions["bash"] = "allow"
            elif group == "browser":
                # Browser not directly supported in new format
                pass
        elif isinstance(group, list) and len(group) >= 2:
            # Complex permission: ["edit", {fileRegex: "...", description: "..."}]
            perm_type = group[0]
            restriction = group[1] if len(group) > 1 else {}
            
            if perm_type == "edit" and isinstance(restriction, dict):
                permissions["edit"] = {}
                pattern = restriction.get("fileRegex", "")
                if pattern:
                    permissions["edit"][pattern] = "allow"
                # Default deny for everything else
                permissions["edit"]["*"] = "deny"
    
    # Ensure read permission
    if "read" not in permissions:
        permissions["read"] = {"*": "allow"}
    
    return permissions

def add_permissions():
    """Add permissions to all IR prompt.md files."""
    
    # Load kilo_modes.yaml
    kilo_data = get_kilo_modes_from_git()
    modes = {mode['slug']: mode for mode in kilo_data['customModes']}
    
    agents_dir = Path("promptosaurus/agents")
    
    for mode_slug, mode_data in modes.items():
        print(f"\nProcessing {mode_slug}...")
        
        # Get permissions
        groups = mode_data.get('groups', [])
        permissions = map_groups_to_permissions(groups)
        
        # Update both minimal and verbose
        for variant in ['minimal', 'verbose']:
            prompt_file = agents_dir / mode_slug / variant / "prompt.md"
            
            if not prompt_file.exists():
                print(f"  ⚠ Skipping {variant} (doesn't exist)")
                continue
            
            # Read current content
            content = prompt_file.read_text()
            
            # Parse frontmatter
            if not content.startswith("---"):
                print(f"  ⚠ Skipping {variant} (no frontmatter)")
                continue
            
            # Find end of frontmatter
            end_marker = content.find("---", 3)
            if end_marker == -1:
                print(f"  ⚠ Skipping {variant} (malformed frontmatter)")
                continue
            
            frontmatter_str = content[4:end_marker].strip()
            body = content[end_marker + 3:].strip()
            
            # Parse existing frontmatter
            try:
                frontmatter = yaml.safe_load(frontmatter_str) or {}
            except:
                frontmatter = {}
            
            # Add permissions
            frontmatter['permissions'] = permissions
            
            # Rebuild file
            new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            new_content = f"---\n{new_frontmatter}---\n\n{body}\n"
            
            # Write back
            prompt_file.write_text(new_content)
            print(f"  ✓ Updated {variant}/prompt.md - permissions: {list(permissions.keys())}")

if __name__ == "__main__":
    add_permissions()
    print("\n✅ Permissions added to all IR prompt.md files!")
