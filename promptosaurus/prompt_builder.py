"""Wrapper to build prompts for AI tools from bundled agent configurations.

This module provides a builder wrapper that allows the existing CLI commands
to work with Phase 2A IR-based builders without changing the CLI interface.

The adapter:
1. Loads agents from promptosaurus/prompts/agents/ into IR models
2. Converts CLI config into build options
3. Calls Phase 2A builders
4. Writes output files

This keeps the user-facing CLI unchanged while using the new Phase 2A system internally.
"""

from pathlib import Path
from typing import Any

from promptosaurus.agent_registry.registry import Registry
from promptosaurus.builders.factory import BuilderFactory
from promptosaurus.builders.base import BuildOptions
from promptosaurus.ir.models import Agent


class PromptBuilder:
    """Adapter that mimics legacy builder interface using Phase 2A builders.
    
    This adapter allows the CLI to use Phase 2A builders while maintaining
    the same interface as legacy builders.
    
    Legacy interface:
        builder.build(output_path: Path, config: dict, dry_run: bool) -> list[str]
    
    Phase 2A interface (internal):
        builder.build(agent: Agent, options: BuildOptions) -> str | dict
    """
    
    def __init__(self, tool_name: str):
        """Initialize adapter for a specific tool.
        
        Args:
            tool_name: Tool name ('kilo', 'cline', 'claude', 'copilot', 'cursor')
        """
        self.tool_name = tool_name
        self.builder = BuilderFactory.get_builder(tool_name)
        
        # Load agents from bundled prompts directory
        prompts_dir = Path(__file__).parent / "prompts" / "agents"
        self.registry = Registry.from_discovery(prompts_dir)
    
    def build(
        self, 
        output: Path, 
        config: dict[str, Any] | None = None, 
        dry_run: bool = False
    ) -> list[str]:
        """Build tool-specific outputs using Phase 2A builders.
        
        This method maintains compatibility with the legacy builder interface
        while using Phase 2A IR-based builders internally.
        
        Args:
            output: Output directory path
            config: Project configuration (language, runtime, etc.)
            dry_run: If True, don't write files (preview only)
        
        Returns:
            List of action strings describing what was created
        """
        actions = []
        
        # Get all agents from registry
        all_agents = self.registry.get_all_agents()
        
        # Build each agent
        for agent_name, agent in all_agents.items():
            # Skip subagents for now (they're included in parent agent)
            if "/" in agent_name:
                continue
            
            try:
                # Use minimal variant by default
                options = BuildOptions(
                    variant="minimal",
                    agent_name=agent_name,
                )
                
                # Build the agent
                output_content = self.builder.build(agent, options)
                
                # Write output based on tool
                if not dry_run:
                    written_files = self._write_output(output, agent_name, output_content)
                    actions.extend([f"✓ {f}" for f in written_files])
                else:
                    actions.append(f"[dry-run] Would build {agent_name} for {self.tool_name}")
                    
            except Exception as e:
                actions.append(f"✗ Failed to build {agent_name}: {e}")
        
        return actions
    
    def _write_output(
        self, 
        output: Path, 
        agent_name: str, 
        content: str | dict[str, Any]
    ) -> list[str]:
        """Write builder output to appropriate files.
        
        Args:
            output: Output directory
            agent_name: Name of the agent
            content: Builder output (string or dict)
        
        Returns:
            List of files written
        """
        written_files = []
        
        if self.tool_name == "kilo":
            # Kilo: .kilo/agents/{agent_name}.md
            agents_dir = output / ".kilo" / "agents"
            agents_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = agents_dir / f"{agent_name}.md"
            file_path.write_text(str(content), encoding="utf-8")
            written_files.append(f".kilo/agents/{agent_name}.md")
            
        elif self.tool_name == "cline":
            # Cline: .clinerules (concatenated)
            file_path = output / ".clinerules"
            
            # Append to existing or create new
            if file_path.exists():
                existing = file_path.read_text(encoding="utf-8")
                file_path.write_text(f"{existing}\n\n{content}", encoding="utf-8")
            else:
                file_path.write_text(str(content), encoding="utf-8")
            written_files.append(".clinerules")
            
        elif self.tool_name == "claude":
            # Claude: custom_instructions/{agent_name}.json
            instructions_dir = output / "custom_instructions"
            instructions_dir.mkdir(parents=True, exist_ok=True)
            
            import json
            file_path = instructions_dir / f"{agent_name}.json"
            file_path.write_text(json.dumps(content, indent=2), encoding="utf-8")
            written_files.append(f"custom_instructions/{agent_name}.json")
            
        elif self.tool_name == "copilot":
            # Copilot: .github/copilot-instructions.md (concatenated)
            github_dir = output / ".github"
            github_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = github_dir / "copilot-instructions.md"
            if file_path.exists():
                existing = file_path.read_text(encoding="utf-8")
                file_path.write_text(f"{existing}\n\n{content}", encoding="utf-8")
            else:
                file_path.write_text(str(content), encoding="utf-8")
            written_files.append(".github/copilot-instructions.md")
            
        elif self.tool_name == "cursor":
            # Cursor: .cursorrules
            file_path = output / ".cursorrules"
            if file_path.exists():
                existing = file_path.read_text(encoding="utf-8")
                file_path.write_text(f"{existing}\n\n{content}", encoding="utf-8")
            else:
                file_path.write_text(str(content), encoding="utf-8")
            written_files.append(".cursorrules")
        
        return written_files


def get_prompt_builder(tool: str) -> PromptBuilder:
    """Get Phase 2A builder adapter for a tool.
    
    This replaces the legacy _get_builder() function, maintaining the
    same interface while using Phase 2A builders internally.
    
    Args:
        tool: Tool name (e.g., 'kilo-cli', 'kilo-ide', 'cline', 'cursor', 'copilot')
    
    Returns:
        Builder adapter instance
    
    Raises:
        ValueError: If tool is unknown
    """
    # Map tool names to Phase 2A builder names
    tool_mapping = {
        "kilo-cli": "kilo",
        "kilo-ide": "kilo",
        "cline": "cline",
        "cursor": "cursor",
        "copilot": "copilot",
        "claude": "claude",
    }
    
    phase2a_tool = tool_mapping.get(tool)
    if not phase2a_tool:
        raise ValueError(f"Unknown tool: {tool}")
    
    return PromptBuilder(phase2a_tool)
