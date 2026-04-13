# Claude API Integration Example

This example shows the output from the **ClaudeBuilder** for integration with Claude's Messages API.

## What's Included

- **`code.json`** - Complete Claude configuration in JSON format ready for API integration

## File Format

Claude uses a JSON dictionary format with three main sections:

```json
{
  "system": "System prompt string",
  "tools": [
    {
      "name": "tool_name",
      "description": "What this tool does",
      "input_schema": { /* JSON Schema */ }
    }
  ],
  "instructions": "Additional instructions/guidance"
}
```

## Installation

Use the JSON in your Claude API client:

```python
import anthropic
import json

# Load the configuration
with open('examples/claude/code.json', 'r') as f:
    config = json.load(f)

# Create Claude client
client = anthropic.Anthropic()

# Use in API call
response = client.messages.create(
    model="claude-opus-4-1",
    max_tokens=4096,
    system=config["system"],
    tools=config["tools"],
    messages=[
        {
            "role": "user",
            "content": "Your task here"
        }
    ]
)
```

## JSON Structure Explained

### System Prompt

A string that defines the AI's core behavior:

```json
{
  "system": "You are an expert code generation assistant. Write clean, well-documented Python code following SOLID principles."
}
```

This is the primary instruction that shapes all responses.

### Tools Definition

Array of tools the AI can use. Each tool includes:

- **name**: Tool identifier (e.g., "read", "write")
- **description**: What the tool does
- **input_schema**: JSON Schema defining required/optional parameters

Example:
```json
{
  "name": "read",
  "description": "Read files and directories",
  "input_schema": {
    "type": "object",
    "properties": {
      "filePath": {
        "type": "string",
        "description": "Path to file or directory"
      }
    },
    "required": ["filePath"]
  }
}
```

### Instructions

Additional guidance as a formatted string. Can include:
- Detailed workflows
- Best practices
- Constraints and rules
- Examples

## Customization Guide

### Change System Prompt

Edit the system field:

```json
{
  "system": "You are an expert test engineer..."
}
```

### Add a Custom Tool

Add to the tools array:

```json
{
  "tools": [
    {
      "name": "custom-tool",
      "description": "Description of what it does",
      "input_schema": {
        "type": "object",
        "properties": {
          "param1": {
            "type": "string",
            "description": "Description"
          }
        },
        "required": ["param1"]
      }
    }
  ]
}
```

### Update Instructions

Modify the instructions string:

```json
{
  "instructions": "# Custom Instructions\n\nYour detailed instructions here..."
}
```

## Common Patterns

### Python Development Assistant

```json
{
  "system": "You are an expert Python developer. Write clean, type-hinted, well-tested code following PEP 8 and SOLID principles.",
  "tools": [
    {
      "name": "read",
      "description": "Read Python files to understand code structure"
    },
    {
      "name": "write",
      "description": "Write Python files and tests"
    },
    {
      "name": "execute",
      "description": "Run tests and verify code"
    }
  ],
  "instructions": "# Python Development Standards\n\n- Use type hints on all public functions\n- Write pytest tests\n- Follow PEP 8\n- Achieve 80%+ coverage"
}
```

### Code Reviewer

```json
{
  "system": "You are an expert code reviewer. Provide constructive feedback on code quality, maintainability, and correctness.",
  "tools": [
    {
      "name": "read",
      "description": "Read code files for review"
    }
  ],
  "instructions": "# Code Review Standards\n\n- Focus on readability and maintainability\n- Identify potential bugs\n- Check for proper error handling\n- Verify test coverage\n- Provide constructive feedback"
}
```

### Documentation Generator

```json
{
  "system": "You are a technical writer. Generate clear, comprehensive documentation with examples.",
  "tools": [
    {
      "name": "read",
      "description": "Read source code"
    },
    {
      "name": "write",
      "description": "Write documentation files"
    }
  ],
  "instructions": "# Documentation Standards\n\n- Include practical examples\n- Explain the why, not just the how\n- Use clear language\n- Cross-reference related topics"
}
```

## Tool Input Schemas

### JSON Schema Reference

Common schema patterns:

**String parameter:**
```json
{
  "type": "string",
  "description": "Parameter description"
}
```

**Optional number:**
```json
{
  "type": "number",
  "description": "Parameter description"
}
```

**Array of strings:**
```json
{
  "type": "array",
  "items": { "type": "string" },
  "description": "List of items"
}
```

**Object with properties:**
```json
{
  "type": "object",
  "properties": {
    "field1": { "type": "string" },
    "field2": { "type": "number" }
  },
  "required": ["field1"]
}
```

