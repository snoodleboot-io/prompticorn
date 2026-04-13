# Intermediate Representation (IR) System

## Overview

The Intermediate Representation (IR) system is the core data modeling layer of Promptosaurus. It provides tool-agnostic data models that represent all components of the prompt architecture system, enabling builders to transform these models into tool-specific outputs.

## Core Models

### Agent Model
**File:** `promptosaurus/ir/models/agent.py`

The Agent model represents a complete AI entity with its configuration, capabilities (tools and skills), and behavioral patterns (workflows). Agents can contain subagents for hierarchical composition.

**Key Attributes:**
- `name`: Unique identifier for the agent (e.g., 'code', 'architect')
- `description`: One-sentence description of the agent's purpose
- `mode`: Agent mode - 'primary' (user-selectable), 'subagent' (delegable only), or 'all' (both)
- `system_prompt`: The system prompt that defines the agent's behavior
- `tools`: List of tool names this agent can use
- `skills`: List of skill names this agent can perform
- `workflows`: List of workflow names this agent can execute
- `subagents`: List of subagent names for hierarchical composition
- `permissions`: Permission rules for the agent (tool-specific)

**Example Usage:**
```python
from promptosaurus.ir.models import Agent

agent = Agent(
    name="code",
    description="Write and review code",
    mode="primary",
    system_prompt="You are an expert programmer...",
    tools=["read", "write", "bash"],
    skills=["implementation", "debugging"],
    workflows=["feature-development", "bug-fixing"],
    subagents=["code-feature", "code-refactor"]
)
```

### Workflow Model
**File:** `promptosaurus/ir/models/workflow.py`

Workflows define a series of steps that an agent can execute in a defined order. Each step is a string describing an action.

**Key Attributes:**
- `name`: Unique identifier for the workflow
- `description`: One-sentence description of the workflow's purpose
- `steps`: List of step descriptions (must be non-empty)

**Example Usage:**
```python
from promptosaurus.ir.models import Workflow

workflow = Workflow(
    name="feature-development",
    description="Develop a new feature from start to finish",
    steps=[
        "Understand requirements",
        "Design solution",
        "Implement code",
        "Write tests",
        "Review code",
        "Deploy to staging"
    ]
)
```

### Skill Model
**File:** `promptosaurus/ir/models/skill.py`

Skills encapsulate specialized knowledge domains that agents leverage for domain-specific expertise.

**Key Attributes:**
- `name`: Unique identifier for the skill
- `description`: One-sentence description of the skill's purpose
- `instructions`: Detailed instructions for applying the skill
- `parameters`: Configuration parameters for the skill

### Tool Model
**File:** `promptosaurus/ir/models/tool.py`

Tools describe available tool integrations that agents can use to interact with external systems.

**Key Attributes:**
- `name`: Unique identifier for the tool
- `description`: One-sentence description of the tool's purpose
- `parameters`: Configuration parameters for the tool
- `permissions`: Permission rules for tool usage

### Rules Model
**File:** `promptosaurus/ir/models/rules.py`

Rules configure behavioral constraints and guidelines that govern agent behavior.

**Key Attributes:**
- `name`: Unique identifier for the rules set
- `description`: One-sentence description of the rules' purpose
- `content`: The actual rules content
- `priority`: Priority level for rule application

### Project Model
**File:** `promptosaurus/ir/models/project.py`

Project manages project-level configuration and metadata.

**Key Attributes:**
- `name`: Project name
- `description`: Project description
- `version`: Project version
- `author`: Project author
- `license`: Project license
- `dependencies`: Project dependencies
- `scripts`: Project scripts

## Data Validation

All IR models use Pydantic for automatic validation and type checking. Validation includes:

1. **Field Validation:** Ensures required fields are present and have correct types
2. **Constraint Validation:** Enforces min/max lengths, patterns, and ranges
3. **Custom Validation:** Allows custom validator functions for complex logic
4. **Immutability:** Models are frozen by default to prevent accidental modification

**Example Validation:**
```python
from promptosaurus.ir.models import Agent

# This will raise a validation error due to empty name
try:
    agent = Agent(
        name="",  # Invalid - empty string
        description="Test agent",
        system_prompt="You are a test agent"
    )
except Exception as e:
    print(f"Validation error: {e}")
```

## Model Relationships

```mermaid
graph TD
    Agent -->|has many| Skills
    Agent -->|has many| Workflows
    Agent -->|has many| Tools
    Agent -->|has many| Subagents
    Agent -->|has one| Rules (optional)
    Project -->|contains| Agents
    Project -->|contains| Skills
    Project -->|contains| Workflows
    
    classDef model fill:#1976d2,color:white;
    classDef relation fill:#388e3c,color:white;
```

## Extending IR Models

IR models can be extended through inheritance to add tool-specific or project-specific fields while maintaining compatibility with the core system.

**Example Extension:**
```python
from promptosaurus.ir.models import Agent
from pydantic import Field
from typing import List, Optional

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
    metadata: dict = Field(
        default_factory=dict,
        description="Custom metadata"
    )
    
    class Config:
        frozen = False  # Allow mutations unlike parent
```

## Loading and Persistence

IR models are typically loaded from source files through the loader system and can be serialized/deserialized for storage or transmission.

**Serialization:**
```python
# Convert to dictionary
agent_dict = agent.model_dump()

# Convert to JSON
agent_json = agent.model_dump_json()

# Create from dictionary
agent = Agent.model_load(agent_dict)

# Create from JSON
agent = Agent.model_validate_json(agent_json)
```

## Best Practices

1. **Use Proper Typing:** Leverage Python's type hints for better IDE support and catch errors early
2. **Keep Models Focused:** Each model should have a single responsibility
3. **Validate Early:** Use Pydantic's validation to catch errors at model creation time
4. **Document Fields:** Use Field descriptions to explain the purpose of each attribute
5. **Consider Immutability:** Use frozen=True unless mutation is explicitly needed
6. **Use Descriptive Names:** Choose clear, descriptive names for models and fields
7. **Follow Naming Conventions:** Use snake_case for field names and PascalCase for model names
