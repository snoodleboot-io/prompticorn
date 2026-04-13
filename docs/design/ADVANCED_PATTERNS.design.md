# Promptosaurus Advanced Patterns Guide

**Version:** 2.0.0  
**Date:** April 9, 2026  
**Target Audience:** Advanced users implementing custom builders and extensions

---

## Table of Contents

1. [Building Custom Builders](#building-custom-builders)
2. [Extending IR Models](#extending-ir-models)
3. [Plugin Architecture](#plugin-architecture)
4. [Registry Customization](#registry-customization)
5. [Performance Optimization](#performance-optimization)
6. [Production Deployment Patterns](#production-deployment-patterns)
7. [Advanced Error Recovery](#advanced-error-recovery)
8. [Benchmarking and Profiling](#benchmarking-and-profiling)

---

## Building Custom Builders

### Step-by-Step: Create a Builder for Your Tool

#### Step 1: Understand the AbstractBuilder Interface

```python
from abc import ABC, abstractmethod
from src.ir.models import Agent
from src.builders.base import BuildOptions
from typing import Any


class AbstractBuilder(ABC):
    """Base class all builders must implement."""
    
    @abstractmethod
    def build(self, agent: Agent, options: BuildOptions) -> str | dict[str, Any]:
        """Transform Agent IR to tool-specific output."""
        pass
    
    @abstractmethod
    def validate(self, agent: Agent) -> list[str]:
        """Return list of validation errors (empty if valid)."""
        pass
    
    def supports_feature(self, feature_name: str) -> bool:
        """Optional: Check feature support."""
        return feature_name.lower() in {
            "skills", "workflows", "rules", "subagents", "tools"
        }
    
    def get_output_format(self) -> str:
        """Optional: Return output format (e.g., 'JSON', 'YAML')."""
        return "Unknown"
    
    def get_tool_name(self) -> str:
        """Optional: Return tool name."""
        return self.__class__.__name__.replace("Builder", "").lower()
```

#### Step 2: Implement Your Builder

```python
from src.builders.base import AbstractBuilder, BuildOptions
from src.ir.models import Agent
from typing import Any
import json


class SlackBuilder(AbstractBuilder):
    """Builder for Slack bot configuration.
    
    Generates Slack bot manifest and configuration for
    deploying an AI agent as a Slack app.
    """
    
    def build(self, agent: Agent, options: BuildOptions) -> dict[str, Any]:
        """Build Slack bot manifest."""
        manifest = {
            "display_information": {
                "name": agent.name,
                "description": agent.description,
            },
            "features": {
                "bot_user": {
                    "display_name": agent.name,
                    "always_online": True,
                }
            },
            "oauth_config": {
                "scopes": {
                    "bot": self._get_scopes(agent),
                }
            },
            "settings": {
                "interactivity": {
                    "is_enabled": True,
                },
                "slash_commands": self._get_slash_commands(agent),
                "event_subscriptions": {
                    "bot_events": self._get_events(agent),
                }
            },
        }
        
        if options.variant == "verbose":
            manifest["_metadata"] = {
                "agent_name": agent.name,
                "built_at": str(agent),
                "include_tools": options.include_tools,
                "include_skills": options.include_skills,
            }
        
        return manifest
    
    def validate(self, agent: Agent) -> list[str]:
        """Validate agent for Slack requirements."""
        errors = []
        
        if not agent.name:
            errors.append("Agent name is required")
        
        if not agent.description:
            errors.append("Agent description is required")
        
        # Slack names must be alphanumeric and under 80 chars
        if not agent.name.replace("-", "").replace("_", "").isalnum():
            errors.append("Agent name must be alphanumeric (- and _ allowed)")
        
        if len(agent.name) > 80:
            errors.append("Agent name must be under 80 characters")
        
        # Check required scopes
        required_scopes = {"chat:write", "app_mentions:read"}
        if not agent.tools:
            errors.append(f"Agent must have tools defined to enable Slack scopes")
        
        return errors
    
    def get_output_format(self) -> str:
        return "JSON (Slack Manifest)"
    
    def get_tool_name(self) -> str:
        return "slack"
    
    def _get_scopes(self, agent: Agent) -> list[str]:
        """Get Slack OAuth scopes needed by agent."""
        scopes = ["chat:write", "app_mentions:read"]
        
        if agent.tools:
            if "file_upload" in agent.tools:
                scopes.append("files:write")
            if "user_lookup" in agent.tools:
                scopes.append("users:read")
        
        return scopes
    
    def _get_slash_commands(self, agent: Agent) -> list[dict]:
        """Get slash commands for agent."""
        commands = [
            {
                "command": f"/{agent.name}",
                "description": agent.description,
                "should_escape": False,
            }
        ]
        return commands
    
    def _get_events(self, agent: Agent) -> list[str]:
        """Get Slack events to subscribe to."""
        return ["app_mention", "message.im"]


# Register the builder
from src.builders.factory import BuilderFactory
BuilderFactory.register("slack", SlackBuilder)

# Use it
agent = Agent(
    name="support_bot",
    description="Handle customer support requests",
    system_prompt="You are a customer support agent...",
    tools=["file_upload", "user_lookup"]
)

builder = BuilderFactory.get_builder("slack")
manifest = builder.build(agent, BuildOptions(variant="verbose"))
print(json.dumps(manifest, indent=2))
```

#### Step 3: Support Optional Features

```python
from src.builders.base import AbstractBuilder, BuildOptions
from src.ir.models import Agent, Skill, Workflow, Rules
from typing import Any


class EnhancedSlackBuilder(AbstractBuilder):
    """Extended Slack builder with optional feature support."""
    
    def build(self, agent: Agent, options: BuildOptions) -> dict[str, Any]:
        """Build Slack manifest with optional features."""
        manifest = {
            "name": agent.name,
            "description": agent.description,
        }
        
        if options.include_skills and agent.skills:
            manifest["skills"] = self._build_skills(agent.skills)
        
        if options.include_workflows and agent.workflows:
            manifest["workflows"] = self._build_workflows(agent.workflows)
        
        if options.include_tools and agent.tools:
            manifest["tools"] = agent.tools
        
        return manifest
    
    def validate(self, agent: Agent) -> list[str]:
        return []
    
    def _build_skills(self, skills: list[str]) -> dict:
        """Build skills section."""
        return {
            "enabled": True,
            "list": skills,
        }
    
    def _build_workflows(self, workflows: list[str]) -> dict:
        """Build workflows section."""
        return {
            "enabled": True,
            "list": workflows,
        }
```

#### Step 4: Add Comprehensive Testing

```python
import pytest
from src.builders.base import BuildOptions
from src.ir.models import Agent


class TestSlackBuilder:
    """Test suite for SlackBuilder."""
    
    @pytest.fixture
    def builder(self):
        return SlackBuilder()
    
    @pytest.fixture
    def agent(self):
        return Agent(
            name="support_bot",
            description="Customer support agent",
            system_prompt="You are a support agent",
            tools=["file_upload"]
        )
    
    def test_build_returns_valid_manifest(self, builder, agent):
        """Test that builder produces valid Slack manifest."""
        output = builder.build(agent, BuildOptions(variant="minimal"))
        
        assert "display_information" in output
        assert output["display_information"]["name"] == "support_bot"
        assert "features" in output
    
    def test_validate_requires_name(self, builder):
        """Test validation catches missing name."""
        agent = Agent(
            name="",
            description="Test",
            system_prompt="Test"
        )
        errors = builder.validate(agent)
        assert any("name" in e.lower() for e in errors)
    
    def test_validate_requires_description(self, builder):
        """Test validation catches missing description."""
        agent = Agent(
            name="test",
            description="",
            system_prompt="Test"
        )
        errors = builder.validate(agent)
        assert any("description" in e.lower() for e in errors)
    
    def test_build_adds_scopes_for_tools(self, builder, agent):
        """Test that scopes are added based on tools."""
        agent.tools = ["file_upload", "user_lookup"]
        output = builder.build(agent, BuildOptions(variant="minimal"))
        
        scopes = output["oauth_config"]["scopes"]["bot"]
        assert "files:write" in scopes  # Added for file_upload
        assert "users:read" in scopes   # Added for user_lookup
    
    def test_verbose_variant_includes_metadata(self, builder, agent):
        """Test verbose variant adds metadata."""
        output = builder.build(agent, BuildOptions(variant="verbose"))
        
        assert "_metadata" in output
        assert output["_metadata"]["agent_name"] == "support_bot"
    
    def test_invalid_name_format_caught(self, builder):
        """Test validation catches invalid characters."""
        agent = Agent(
            name="bot@#$",  # Invalid characters
            description="Test",
            system_prompt="Test"
        )
        errors = builder.validate(agent)
        assert any("alphanumeric" in e.lower() for e in errors)
```

---

## Extending IR Models

### Creating Model Extensions

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from src.ir.models import Agent


class ExtendedAgent(Agent):
    """Extended Agent model with additional fields."""
    
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorizing agents"
    )
    version: str = Field(
        default="1.0.0",
        description="Semantic version of the agent"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom metadata"
    )
    deprecated: bool = Field(
        default=False,
        description="Whether this agent is deprecated"
    )
    requires_approval: bool = Field(
        default=False,
        description="Whether changes require approval"
    )
    
    class Config:
        frozen = False  # Allow mutations unlike parent


# Create an extended agent
agent = ExtendedAgent(
    name="architect",
    description="Design expert",
    system_prompt="You are an architect",
    tags=["design", "core"],
    version="2.1.0",
    metadata={"team": "platform", "oncall": "alice@example.com"}
)

print(agent.tags)  # ["design", "core"]
print(agent.metadata["team"])  # "platform"
```

### Custom Validators

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List


class ValidatedAgent(BaseModel):
    """Agent with custom validation rules."""
    
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1)
    system_prompt: str = Field(..., min_length=20)
    skills: List[str] = Field(default_factory=list)
    
    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """Ensure name is kebab-case."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Name must be alphanumeric with - or _")
        return v.lower()
    
    @field_validator("skills")
    @classmethod
    def validate_skills_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure no duplicate skills."""
        if len(v) != len(set(v)):
            raise ValueError("Duplicate skills not allowed")
        return v
    
    @model_validator(mode="after")
    def validate_description_not_prompt(self) -> "ValidatedAgent":
        """Ensure description is not same as prompt."""
        if self.description == self.system_prompt:
            raise ValueError("Description and prompt must be different")
        return self


# Valid
agent = ValidatedAgent(
    name="code-agent",
    description="Write code",
    system_prompt="You are an expert programmer..."
)

# Invalid - raises validation error
try:
    bad_agent = ValidatedAgent(
        name="bad@agent",  # Invalid format
        description="Test",
        system_prompt="Test"
    )
except Exception as e:
    print(f"Validation failed: {e}")
```

### Composite Models

```python
from dataclasses import dataclass
from typing import List, Dict
from src.ir.models import Agent, Skill, Workflow


@dataclass
class AgentTeam:
    """Composite model for team of agents."""
    
    team_name: str
    description: str
    agents: Dict[str, Agent]
    shared_skills: List[Skill] = None
    
    def __post_init__(self):
        if self.shared_skills is None:
            self.shared_skills = []
    
    def get_agent(self, name: str) -> Agent:
        """Get agent by name."""
        return self.agents[name]
    
    def add_agent(self, agent: Agent) -> None:
        """Add agent to team."""
        self.agents[agent.name] = agent
    
    def share_skill(self, skill: Skill) -> None:
        """Add skill available to all agents."""
        self.shared_skills.append(skill)
    
    def get_all_skills(self) -> List[str]:
        """Get all skills (shared + individual)."""
        all_skills = {s.name for s in self.shared_skills}
        
        for agent in self.agents.values():
            all_skills.update(agent.skills)
        
        return list(all_skills)


# Create a team
team = AgentTeam(
    team_name="Platform Team",
    description="Core platform agents",
    agents={
        "architect": Agent(
            name="architect",
            description="Design systems",
            system_prompt="You are an architect",
            skills=["data-modeling"]
        ),
        "code": Agent(
            name="code",
            description="Write code",
            system_prompt="You are a developer",
            skills=["implementation"]
        ),
    }
)

# Add shared skill
team.share_skill(Skill(
    name="testing",
    description="Write comprehensive tests",
    instructions="Always write tests..."
))

print(team.get_all_skills())  # All skills across team
```

---

## Plugin Architecture

### Basic Plugin System

```python
from abc import ABC, abstractmethod
from typing import Dict, Type, Any
from src.builders.base import AbstractBuilder


class BuilderPlugin(ABC):
    """Base class for builder plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
    
    @property
    @abstractmethod
    def builder_class(self) -> Type[AbstractBuilder]:
        """Builder class to register."""
        pass
    
    def on_load(self) -> None:
        """Called when plugin is loaded."""
        pass
    
    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata."""
        return {
            "name": self.name,
            "version": "1.0.0",
        }


class PluginRegistry:
    """Registry for managing builder plugins."""
    
    def __init__(self):
        self._plugins: Dict[str, BuilderPlugin] = {}
    
    def register(self, plugin: BuilderPlugin) -> None:
        """Register a plugin."""
        plugin.on_load()
        self._plugins[plugin.name] = plugin
        
        # Register builder with main factory
        from src.builders.factory import BuilderFactory
        BuilderFactory.register(plugin.name, plugin.builder_class)
    
    def unregister(self, name: str) -> None:
        """Unregister a plugin."""
        if name in self._plugins:
            self._plugins[name].on_unload()
            del self._plugins[name]
    
    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """List all registered plugins."""
        return {
            name: plugin.get_metadata()
            for name, plugin in self._plugins.items()
        }


# Example plugin
class SlackBuilderPlugin(BuilderPlugin):
    """Plugin for Slack builder."""
    
    @property
    def name(self) -> str:
        return "slack"
    
    @property
    def builder_class(self) -> Type[AbstractBuilder]:
        from slack_builder import SlackBuilder
        return SlackBuilder
    
    def on_load(self) -> None:
        print("Slack plugin loaded")
    
    def on_unload(self) -> None:
        print("Slack plugin unloaded")
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "slack",
            "version": "2.0.0",
            "author": "Platform Team",
            "supports": ["skills", "workflows", "tools"],
        }


# Usage
registry = PluginRegistry()
slack_plugin = SlackBuilderPlugin()
registry.register(slack_plugin)

print(registry.list_plugins())
```

### Dynamic Plugin Loading

```python
import importlib
from pathlib import Path
from typing import List
from advanced_patterns import BuilderPlugin, PluginRegistry


class DynamicPluginLoader:
    """Load plugins from filesystem."""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.registry = PluginRegistry()
    
    def load_plugins(self) -> List[str]:
        """Load all plugins from plugin directory."""
        loaded = []
        
        if not self.plugin_dir.exists():
            return loaded
        
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
            
            try:
                # Import plugin module
                module_name = plugin_file.stem
                spec = importlib.util.spec_from_file_location(
                    f"plugins.{module_name}",
                    plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find plugin class
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BuilderPlugin) and 
                        attr is not BuilderPlugin):
                        
                        plugin = attr()
                        self.registry.register(plugin)
                        loaded.append(plugin.name)
            
            except Exception as e:
                print(f"Failed to load plugin {plugin_file}: {e}")
        
        return loaded
    
    def get_registry(self) -> PluginRegistry:
        """Get plugin registry."""
        return self.registry


# Example: Directory structure
# plugins/
#   slack_plugin.py
#   discord_plugin.py
#   teams_plugin.py

# Usage
loader = DynamicPluginLoader("plugins")
loaded_plugins = loader.load_plugins()
print(f"Loaded plugins: {loaded_plugins}")

registry = loader.get_registry()
print(registry.list_plugins())
```

---

## Registry Customization

### Custom Agent Registry

```python
from typing import Dict, List, Optional
from src.ir.models import Agent
from pathlib import Path
import json


class CustomAgentRegistry:
    """Custom registry with versioning and metadata."""
    
    def __init__(self, storage_dir: str = "agents"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self._cache: Dict[str, Agent] = {}
    
    def register(self, agent: Agent, metadata: Dict = None) -> None:
        """Register an agent with metadata."""
        self._cache[agent.name] = agent
        
        # Save to disk
        agent_dir = self.storage_dir / agent.name
        agent_dir.mkdir(exist_ok=True)
        
        # Save agent
        with open(agent_dir / "agent.json", "w") as f:
            json.dump(agent.model_dump(), f, indent=2)
        
        # Save metadata
        if metadata:
            with open(agent_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
    
    def get(self, name: str) -> Optional[Agent]:
        """Get agent from cache or disk."""
        # Check cache
        if name in self._cache:
            return self._cache[name]
        
        # Load from disk
        agent_file = self.storage_dir / name / "agent.json"
        if agent_file.exists():
            with open(agent_file) as f:
                data = json.load(f)
            agent = Agent(**data)
            self._cache[name] = agent
            return agent
        
        return None
    
    def list(self) -> List[str]:
        """List all registered agents."""
        return list(set(
            list(self._cache.keys()) +
            [d.name for d in self.storage_dir.iterdir() if d.is_dir()]
        ))
    
    def get_metadata(self, name: str) -> Optional[Dict]:
        """Get agent metadata."""
        metadata_file = self.storage_dir / name / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)
        return None
    
    def delete(self, name: str) -> None:
        """Delete an agent."""
        if name in self._cache:
            del self._cache[name]
        
        agent_dir = self.storage_dir / name
        if agent_dir.exists():
            import shutil
            shutil.rmtree(agent_dir)


# Usage
registry = CustomAgentRegistry()

agent = Agent(
    name="architect",
    description="Design expert",
    system_prompt="You are an architect"
)

registry.register(agent, metadata={
    "author": "Alice",
    "team": "Platform",
    "created_at": "2026-04-09",
    "approval_status": "approved"
})

# Later...
loaded_agent = registry.get("architect")
print(registry.list())
print(registry.get_metadata("architect"))
```

---

## Performance Optimization

### Lazy Loading and Caching

```python
from functools import cached_property
from typing import Dict
from src.ir.models import Agent
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions


class CachedBuilderSession:
    """Session that caches build results."""
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self._build_cache: Dict[tuple, str | dict] = {}
    
    @cached_property
    def all_builders(self) -> list[str]:
        """Lazily load all builders."""
        return BuilderFactory.list_builders()
    
    def build(self, tool: str, variant: str = "minimal") -> str | dict:
        """Build with caching."""
        cache_key = (tool, variant)
        
        if cache_key in self._build_cache:
            return self._build_cache[cache_key]
        
        builder = BuilderFactory.get_builder(tool)
        options = BuildOptions(variant=variant, agent_name=self.agent.name)
        result = builder.build(self.agent, options)
        
        self._build_cache[cache_key] = result
        return result
    
    def clear_cache(self) -> None:
        """Clear build cache."""
        self._build_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "cached_builds": len(self._build_cache),
            "agent_name": self.agent.name,
        }


# Usage
session = CachedBuilderSession(agent)

# First build - slow
result1 = session.build("kilo", "minimal")

# Second build - from cache
result2 = session.build("kilo", "minimal")

print(session.get_cache_stats())
```

### Parallel Building

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.ir.models import Agent
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions


async def build_for_all_tools_async(
    agent: Agent,
    variant: str = "minimal"
) -> Dict[str, str | dict]:
    """Build for all tools in parallel."""
    tools = BuilderFactory.list_builders()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                _build_single_tool,
                agent,
                tool,
                variant
            )
            for tool in tools
        ]
        
        results = await asyncio.gather(*tasks)
        return {tool: result for tool, result in zip(tools, results)}


def _build_single_tool(agent: Agent, tool: str, variant: str) -> str | dict:
    """Build for a single tool."""
    builder = BuilderFactory.get_builder(tool)
    options = BuildOptions(variant=variant, agent_name=agent.name)
    return builder.build(agent, options)


# Usage
# results = asyncio.run(build_for_all_tools_async(agent))
```

---

## Production Deployment Patterns

### Configuration Management

```python
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class BuilderConfig:
    """Builder configuration for production."""
    
    # Caching
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    
    # Validation
    strict_validation: bool = True
    
    # Error handling
    fail_fast: bool = False  # Continue on error
    
    # Performance
    max_parallel_builds: int = 5
    
    # Logging
    log_builds: bool = True
    
    @classmethod
    def from_env(cls) -> "BuilderConfig":
        """Load config from environment variables."""
        return cls(
            enable_caching=os.getenv("BUILDER_CACHE", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("BUILDER_CACHE_TTL", "3600")),
            strict_validation=os.getenv("BUILDER_STRICT", "true").lower() == "true",
            fail_fast=os.getenv("BUILDER_FAIL_FAST", "false").lower() == "true",
            max_parallel_builds=int(os.getenv("BUILDER_PARALLEL", "5")),
            log_builds=os.getenv("BUILDER_LOG", "true").lower() == "true",
        )


# Usage in production
config = BuilderConfig.from_env()
print(f"Cache enabled: {config.enable_caching}")
print(f"Parallel builds: {config.max_parallel_builds}")
```

### Health Checks

```python
from dataclasses import dataclass
from src.builders.factory import BuilderFactory
from src.ir.models import Agent


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    healthy: bool
    builders_available: list[str]
    failed_builders: list[str]
    messages: list[str]


def check_builder_health() -> HealthCheckResult:
    """Check health of builder system."""
    messages = []
    failed = []
    
    try:
        available = BuilderFactory.list_builders()
        
        if not available:
            messages.append("No builders registered")
            return HealthCheckResult(
                healthy=False,
                builders_available=[],
                failed_builders=[],
                messages=messages
            )
        
        # Test each builder
        test_agent = Agent(
            name="health-check",
            description="Test",
            system_prompt="Test"
        )
        
        for tool in available:
            try:
                builder = BuilderFactory.get_builder(tool)
                errors = builder.validate(test_agent)
                if errors:
                    messages.append(f"{tool}: validation issues")
            except Exception as e:
                failed.append(tool)
                messages.append(f"{tool}: {str(e)}")
        
        healthy = len(failed) == 0
        return HealthCheckResult(
            healthy=healthy,
            builders_available=available,
            failed_builders=failed,
            messages=messages
        )
    
    except Exception as e:
        return HealthCheckResult(
            healthy=False,
            builders_available=[],
            failed_builders=[],
            messages=[f"Health check failed: {str(e)}"]
        )


# Usage
health = check_builder_health()
if health.healthy:
    print("✓ All builders operational")
else:
    print(f"✗ Issues detected: {health.messages}")
```

---

## Advanced Error Recovery

### Circuit Breaker Pattern

```python
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any
from src.builders.errors import BuilderException


class CircuitState(Enum):
    """States of a circuit breaker."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failed, rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """Circuit breaker for builder failures."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time: datetime = None
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self.state = CircuitState.HALF_OPEN
            else:
                raise BuilderException("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self) -> None:
        """Reset after successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self) -> None:
        """Handle failure."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_recovery(self) -> bool:
        """Check if recovery timeout has elapsed."""
        if not self.last_failure_time:
            return False
        
        elapsed = datetime.now() - self.last_failure_time
        return elapsed > timedelta(seconds=self.recovery_timeout)


# Usage
breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

for i in range(10):
    try:
        result = breaker.call(some_build_function, agent, tool)
    except BuilderException as e:
        print(f"Build failed: {e}")
        # Handle failure gracefully
```

---

## Benchmarking and Profiling

### Performance Benchmarking

```python
import time
from typing import Dict, List
from src.ir.models import Agent
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions


class BuilderBenchmark:
    """Benchmark builder performance."""
    
    def __init__(self):
        self.results: Dict[str, List[float]] = {}
    
    def benchmark_tool(
        self,
        agent: Agent,
        tool: str,
        iterations: int = 10
    ) -> Dict[str, float]:
        """Benchmark building with a specific tool."""
        times = []
        
        builder = BuilderFactory.get_builder(tool)
        options = BuildOptions(variant="minimal")
        
        for _ in range(iterations):
            start = time.perf_counter()
            builder.build(agent, options)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        self.results[tool] = times
        
        return {
            "tool": tool,
            "iterations": iterations,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
            "avg_ms": sum(times) / len(times) * 1000,
            "total_ms": sum(times) * 1000,
        }
    
    def benchmark_all(
        self,
        agent: Agent,
        iterations: int = 10
    ) -> Dict[str, Dict]:
        """Benchmark all tools."""
        results = {}
        
        for tool in BuilderFactory.list_builders():
            results[tool] = self.benchmark_tool(agent, tool, iterations)
        
        return results
    
    def print_report(self) -> None:
        """Print benchmark report."""
        print("\n" + "=" * 70)
        print("BUILDER PERFORMANCE BENCHMARK")
        print("=" * 70)
        
        for tool, times in self.results.items():
            avg_ms = sum(times) / len(times) * 1000
            print(f"{tool:15} {avg_ms:8.3f}ms (n={len(times)})")


# Usage
benchmark = BuilderBenchmark()
results = benchmark.benchmark_all(agent, iterations=100)
benchmark.print_report()
```

---

## Next Steps

- See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for practical integration patterns
- See [BUILDER_API_REFERENCE.md](./BUILDER_API_REFERENCE.md) for complete API documentation
- See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for migrating existing configurations

---

*This guide covers advanced patterns for extending and customizing Promptosaurus. For standard usage, see the Integration Guide.*