**Enum (limited options):**
```json
{
  "type": "string",
  "enum": ["option1", "option2", "option3"],
  "description": "Must be one of the listed options"
}
```

## Validation

Before using the JSON, validate it:

```python
import json

# Load and validate
with open('code.json', 'r') as f:
    config = json.load(f)

# Check required fields
assert "system" in config
assert "tools" in config
assert "instructions" in config

# Verify structure
assert isinstance(config["system"], str)
assert isinstance(config["tools"], list)
assert isinstance(config["instructions"], str)

# Verify each tool has required fields
for tool in config["tools"]:
    assert "name" in tool
    assert "description" in tool
    assert "input_schema" in tool
```

## Integration Examples

### Using with Claude SDK

```python
import anthropic
import json

with open('code.json') as f:
    config = json.load(f)

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-1",
    max_tokens=2048,
    system=config["system"],
    tools=config["tools"],
    messages=[
        {
            "role": "user",
            "content": "Generate a Python function that..."
        }
    ]
)
```

### Using with REST API

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-4-1",
    "max_tokens": 2048,
    "system": "You are an expert code generation assistant...",
    "tools": [/* tools from JSON */],
    "messages": [
      {
        "role": "user",
        "content": "Your task here"
      }
    ]
  }'
```

### Using with LangChain

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import Tool
import json

with open('code.json') as f:
    config = json.load(f)

# Convert JSON tools to LangChain tools
tools = []
for tool_def in config["tools"]:
    tools.append(Tool(
        name=tool_def["name"],
        description=tool_def["description"],
        func=lambda x: f"Executing {tool_def['name']}"
    ))

# Create LLM with tools
llm = ChatAnthropic(
    model="claude-opus-4-1",
    system_prompt=config["system"]
).bind_tools(tools)
```

## Troubleshooting

### Invalid JSON

**Check:**
1. File is valid JSON (use `json.dumps()` to validate)
2. All strings are properly quoted
3. No trailing commas in objects/arrays

**Validate:**
```bash
python3 -m json.tool code.json > /dev/null && echo "Valid JSON"
```

### Tool schema not recognized

**Check:**
1. `input_schema` is valid JSON Schema
2. Schema has `type: "object"` at root
3. `properties` object exists
4. Parameter types are valid (`string`, `number`, `object`, `array`, `boolean`)

**Verify:**
```python
import json
from jsonschema import Draft7Validator

with open('code.json') as f:
    config = json.load(f)

for tool in config["tools"]:
    try:
        Draft7Validator.check_schema(tool["input_schema"])
        print(f"✓ {tool['name']} schema is valid")
    except Exception as e:
        print(f"✗ {tool['name']} schema error: {e}")
```

### Claude not using tools

**Check:**
1. Tools are properly defined with valid schema
2. System prompt suggests when to use tools
3. Instructions mention tool availability
4. Tool descriptions are clear and specific

**Improve:**
- Make instructions more explicit about tool usage
- Provide examples of when to use each tool
- Ensure tool descriptions are clear

## File Placement

Choose where to store the JSON based on your use case:

```
your-project/
├── config/
│   └── claude.json          ← Configuration directory
├── src/
│   └── ai/
│       └── config.json      ← With AI code
├── claude-config.json       ← Project root
└── code.json                ← Current location in example
```

## Best Practices

### Keep It Concise

Long system prompts are less effective. Keep to essential information.

### Be Specific

Instead of:
```json
{
  "system": "You are helpful and write good code"
}
```

Better:
```json
{
  "system": "You are an expert Python developer. Write type-hinted code following PEP 8 and SOLID principles."
}
```

### Provide Examples

In instructions, include concrete examples:

```json
{
  "instructions": "# Function Naming\n\nGood: parse_user_config()\nBad: parse()"
}
```

### Document Tool Schemas

Make tool descriptions match the schema:

```json
{
  "name": "read_file",
  "description": "Read a file. Parameters: file_path (string, required), limit (number, optional)",
  "input_schema": { /* ... */ }
}
```

## Next Steps

1. **Copy the example** to your project
2. **Customize** the system prompt for your use case
3. **Add tools** relevant to your task
4. **Update instructions** with your workflow
5. **Test** with Claude API
6. **Iterate** based on results

## For More Information

- [Claude API Documentation](https://docs.anthropic.com)
- [Messages API Guide](https://docs.anthropic.com/en/docs/build-a-chatbot)
- [Tools Overview](https://docs.anthropic.com/en/docs/build-a-chatbot#tools)
- [Builder Documentation](../../docs/BUILDERS.md)
