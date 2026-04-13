# Promptosaurus Integration Guide

**Version:** 2.0.0  
**Date:** April 9, 2026  
**Target Audience:** Developers integrating Promptosaurus IR models into existing projects

---

## Table of Contents

1. [Overview](#overview)
2. [Integration Patterns](#integration-patterns)
3. [Using IR Models in Your Code](#using-ir-models-in-your-code)
4. [Dependency Injection](#dependency-injection)
5. [Error Handling Strategies](#error-handling-strategies)
6. [Testing Custom Builders](#testing-custom-builders)
7. [Performance Optimization](#performance-optimization)
8. [Real-World Integration Examples](#real-world-integration-examples)
9. [Troubleshooting](#troubleshooting)

---

## Overview

Promptosaurus provides a **tool-agnostic Intermediate Representation (IR)** system that you can integrate into your existing projects. This guide shows you how to:

- Use IR models as a foundation for your own applications
- Build custom builders for new tools or platforms
- Create dependency injection patterns for flexibility
- Handle errors gracefully in production systems
- Test your custom implementations thoroughly

### What You'll Need

- **Python 3.11+** (for IR models and builders)
- **Basic understanding** of the Pydantic library
- **Familiarity** with builder pattern and dependency injection

---

## Integration Patterns

### Pattern 1: Direct IR Usage (Simplest)

The simplest approach is to directly use IR models in your code:

```python
from src.ir.models import Agent, Skill, Workflow
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions

# Create an agent directly
agent = Agent(
    name="my_agent",
    description="My custom agent",
    system_prompt="You are an expert in...",
    skills=["analysis", "design"],
    tools=["code_editor", "terminal"]
)

# Build for a specific tool
kilo_builder = BuilderFactory.get_builder("kilo")
output = kilo_builder.build(agent, BuildOptions(variant="minimal"))
print(output)
```

**Pros:**
- Simple and straightforward
- No boilerplate code
- Easy to understand

**Cons:**
- Tightly coupled to Pydantic models
- Hard to mock for testing
- Difficult to swap implementations

---

### Pattern 2: Custom Builder Pattern (Recommended)

Create your own builder for your specific tool:

```python
from src.builders.base import AbstractBuilder, BuildOptions
from src.ir.models import Agent
from typing import Any

class MyCustomToolBuilder(AbstractBuilder):
    """Builder for your custom tool."""
    
    def build(self, agent: Agent, options: BuildOptions) -> dict[str, Any]:
        """Build configuration for your tool."""
        config = {
            "id": agent.name,
            "label": agent.description,
            "system_instructions": agent.system_prompt,
            "capabilities": [],
        }
        
        if options.include_tools and agent.tools:
            config["capabilities"].extend(agent.tools)
        
        if options.include_skills and agent.skills:
            config["capabilities"].extend(agent.skills)
        
        return config
    
    def validate(self, agent: Agent) -> list[str]:
        """Validate agent for your tool."""
        errors = []
        
        if not agent.name or len(agent.name) > 50:
            errors.append("Agent name must be 1-50 characters")
        
        if not agent.system_prompt or len(agent.system_prompt) < 20:
            errors.append("System prompt must be at least 20 characters")
        
        return errors
    
    def get_output_format(self) -> str:
        return "JSON"
    
    def get_tool_name(self) -> str:
        return "my_custom_tool"


# Register your builder
from src.builders.factory import BuilderFactory
BuilderFactory.register("my_tool", MyCustomToolBuilder)

# Use it like any other builder
builder = BuilderFactory.get_builder("my_tool")
output = builder.build(agent, BuildOptions(variant="verbose"))
```

**Pros:**
- Extensible and maintainable
- Reusable across projects
- Follows established patterns

**Cons:**
- More code to write initially
- Requires understanding of AbstractBuilder

---

### Pattern 3: Protocol-Based Feature Support

Support optional features using Python protocols:

```python
from typing import Protocol, List
from src.ir.models import Skill, Workflow, Rules
from src.builders.base import AbstractBuilder, BuildOptions
from src.ir.models import Agent

class SupportsSkills(Protocol):
    """Protocol for builders that support skills."""
    
    def build_skills(self, skills: List[Skill]) -> str:
        """Build skill-specific output."""
        ...


class SupportsWorkflows(Protocol):
    """Protocol for builders that support workflows."""
    
    def build_workflows(self, workflows: List[Workflow]) -> str:
        """Build workflow-specific output."""
        ...


class FeatureAwareBuilder(AbstractBuilder):
    """Builder that checks feature support at runtime."""
    
    def build(self, agent: Agent, options: BuildOptions) -> str:
        output = f"Agent: {agent.name}\n"
        
        if options.include_skills and hasattr(self, "build_skills"):
            skills_output = self.build_skills(agent.skills)  # type: ignore
            output += f"\n{skills_output}"
        
        if options.include_workflows and hasattr(self, "build_workflows"):
            workflows_output = self.build_workflows(agent.workflows)  # type: ignore
            output += f"\n{workflows_output}"
        
        return output
    
    def validate(self, agent: Agent) -> list[str]:
        return []
```

---

## Using IR Models in Your Code

### Loading Agents from Files

```python
import json
from pathlib import Path
from src.ir.models import Agent

# Load from JSON
def load_agent_from_json(filepath: str) -> Agent:
    """Load an agent from a JSON file."""
    with open(filepath) as f:
        data = json.load(f)
    return Agent(**data)


# Load from YAML
import yaml

def load_agent_from_yaml(filepath: str) -> Agent:
    """Load an agent from a YAML file."""
    with open(filepath) as f:
        data = yaml.safe_load(f)
    return Agent(**data)


# Example usage
architect = load_agent_from_json("agents/architect/config.json")
code_agent = load_agent_from_yaml("agents/code/config.yaml")
```

### Validating Agents

```python
from pydantic import ValidationError
from src.ir.models import Agent

try:
    agent = Agent(
        name="",  # Invalid: empty name
        description="Test agent",
        system_prompt="Test prompt"
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
    for error in e.errors():
        print(f"  - {error['loc'][0]}: {error['msg']}")
```

### Creating Agent Collections

```python
from dataclasses import dataclass
from typing import Dict
from src.ir.models import Agent

@dataclass
class AgentRegistry:
    """Registry for managing multiple agents."""
    agents: Dict[str, Agent]
    
    def get(self, name: str) -> Agent:
        """Get agent by name."""
        if name not in self.agents:
            raise ValueError(f"Agent not found: {name}")
        return self.agents[name]
    
    def list(self) -> list[str]:
        """List all registered agent names."""
        return list(self.agents.keys())
    
    def register(self, agent: Agent) -> None:
        """Register a new agent."""
        self.agents[agent.name] = agent
    
    def export_all(self, format: str = "json") -> Dict:
        """Export all agents."""
        if format == "json":
            return {
                name: agent.model_dump()
                for name, agent in self.agents.items()
            }
        raise ValueError(f"Unsupported format: {format}")


# Usage
registry = AgentRegistry(agents={})
registry.register(Agent(
    name="architect",
    description="Design systems",
    system_prompt="You are an architect..."
))
registry.register(Agent(
    name="code",
    description="Implement features",
    system_prompt="You are a developer..."
))

print(registry.list())  # ["architect", "code"]
print(registry.get("architect").description)  # "Design systems"
```

---

## Dependency Injection

### Basic Dependency Injection

Inject the builder factory to make your code testable:

```python
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions
from src.ir.models import Agent
from typing import Protocol

class Builder(Protocol):
    """Protocol for any builder."""
    def build(self, agent: Agent, options: BuildOptions) -> str | dict:
        ...


class AgentService:
    """Service that uses a builder."""
    
    def __init__(self, builder_factory = None):
        """Initialize with optional factory injection."""
        self.factory = builder_factory or BuilderFactory
    
    def build_agent(self, agent: Agent, tool: str) -> str | dict:
        """Build agent for a specific tool."""
        builder = self.factory.get_builder(tool)
        options = BuildOptions(variant="minimal", agent_name=agent.name)
        return builder.build(agent, options)


# Production usage
service = AgentService()  # Uses real factory
output = service.build_agent(agent, "kilo")

# Testing usage
class MockFactory:
    def get_builder(self, tool: str):
        # Return mock builder
        pass

test_service = AgentService(builder_factory=MockFactory())
```

### Advanced Dependency Injection with Dataclasses

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod
from src.builders.base import AbstractBuilder, BuildOptions
from src.ir.models import Agent

class BuilderProvider(ABC):
    """Abstract provider for builders."""
    
    @abstractmethod
    def get_builder(self, tool: str) -> AbstractBuilder:
        pass


class DefaultBuilderProvider(BuilderProvider):
    """Default provider using the factory."""
    
    def get_builder(self, tool: str) -> AbstractBuilder:
        from src.builders.factory import BuilderFactory
        return BuilderFactory.get_builder(tool)


@dataclass
class AgentBuildContext:
    """Context for building agents."""
    builder_provider: BuilderProvider
    variant: str = "minimal"
    
    def build(self, agent: Agent, tool: str) -> str | dict:
        """Build agent using injected provider."""
        builder = self.builder_provider.get_builder(tool)
        options = BuildOptions(variant=self.variant, agent_name=agent.name)
        return builder.build(agent, options)


# Usage
from src.builders.factory import BuilderFactory
provider = DefaultBuilderProvider()
context = AgentBuildContext(builder_provider=provider, variant="verbose")
output = context.build(agent, "claude")
```

---

## Error Handling Strategies

### Strategy 1: Validation Before Build

```python
from src.builders.errors import BuilderValidationError
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions
from src.ir.models import Agent

def safe_build(agent: Agent, tool: str) -> str | dict | None:
    """Build agent with validation."""
    try:
        builder = BuilderFactory.get_builder(tool)
        
        # Validate first
        errors = builder.validate(agent)
        if errors:
            raise BuilderValidationError(errors)
        
        # Build if valid
        options = BuildOptions(variant="minimal")
        return builder.build(agent, options)
    
    except BuilderValidationError as e:
        print(f"Validation failed: {e}")
        return None
    except Exception as e:
        print(f"Build failed: {e}")
        return None
```

### Strategy 2: Error Recovery

```python
from src.builders.errors import (
    BuilderNotFoundError,
    BuilderValidationError,
    UnsupportedFeatureError
)
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions
from src.ir.models import Agent

def build_with_fallback(agent: Agent, tool: str, fallback_tool: str = "kilo"):
    """Build with fallback to another tool."""
    try:
        builder = BuilderFactory.get_builder(tool)
    except BuilderNotFoundError:
        print(f"Builder not found for {tool}, using {fallback_tool}")
        builder = BuilderFactory.get_builder(fallback_tool)
    
    try:
        options = BuildOptions(variant="minimal")
        return builder.build(agent, options)
    except BuilderValidationError as e:
        print(f"Validation failed: {e}")
        # Could strip problematic components
        agent.skills = []
        agent.workflows = []
        return builder.build(agent, options)
```

### Strategy 3: Structured Error Responses

```python
from dataclasses import dataclass
from typing import Optional
from src.ir.models import Agent
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions

@dataclass
class BuildResult:
    """Result of a build operation."""
    success: bool
    output: Optional[str | dict] = None
    error: Optional[str] = None
    warnings: list[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


def build_agent(agent: Agent, tool: str) -> BuildResult:
    """Build with structured error handling."""
    try:
        builder = BuilderFactory.get_builder(tool)
        
        errors = builder.validate(agent)
        if errors:
            return BuildResult(
                success=False,
                error=f"Validation failed: {'; '.join(errors)}"
            )
        
        output = builder.build(agent, BuildOptions(variant="minimal"))
        return BuildResult(success=True, output=output)
    
    except Exception as e:
        return BuildResult(
            success=False,
            error=str(e)
        )


# Usage
result = build_agent(agent, "kilo")
if result.success:
    print("Build succeeded")
    print(result.output)
else:
    print(f"Build failed: {result.error}")
```

---

## Testing Custom Builders

### Unit Testing a Custom Builder

```python
import pytest
from src.builders.base import AbstractBuilder, BuildOptions
from src.ir.models import Agent


class MyBuilder(AbstractBuilder):
    def build(self, agent: Agent, options: BuildOptions) -> str:
        return f"# {agent.name}\n{agent.system_prompt}"
    
    def validate(self, agent: Agent) -> list[str]:
        errors = []
        if not agent.name:
            errors.append("Name required")
        if len(agent.system_prompt) < 10:
            errors.append("Prompt too short")
        return errors


class TestMyBuilder:
    """Test suite for MyBuilder."""
    
    @pytest.fixture
    def builder(self):
        return MyBuilder()
    
    @pytest.fixture
    def agent(self):
        return Agent(
            name="test_agent",
            description="Test",
            system_prompt="This is a test system prompt"
        )
    
    def test_build_success(self, builder, agent):
        """Test successful build."""
        options = BuildOptions(variant="minimal")
        output = builder.build(agent, options)
        
        assert "test_agent" in output
        assert "This is a test system prompt" in output
    
    def test_validate_success(self, builder, agent):
        """Test validation passes."""
        errors = builder.validate(agent)
        assert errors == []
    
    def test_validate_empty_name(self, builder):
        """Test validation fails with empty name."""
        agent = Agent(
            name="",  # Invalid
            description="Test",
            system_prompt="This is a test system prompt"
        )
        errors = builder.validate(agent)
        assert "Name required" in errors
    
    def test_validate_short_prompt(self, builder):
        """Test validation fails with short prompt."""
        agent = Agent(
            name="test",
            description="Test",
            system_prompt="Too short"  # Only 9 chars
        )
        errors = builder.validate(agent)
        assert "Prompt too short" in errors
    
    def test_build_with_options(self, builder, agent):
        """Test build respects options."""
        options = BuildOptions(
            variant="verbose",
            include_skills=True,
            include_tools=True
        )
        output = builder.build(agent, options)
        assert output is not None
```

### Integration Testing

```python
import pytest
from src.builders.factory import BuilderFactory
from src.ir.models import Agent
from src.builders.base import BuildOptions


class TestBuilderIntegration:
    """Test integration with BuilderFactory."""
    
    def test_factory_builds_agent(self):
        """Test that factory-created builder can build."""
        agent = Agent(
            name="test",
            description="Test agent",
            system_prompt="You are a test agent"
        )
        
        builder = BuilderFactory.get_builder("kilo")
        options = BuildOptions(variant="minimal")
        output = builder.build(agent, options)
        
        assert output is not None
        assert isinstance(output, str)
    
    def test_all_builders_registered(self):
        """Test all expected builders are registered."""
        expected_tools = ["kilo", "claude", "cline", "cursor", "copilot"]
        available = BuilderFactory.list_builders()
        
        for tool in expected_tools:
            assert tool in available


@pytest.mark.integration
def test_roundtrip_build():
    """Test building and parsing output."""
    agent = Agent(
        name="architect",
        description="Design expert",
        system_prompt="You are an architect",
        skills=["design", "analysis"]
    )
    
    # Build for multiple tools
    for tool in ["kilo", "claude"]:
        builder = BuilderFactory.get_builder(tool)
        output = builder.build(agent, BuildOptions(variant="minimal"))
        
        # Verify output is not empty
        assert output
        assert agent.name in str(output)
```

---

## Performance Optimization

### Caching Build Results

```python
from functools import lru_cache
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions
from src.ir.models import Agent


@lru_cache(maxsize=128)
def cached_build(agent_name: str, tool: str, variant: str) -> str:
    """Build with caching."""
    # Note: This is a simplified example
    # In real code, you'd need to serialize the Agent
    builder = BuilderFactory.get_builder(tool)
    # ... load agent from cache key ...
    options = BuildOptions(variant=variant)
    return builder.build(agent, options)  # type: ignore
```

### Batch Building

```python
from concurrent.futures import ThreadPoolExecutor
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions
from src.ir.models import Agent


def build_for_all_tools(agent: Agent, variant: str = "minimal") -> dict[str, str | dict]:
    """Build agent for all registered tools efficiently."""
    results = {}
    tools = BuilderFactory.list_builders()
    
    # Build sequentially (builders are lightweight)
    for tool in tools:
        builder = BuilderFactory.get_builder(tool)
        options = BuildOptions(variant=variant, agent_name=agent.name)
        results[tool] = builder.build(agent, options)
    
    return results


# For larger batches, use threading if needed
def build_multiple_agents(agents: list[Agent], tools: list[str]) -> dict:
    """Build multiple agents for multiple tools."""
    results = {}
    
    for agent in agents:
        results[agent.name] = {}
        for tool in tools:
            builder = BuilderFactory.get_builder(tool)
            options = BuildOptions(variant="minimal", agent_name=agent.name)
            results[agent.name][tool] = builder.build(agent, options)
    
    return results
```

---

## Real-World Integration Examples

### Example 1: Web Service Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.ir.models import Agent
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions
from src.builders.errors import BuilderNotFoundError, BuilderValidationError

app = FastAPI()


class AgentBuildRequest(BaseModel):
    """Request to build an agent."""
    agent: Agent
    tool: str
    variant: str = "minimal"


class AgentBuildResponse(BaseModel):
    """Response with built agent."""
    success: bool
    output: str | dict | None = None
    error: str | None = None


@app.post("/build-agent", response_model=AgentBuildResponse)
async def build_agent(request: AgentBuildRequest):
    """Build an agent for a specific tool."""
    try:
        builder = BuilderFactory.get_builder(request.tool)
        
        errors = builder.validate(request.agent)
        if errors:
            raise BuilderValidationError(errors)
        
        options = BuildOptions(
            variant=request.variant,
            agent_name=request.agent.name
        )
        output = builder.build(request.agent, options)
        
        return AgentBuildResponse(success=True, output=output)
    
    except BuilderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BuilderValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Example 2: CLI Tool Integration

```python
import click
from src.ir.models import Agent
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions
from src.builders.errors import BuilderException


@click.group()
def cli():
    """Promptosaurus CLI."""
    pass


@cli.command()
@click.option("--agent", required=True, help="Agent name")
@click.option("--tool", required=True, help="Target tool")
@click.option("--variant", default="minimal", help="Build variant")
@click.option("--output", type=click.File("w"), help="Output file")
def build(agent: str, tool: str, variant: str, output):
    """Build an agent for a specific tool."""
    try:
        # Load agent
        import json
        with open(f"agents/{agent}/config.json") as f:
            agent_data = json.load(f)
        
        agent_obj = Agent(**agent_data)
        
        # Build
        builder = BuilderFactory.get_builder(tool)
        options = BuildOptions(variant=variant, agent_name=agent_obj.name)
        result = builder.build(agent_obj, options)
        
        # Output
        if output:
            if isinstance(result, dict):
                json.dump(result, output)
            else:
                output.write(result)
        else:
            click.echo(result)
    
    except BuilderException as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
```

### Example 3: Configuration Management

```python
from pathlib import Path
import json
import yaml
from src.ir.models import Agent
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions


class AgentConfigManager:
    """Manage agent configurations."""
    
    def __init__(self, agents_dir: str = "agents"):
        self.agents_dir = Path(agents_dir)
    
    def load_agent(self, name: str) -> Agent:
        """Load agent from file."""
        # Try JSON first
        json_path = self.agents_dir / name / "config.json"
        if json_path.exists():
            with open(json_path) as f:
                return Agent(**json.load(f))
        
        # Try YAML
        yaml_path = self.agents_dir / name / "config.yaml"
        if yaml_path.exists():
            with open(yaml_path) as f:
                return Agent(**yaml.safe_load(f))
        
        raise FileNotFoundError(f"Agent config not found: {name}")
    
    def save_agent(self, agent: Agent, format: str = "json"):
        """Save agent to file."""
        agent_dir = self.agents_dir / agent.name
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            path = agent_dir / "config.json"
            with open(path, "w") as f:
                json.dump(agent.model_dump(), f, indent=2)
        elif format == "yaml":
            path = agent_dir / "config.yaml"
            with open(path, "w") as f:
                yaml.dump(agent.model_dump(), f)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def build_all(self, variant: str = "minimal") -> dict:
        """Build all agents for all tools."""
        agents = {}
        tools = BuilderFactory.list_builders()
        
        for agent_dir in self.agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            
            agent = self.load_agent(agent_dir.name)
            agents[agent.name] = {}
            
            for tool in tools:
                builder = BuilderFactory.get_builder(tool)
                options = BuildOptions(variant=variant, agent_name=agent.name)
                agents[agent.name][tool] = builder.build(agent, options)
        
        return agents
```

---

## Troubleshooting

### Issue: ImportError for IR Models

**Error:**
```
ImportError: cannot import name 'Agent' from 'src.ir.models'
```

**Solution:**
```bash
# Make sure src is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or add to sys.path in code
import sys
sys.path.insert(0, '/path/to/promptosaurus')

from src.ir.models import Agent
```

### Issue: Builder Not Found

**Error:**
```
BuilderNotFoundError: No builder registered for tool: 'my_tool'
```

**Solution:**
```python
# Register your builder before using
from src.builders.factory import BuilderFactory
from my_builders import MyCustomBuilder

BuilderFactory.register("my_tool", MyCustomBuilder)

# Now it works
builder = BuilderFactory.get_builder("my_tool")
```

### Issue: Validation Errors During Build

**Error:**
```
BuilderValidationError: Agent IR model validation failed:
  - Agent name is required
  - System prompt must be at least 20 characters
```

**Solution:**
```python
# Check validation before building
builder = BuilderFactory.get_builder("kilo")
errors = builder.validate(agent)

if errors:
    for error in errors:
        print(f"Fix: {error}")
    # Fix agent before building
    agent.system_prompt = "I am a helpful AI assistant that..."
    errors = builder.validate(agent)  # Should be empty now
```

### Issue: Memory Issues with Large Batches

**Error:**
```
MemoryError: Unable to build 1000 agents at once
```

**Solution:**
```python
# Build in smaller batches
def build_in_batches(agents: list[Agent], batch_size: int = 100):
    """Build agents in smaller batches."""
    results = {}
    
    for i in range(0, len(agents), batch_size):
        batch = agents[i:i+batch_size]
        
        for agent in batch:
            builder = BuilderFactory.get_builder("kilo")
            output = builder.build(agent, BuildOptions(variant="minimal"))
            results[agent.name] = output
        
        # Optional: save batch results to disk to free memory
        # save_batch_results(results, batch_num)
    
    return results
```

---

## Next Steps

- See [ADVANCED_PATTERNS.md](./ADVANCED_PATTERNS.md) for building custom builders
- See [BUILDER_API_REFERENCE.md](./BUILDER_API_REFERENCE.md) for complete API documentation
- See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for migrating existing configurations

---

*This guide covers practical integration patterns for Promptosaurus. For questions or issues, refer to the troubleshooting section or consult the main documentation.*
