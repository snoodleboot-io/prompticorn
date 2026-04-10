#!/usr/bin/env python3
"""Migrate bundled prompts from old format to IR format.

OLD format:
- kilo_modes.yaml with system prompts
- agents/{mode}/subagents/{mode}-{name}.md files

NEW IR format:
- agents/{mode}/minimal/prompt.md
- agents/{mode}/verbose/prompt.md  
- agents/{mode}/subagents/{name}/minimal/prompt.md
- agents/{mode}/subagents/{name}/verbose/prompt.md
"""

import yaml
from pathlib import Path
import shutil

# Get the kilo_modes.yaml from git history
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

def migrate():
    """Migrate all agents to IR format."""
    
    # Load kilo_modes.yaml
    kilo_data = get_kilo_modes_from_git()
    modes = {mode['slug']: mode for mode in kilo_data['customModes']}
    
    prompts_dir = Path("promptosaurus/prompts/agents")
    new_agents_dir = Path("promptosaurus/agents")
    
    # Create new agents directory
    new_agents_dir.mkdir(exist_ok=True)
    
    # Migrate each mode
    for mode_slug, mode_data in modes.items():
        print(f"\n Processing {mode_slug}...")
        
        mode_dir = new_agents_dir / mode_slug
        mode_dir.mkdir(exist_ok=True)
        
        # Create minimal variant
        minimal_dir = mode_dir / "minimal"
        minimal_dir.mkdir(exist_ok=True)
        
        # Create prompt.md from roleDefinition
        role_definition = mode_data.get('roleDefinition', '')
        description = mode_data.get('description', '')
        
        minimal_prompt = f"""---
name: {mode_slug}
description: {description}
---

{role_definition}

{mode_data.get('whenToUse', '')}
"""
        
        (minimal_dir / "prompt.md").write_text(minimal_prompt.strip() + "\n")
        print(f"  ✓ Created {mode_slug}/minimal/prompt.md")
        
        # Create verbose variant (same for now, can enhance later)
        verbose_dir = mode_dir / "verbose"
        verbose_dir.mkdir(exist_ok=True)
        (verbose_dir / "prompt.md").write_text(minimal_prompt.strip() + "\n")
        print(f"  ✓ Created {mode_slug}/verbose/prompt.md")
        
        # Migrate subagents
        old_subagents_dir = prompts_dir / mode_slug / "subagents"
        if old_subagents_dir.exists():
            new_subagents_dir = mode_dir / "subagents"
            new_subagents_dir.mkdir(exist_ok=True)
            
            for subagent_file in old_subagents_dir.glob("*.md"):
                # Extract subagent name: "test-strategy.md" -> "strategy"
                subagent_name = subagent_file.stem.replace(f"{mode_slug}-", "")
                
                subagent_dir = new_subagents_dir / subagent_name
                subagent_dir.mkdir(exist_ok=True)
                
                # Create minimal variant
                subagent_minimal = subagent_dir / "minimal"
                subagent_minimal.mkdir(exist_ok=True)
                
                # Read old subagent content
                content = subagent_file.read_text()
                
                # Create IR format with frontmatter
                ir_content = f"""---
name: {subagent_name}
description: {mode_slug.capitalize()} - {subagent_name}
---

{content}
"""
                
                (subagent_minimal / "prompt.md").write_text(ir_content)
                print(f"  ✓ Created {mode_slug}/subagents/{subagent_name}/minimal/prompt.md")
                
                # Create verbose variant (copy for now)
                subagent_verbose = subagent_dir / "verbose"
                subagent_verbose.mkdir(exist_ok=True)
                (subagent_verbose / "prompt.md").write_text(ir_content)
                print(f"  ✓ Created {mode_slug}/subagents/{subagent_name}/verbose/prompt.md")

if __name__ == "__main__":
    migrate()
    print("\n✅ Migration complete! New IR format in promptosaurus/agents/")
    print("\nNext steps:")
    print("1. Review generated files")
    print("2. Update PromptBuilder to use promptosaurus/agents/")
    print("3. Delete promptosaurus/prompts/agents/ (old format)")
