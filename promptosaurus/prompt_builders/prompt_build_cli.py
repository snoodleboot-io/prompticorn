"""Command-line interface for the prompt-build tool.

This module provides the CLI interface for building tool-specific agent
configurations from the unified IR models. Users can specify the target tool
(kilo, claude, cline, copilot, cursor), agent name, output variant, and
output destination.

Usage:
    prompt-build --tool kilo --agent code --variant minimal --output .kilo/agents/
    prompt-build --tool claude --agent architect --variant verbose --output ./
    prompt-build --tool cline --agent code --output ./outputs/
    prompt-build --help
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, NoReturn

from promptosaurus.agent_registry.errors import AgentNotFoundError
from promptosaurus.agent_registry.registry import Registry
from promptosaurus.builders.base import Builder, BuildOptions
from promptosaurus.builders.errors import BuilderException, BuilderNotFoundError
from promptosaurus.builders.factory import BuilderFactory
from promptosaurus.ir.models import Agent


class PromptBuildCLI:
    """Command-line interface for prompt-build tool.

    Handles argument parsing, agent loading, builder selection, and output
    file writing. Provides user-friendly error messages and help documentation.
    """

    # Tool output filename mapping
    OUTPUT_FILENAMES = {
        "kilo": "{agent_name}.md",
        "claude": "{agent_name}.json",
        "cline": ".clinerules",
        "copilot": "{agent_name}.md",
        "cursor": ".cursorrules",
    }

    # Output directory mapping for special tools
    OUTPUT_SUBDIRS = {
        "copilot": ".github/instructions",
    }

    def __init__(self, agents_dir: str | Path = "agents") -> None:
        """Initialize CLI with agents directory.

        Args:
            agents_dir: Path to agents directory for discovery
        """
        self.agents_dir = Path(agents_dir)
        self.registry = Registry.from_discovery(self.agents_dir)

    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser.

        Returns:
            Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            prog="prompt-build",
            description="Build tool-specific agent configurations from unified IR models",
            epilog=(
                "Examples:\n"
                "  prompt-build --tool kilo --agent code\n"
                "  prompt-build --tool claude --agent architect --variant verbose\n"
                "  prompt-build --tool cline --agent code --output ./outputs/"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument(
            "--tool",
            required=True,
            choices=["kilo", "claude", "cline", "copilot", "cursor"],
            help="Target tool to build for (kilo, claude, cline, copilot, cursor)",
        )

        parser.add_argument(
            "--agent",
            required=True,
            help="Name of agent to build (e.g., code, architect, test)",
        )

        parser.add_argument(
            "--variant",
            default="minimal",
            choices=["minimal", "verbose"],
            help="Build variant (minimal or verbose, default: minimal)",
        )

        parser.add_argument(
            "--output",
            default=".",
            help="Output directory or file path (default: current directory)",
        )

        parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s 0.1.0",
        )

        return parser

    def get_builder(self, tool: str) -> Builder:
        """Get builder instance for the specified tool.

        Args:
            tool: Tool name (kilo, claude, cline, copilot, cursor)

        Returns:
            Builder instance

        Raises:
            BuilderNotFoundError: If builder is not available
        """
        try:
            return BuilderFactory.get_builder(tool)
        except BuilderNotFoundError:
            available = BuilderFactory.list_builders()
            self._error(
                f"Builder not found for tool '{tool}'.\nAvailable tools: {', '.join(available)}",
                exit_code=1,
            )

    def load_agent(self, agent_name: str) -> Agent:
        """Load agent from registry.

        Args:
            agent_name: Name of agent to load

        Returns:
            Agent IR model

        Raises:
            AgentNotFoundError: If agent is not found
        """
        try:
            return self.registry.get_agent(agent_name)
        except AgentNotFoundError:
            available = self.registry.list_agents()
            if available:
                self._error(
                    f"Agent '{agent_name}' not found.\nAvailable agents: {', '.join(available)}",
                    exit_code=1,
                )
            else:
                self._error(
                    f"Agent '{agent_name}' not found.\nNo agents discovered in {self.agents_dir}",
                    exit_code=1,
                )

    def build_output(
        self, builder: Builder, agent: Agent, tool: str, variant: str
    ) -> str | dict[str, Any]:
        """Build output using the specified builder.

        Args:
            builder: Builder instance
            agent: Agent IR model
            tool: Tool name (for context in error messages)
            variant: Build variant (minimal or verbose)

        Returns:
            Built output (string or dict depending on builder)

        Raises:
            BuilderException: If build fails
        """
        try:
            options = BuildOptions(
                variant=variant,
                agent_name=agent.name,
            )
            return builder.build(agent, options)
        except BuilderException as e:
            self._error(
                f"Failed to build agent with {tool} builder: {e}",
                exit_code=1,
            )

    def determine_output_path(self, output_arg: str, tool: str, agent_name: str) -> Path:
        """Determine the output file path based on arguments.

        Args:
            output_arg: Output argument from CLI
            tool: Tool name
            agent_name: Agent name

        Returns:
            Full path to output file

        Raises:
            ValueError: If output path cannot be determined
        """
        output_path = Path(output_arg)

        # Handle special tools with subdirectories
        if tool in self.OUTPUT_SUBDIRS:
            output_path = output_path / self.OUTPUT_SUBDIRS[tool]

        # If output is a directory or doesn't have an extension, construct filename
        if output_path.is_dir() or (
            not output_path.suffix and not str(output_path).endswith(("rules", "rules"))
        ):
            filename_template = self.OUTPUT_FILENAMES.get(tool, "{agent_name}.md")
            filename = filename_template.format(agent_name=agent_name)
            output_path = output_path / filename

        return output_path

    def write_output(self, output_path: Path, content: str | dict[str, Any], tool: str) -> None:
        """Write built content to filesystem.

        Args:
            output_path: Path to write to
            content: Content to write (string or dict)
            tool: Tool name (for format-specific handling)

        Raises:
            IOError: If write fails
        """
        try:
            # Create parent directories if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert content to string if needed
            if isinstance(content, dict):
                # Claude builder returns dict, convert to JSON
                content_str = json.dumps(content, indent=2)
            else:
                # content is already a string
                content_str = str(content)

            output_path.write_text(content_str)

            print(f"✓ Built {tool} agent: {output_path}")

        except OSError as e:
            self._error(
                f"Failed to write output file: {e}",
                exit_code=1,
            )

    def run(self, args: list[str] | None = None) -> int:
        """Run the CLI with the given arguments.

        Args:
            args: Command-line arguments (defaults to sys.argv[1:])

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        parser = self.create_parser()

        try:
            parsed_args = parser.parse_args(args)
        except SystemExit as e:
            # argparse calls sys.exit() on error
            exit_code = e.code if isinstance(e.code, int) else 1
            return exit_code

        # Load agent from registry
        agent = self.load_agent(parsed_args.agent)

        # Get builder for tool
        builder = self.get_builder(parsed_args.tool)

        # Build output
        output = self.build_output(builder, agent, parsed_args.tool, parsed_args.variant)

        # Determine output path
        output_path = self.determine_output_path(
            parsed_args.output, parsed_args.tool, parsed_args.agent
        )

        # Write output to filesystem
        self.write_output(output_path, output, parsed_args.tool)

        return 0

    @staticmethod
    def _error(message: str, exit_code: int = 1) -> NoReturn:
        """Print error message and exit.

        Args:
            message: Error message to print
            exit_code: Exit code to use (default: 1)
        """
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(exit_code)


def main(args: list[str] | None = None) -> int:
    """Entry point for the prompt-build CLI.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    cli = PromptBuildCLI()
    return cli.run(args)


if __name__ == "__main__":
    sys.exit(main())
