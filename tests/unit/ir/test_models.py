"""Comprehensive unit tests for IR layer models with 100% coverage.

Tests cover:
- Happy path: Valid model creation with all required fields
- Edge cases: Empty lists, empty dicts, boundary values
- Validation: Field constraints (min_length, required, etc.)
- Immutability: Models are frozen and cannot be modified
- Schema validation: Export to dict/JSON and validation errors
"""

import pytest
from pydantic import ValidationError

from prompticorn.ir.models import Agent, Project, Rules, Skill, Tool, Workflow

# ============================================================================
# FIXTURES - Common test data
# ============================================================================


@pytest.fixture
def valid_agent() -> Agent:
    """Create a valid agent with all fields."""
    return Agent(
        name="code",
        description="Code implementation specialist",
        system_prompt="You are an expert code writer.",
        tools=["git", "python"],
        skills=["refactor", "test"],
        workflows=["code-review"],
        subagents=["formatter"],
    )


@pytest.fixture
def valid_skill() -> Skill:
    """Create a valid skill."""
    return Skill(
        name="refactor",
        description="Improve code structure",
        instructions="Apply SOLID principles and design patterns.",
        tools_needed=["git", "python"],
    )


@pytest.fixture
def valid_workflow() -> Workflow:
    """Create a valid workflow."""
    return Workflow(
        name="code-review",
        description="Review code for quality",
        steps=[
            "Analyze code structure",
            "Check test coverage",
            "Verify error handling",
            "Approve or request changes",
        ],
    )


@pytest.fixture
def valid_tool() -> Tool:
    """Create a valid tool."""
    return Tool(
        name="git",
        description="Version control system",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "args": {"type": "array"},
            },
        },
    )


@pytest.fixture
def valid_rules() -> Rules:
    """Create valid rules."""
    return Rules(
        constraints=[
            "Do not delete production code without approval",
            "All commits must have tests",
        ],
        guidelines={
            "code": ["Follow PEP 8", "Use type hints"],
            "security": ["Validate all inputs", "Use secure defaults"],
        },
    )


@pytest.fixture
def valid_project() -> Project:
    """Create a valid project."""
    return Project(
        registry_settings={"timeout": 30, "retries": 3},
        verbosity="verbose",
        builder_configs={"python": {"version": "3.11"}},
    )


# ============================================================================
# AGENT MODEL TESTS
# ============================================================================


class TestAgent:
    """Test Agent model."""

    def test_agent_creation_valid(self, valid_agent: Agent) -> None:
        """Test creating a valid agent with all fields."""
        assert valid_agent.name == "code"
        assert valid_agent.description == "Code implementation specialist"
        assert valid_agent.system_prompt == "You are an expert code writer."
        assert valid_agent.tools == ["git", "python"]
        assert valid_agent.skills == ["refactor", "test"]
        assert valid_agent.workflows == ["code-review"]
        assert valid_agent.subagents == ["formatter"]

    def test_agent_creation_minimal(self) -> None:
        """Test creating an agent with only required fields."""
        agent = Agent(
            name="test",
            description="Test agent",
            system_prompt="You are a test agent.",
        )
        assert agent.name == "test"
        assert agent.description == "Test agent"
        assert agent.system_prompt == "You are a test agent."
        assert agent.tools == []
        assert agent.skills == []
        assert agent.workflows == []
        assert agent.subagents == []

    def test_agent_empty_lists_default(self) -> None:
        """Test that empty lists are allowed by default_factory."""
        agent = Agent(
            name="test",
            description="Test agent",
            system_prompt="System prompt",
            tools=[],
            skills=[],
            workflows=[],
            subagents=[],
        )
        assert agent.tools == []
        assert agent.skills == []
        assert agent.workflows == []
        assert agent.subagents == []

    def test_agent_name_required(self) -> None:
        """Test that agent name is required."""
        with pytest.raises(ValidationError) as exc_info:
            Agent(  # type: ignore[call-argument]
                description="Test agent",
                system_prompt="System prompt",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_agent_name_non_empty(self) -> None:
        """Test that agent name cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Agent(
                name="",
                description="Test agent",
                system_prompt="System prompt",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_agent_description_required(self) -> None:
        """Test that agent description is required."""
        with pytest.raises(ValidationError) as exc_info:
            Agent(  # type: ignore[call-argument]
                name="test",
                system_prompt="System prompt",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("description",) for error in errors)

    def test_agent_description_non_empty(self) -> None:
        """Test that agent description cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Agent(
                name="test",
                description="",
                system_prompt="System prompt",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("description",) for error in errors)

    def test_agent_system_prompt_required(self) -> None:
        """Test that system prompt is required."""
        with pytest.raises(ValidationError) as exc_info:
            Agent(  # type: ignore[call-argument]
                name="test",
                description="Test agent",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("system_prompt",) for error in errors)

    def test_agent_system_prompt_non_empty(self) -> None:
        """Test that system prompt cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Agent(
                name="test",
                description="Test agent",
                system_prompt="",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("system_prompt",) for error in errors)

    def test_agent_frozen(self, valid_agent: Agent) -> None:
        """Test that agent is immutable (frozen=True)."""
        with pytest.raises(ValidationError):
            valid_agent.name = "different"

    def test_agent_frozen_list_fields(self, valid_agent: Agent) -> None:
        """Test that list fields in frozen agent cannot be modified."""
        with pytest.raises(ValidationError):
            valid_agent.tools = ["new_tool"]

    def test_agent_export_to_dict(self, valid_agent: Agent) -> None:
        """Test exporting agent to dictionary."""
        agent_dict = valid_agent.model_dump()
        assert agent_dict["name"] == "code"
        assert agent_dict["description"] == "Code implementation specialist"
        assert agent_dict["system_prompt"] == "You are an expert code writer."
        assert agent_dict["tools"] == ["git", "python"]

    def test_agent_export_to_json(self, valid_agent: Agent) -> None:
        """Test exporting agent to JSON."""
        agent_json = valid_agent.model_dump_json()
        assert isinstance(agent_json, str)
        assert "code" in agent_json
        assert "Code implementation specialist" in agent_json

    def test_agent_model_validate_from_dict(self) -> None:
        """Test validating agent from dictionary."""
        agent_dict = {
            "name": "test",
            "description": "Test agent",
            "system_prompt": "System prompt",
        }
        agent = Agent.model_validate(agent_dict)
        assert agent.name == "test"
        assert agent.description == "Test agent"

    def test_agent_tools_with_multiple_items(self) -> None:
        """Test agent with multiple tools."""
        agent = Agent(
            name="test",
            description="Test",
            system_prompt="Prompt",
            tools=["git", "python", "docker", "kubernetes"],
        )
        assert len(agent.tools) == 4
        assert "docker" in agent.tools

    def test_agent_subagents_hierarchy(self) -> None:
        """Test agent with subagents for hierarchical composition."""
        agent = Agent(
            name="manager",
            description="Manages subagents",
            system_prompt="Coordinate work",
            subagents=["coder", "tester", "reviewer"],
        )
        assert len(agent.subagents) == 3
        assert "coder" in agent.subagents


# ============================================================================
# SKILL MODEL TESTS
# ============================================================================


class TestSkill:
    """Test Skill model."""

    def test_skill_creation_valid(self, valid_skill: Skill) -> None:
        """Test creating a valid skill."""
        assert valid_skill.name == "refactor"
        assert valid_skill.description == "Improve code structure"
        assert valid_skill.instructions == "Apply SOLID principles and design patterns."
        assert valid_skill.tools_needed == ["git", "python"]

    def test_skill_creation_minimal(self) -> None:
        """Test creating a skill with only required fields."""
        skill = Skill(
            name="test",
            description="Test skill",
            instructions="Do something.",
        )
        assert skill.name == "test"
        assert skill.description == "Test skill"
        assert skill.instructions == "Do something."
        assert skill.tools_needed == []

    def test_skill_tools_needed_empty(self) -> None:
        """Test that tools_needed can be empty list by default."""
        skill = Skill(
            name="test",
            description="Test skill",
            instructions="Instructions",
        )
        assert skill.tools_needed == []

    def test_skill_tools_needed_explicit_empty(self) -> None:
        """Test explicitly setting tools_needed to empty list."""
        skill = Skill(
            name="test",
            description="Test skill",
            instructions="Instructions",
            tools_needed=[],
        )
        assert skill.tools_needed == []

    def test_skill_name_required(self) -> None:
        """Test that skill name is required."""
        with pytest.raises(ValidationError) as exc_info:
            Skill(  # type: ignore[call-argument]
                description="Test skill",
                instructions="Instructions",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_skill_name_non_empty(self) -> None:
        """Test that skill name cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Skill(
                name="",
                description="Test skill",
                instructions="Instructions",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_skill_description_required(self) -> None:
        """Test that skill description is required."""
        with pytest.raises(ValidationError) as exc_info:
            Skill(  # type: ignore[call-argument]
                name="test",
                instructions="Instructions",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("description",) for error in errors)

    def test_skill_description_non_empty(self) -> None:
        """Test that skill description cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Skill(
                name="test",
                description="",
                instructions="Instructions",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("description",) for error in errors)

    def test_skill_instructions_required(self) -> None:
        """Test that skill instructions are required."""
        with pytest.raises(ValidationError) as exc_info:
            Skill(  # type: ignore[call-argument]
                name="test",
                description="Test skill",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("instructions",) for error in errors)

    def test_skill_instructions_non_empty(self) -> None:
        """Test that skill instructions cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Skill(
                name="test",
                description="Test skill",
                instructions="",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("instructions",) for error in errors)

    def test_skill_frozen(self, valid_skill: Skill) -> None:
        """Test that skill is immutable (frozen=True)."""
        with pytest.raises(ValidationError):
            valid_skill.name = "different"

    def test_skill_frozen_list_fields(self, valid_skill: Skill) -> None:
        """Test that list fields in frozen skill cannot be modified."""
        with pytest.raises(ValidationError):
            valid_skill.tools_needed = ["new_tool"]

    def test_skill_export_to_dict(self, valid_skill: Skill) -> None:
        """Test exporting skill to dictionary."""
        skill_dict = valid_skill.model_dump()
        assert skill_dict["name"] == "refactor"
        assert skill_dict["description"] == "Improve code structure"
        assert skill_dict["instructions"] == "Apply SOLID principles and design patterns."

    def test_skill_export_to_json(self, valid_skill: Skill) -> None:
        """Test exporting skill to JSON."""
        skill_json = valid_skill.model_dump_json()
        assert isinstance(skill_json, str)
        assert "refactor" in skill_json

    def test_skill_with_many_tools(self) -> None:
        """Test skill with multiple tools required."""
        skill = Skill(
            name="test",
            description="Complex skill",
            instructions="Instructions",
            tools_needed=["git", "python", "docker", "kubernetes", "aws"],
        )
        assert len(skill.tools_needed) == 5


# ============================================================================
# WORKFLOW MODEL TESTS
# ============================================================================


class TestWorkflow:
    """Test Workflow model."""

    def test_workflow_creation_valid(self, valid_workflow: Workflow) -> None:
        """Test creating a valid workflow."""
        assert valid_workflow.name == "code-review"
        assert valid_workflow.description == "Review code for quality"
        assert len(valid_workflow.steps) == 4
        assert valid_workflow.steps[0] == "Analyze code structure"

    def test_workflow_creation_single_step(self) -> None:
        """Test creating a workflow with a single step."""
        workflow = Workflow(
            name="test",
            description="Simple workflow",
            steps=["Do something"],
        )
        assert len(workflow.steps) == 1
        assert workflow.steps[0] == "Do something"

    def test_workflow_steps_required(self) -> None:
        """Test that workflow steps are required."""
        with pytest.raises(ValidationError) as exc_info:
            Workflow(  # type: ignore[call-argument]
                name="test",
                description="Workflow",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("steps",) for error in errors)

    def test_workflow_steps_must_be_non_empty(self) -> None:
        """Test that workflow must have at least one step."""
        with pytest.raises(ValidationError) as exc_info:
            Workflow(
                name="test",
                description="Workflow",
                steps=[],
            )
        errors = exc_info.value.errors()
        # Check that validation error is for steps field
        assert any(error["loc"] == ("steps",) for error in errors)

    def test_workflow_name_required(self) -> None:
        """Test that workflow name is required."""
        with pytest.raises(ValidationError) as exc_info:
            Workflow(  # type: ignore[call-argument]
                description="Workflow",
                steps=["Step 1"],
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_workflow_name_non_empty(self) -> None:
        """Test that workflow name cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Workflow(
                name="",
                description="Workflow",
                steps=["Step 1"],
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_workflow_description_required(self) -> None:
        """Test that workflow description is required."""
        with pytest.raises(ValidationError) as exc_info:
            Workflow(  # type: ignore[call-argument]
                name="test",
                steps=["Step 1"],
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("description",) for error in errors)

    def test_workflow_description_non_empty(self) -> None:
        """Test that workflow description cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Workflow(
                name="test",
                description="",
                steps=["Step 1"],
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("description",) for error in errors)

    def test_workflow_steps_list_of_strings(self) -> None:
        """Test that steps is a list of strings."""
        workflow = Workflow(
            name="test",
            description="Test workflow",
            steps=["Step 1", "Step 2", "Step 3"],
        )
        assert all(isinstance(step, str) for step in workflow.steps)

    def test_workflow_frozen(self, valid_workflow: Workflow) -> None:
        """Test that workflow is immutable (frozen=True)."""
        with pytest.raises(ValidationError):
            valid_workflow.name = "different"

    def test_workflow_frozen_steps(self, valid_workflow: Workflow) -> None:
        """Test that steps list in frozen workflow cannot be modified."""
        with pytest.raises(ValidationError):
            valid_workflow.steps = ["New step"]

    def test_workflow_export_to_dict(self, valid_workflow: Workflow) -> None:
        """Test exporting workflow to dictionary."""
        workflow_dict = valid_workflow.model_dump()
        assert workflow_dict["name"] == "code-review"
        assert workflow_dict["description"] == "Review code for quality"
        assert len(workflow_dict["steps"]) == 4

    def test_workflow_export_to_json(self, valid_workflow: Workflow) -> None:
        """Test exporting workflow to JSON."""
        workflow_json = valid_workflow.model_dump_json()
        assert isinstance(workflow_json, str)
        assert "code-review" in workflow_json
        assert "Analyze code structure" in workflow_json

    def test_workflow_many_steps(self) -> None:
        """Test workflow with many steps."""
        steps = [f"Step {i}" for i in range(1, 21)]
        workflow = Workflow(
            name="complex",
            description="Complex workflow",
            steps=steps,
        )
        assert len(workflow.steps) == 20

    def test_workflow_long_step_descriptions(self) -> None:
        """Test workflow with long step descriptions."""
        workflow = Workflow(
            name="test",
            description="Test",
            steps=[
                "This is a very long step description that explains in detail what needs to be done",
                "Another step with comprehensive instructions",
            ],
        )
        assert len(workflow.steps[0]) > 50


# ============================================================================
# TOOL MODEL TESTS
# ============================================================================


class TestTool:
    """Test Tool model."""

    def test_tool_creation_valid(self, valid_tool: Tool) -> None:
        """Test creating a valid tool."""
        assert valid_tool.name == "git"
        assert valid_tool.description == "Version control system"
        assert isinstance(valid_tool.parameters, dict)
        assert "properties" in valid_tool.parameters

    def test_tool_creation_minimal(self) -> None:
        """Test creating a tool with only required fields."""
        tool = Tool(
            name="test",
            description="Test tool",
        )
        assert tool.name == "test"
        assert tool.description == "Test tool"
        assert tool.parameters == {}

    def test_tool_parameters_empty_by_default(self) -> None:
        """Test that parameters default to empty dict."""
        tool = Tool(
            name="test",
            description="Test tool",
        )
        assert tool.parameters == {}

    def test_tool_parameters_explicit_empty(self) -> None:
        """Test explicitly setting parameters to empty dict."""
        tool = Tool(
            name="test",
            description="Test tool",
            parameters={},
        )
        assert tool.parameters == {}

    def test_tool_parameters_json_schema(self) -> None:
        """Test tool with JSON schema parameters."""
        tool = Tool(
            name="test",
            description="Test tool",
            parameters={
                "type": "object",
                "required": ["command"],
                "properties": {
                    "command": {"type": "string"},
                    "args": {"type": "array", "items": {"type": "string"}},
                },
            },
        )
        assert tool.parameters["type"] == "object"
        assert "properties" in tool.parameters

    def test_tool_name_required(self) -> None:
        """Test that tool name is required."""
        with pytest.raises(ValidationError) as exc_info:
            Tool(  # type: ignore[call-argument]
                description="Test tool",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_tool_name_non_empty(self) -> None:
        """Test that tool name cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Tool(
                name="",
                description="Test tool",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_tool_description_required(self) -> None:
        """Test that tool description is required."""
        with pytest.raises(ValidationError) as exc_info:
            Tool(  # type: ignore[call-argument]
                name="test",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("description",) for error in errors)

    def test_tool_description_non_empty(self) -> None:
        """Test that tool description cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Tool(
                name="test",
                description="",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("description",) for error in errors)

    def test_tool_frozen(self, valid_tool: Tool) -> None:
        """Test that tool is immutable (frozen=True)."""
        with pytest.raises(ValidationError):
            valid_tool.name = "different"

    def test_tool_frozen_dict_fields(self, valid_tool: Tool) -> None:
        """Test that dict fields in frozen tool cannot be modified."""
        with pytest.raises(ValidationError):
            valid_tool.parameters = {"new": "value"}

    def test_tool_export_to_dict(self, valid_tool: Tool) -> None:
        """Test exporting tool to dictionary."""
        tool_dict = valid_tool.model_dump()
        assert tool_dict["name"] == "git"
        assert tool_dict["description"] == "Version control system"

    def test_tool_export_to_json(self, valid_tool: Tool) -> None:
        """Test exporting tool to JSON."""
        tool_json = valid_tool.model_dump_json()
        assert isinstance(tool_json, str)
        assert "git" in tool_json

    def test_tool_complex_parameters(self) -> None:
        """Test tool with complex nested parameters."""
        tool = Tool(
            name="api",
            description="API tool",
            parameters={
                "type": "object",
                "properties": {
                    "endpoint": {"type": "string"},
                    "headers": {
                        "type": "object",
                        "properties": {
                            "authorization": {"type": "string"},
                            "content-type": {"type": "string"},
                        },
                    },
                    "body": {"type": "object"},
                },
            },
        )
        assert "headers" in tool.parameters["properties"]


# ============================================================================
# RULES MODEL TESTS
# ============================================================================


class TestRules:
    """Test Rules model."""

    def test_rules_creation_valid(self, valid_rules: Rules) -> None:
        """Test creating valid rules."""
        assert len(valid_rules.constraints) == 2
        assert len(valid_rules.guidelines) == 2
        assert "code" in valid_rules.guidelines

    def test_rules_creation_empty(self) -> None:
        """Test creating rules with all empty defaults."""
        rules = Rules()
        assert rules.constraints == []
        assert rules.guidelines == {}

    def test_rules_constraints_default_empty(self) -> None:
        """Test that constraints default to empty list."""
        rules = Rules()
        assert rules.constraints == []

    def test_rules_constraints_explicit_empty(self) -> None:
        """Test explicitly setting constraints to empty list."""
        rules = Rules(constraints=[])
        assert rules.constraints == []

    def test_rules_guidelines_default_empty(self) -> None:
        """Test that guidelines default to empty dict."""
        rules = Rules()
        assert rules.guidelines == {}

    def test_rules_guidelines_explicit_empty(self) -> None:
        """Test explicitly setting guidelines to empty dict."""
        rules = Rules(guidelines={})
        assert rules.guidelines == {}

    def test_rules_with_constraints(self) -> None:
        """Test rules with multiple constraints."""
        rules = Rules(
            constraints=[
                "Constraint 1",
                "Constraint 2",
                "Constraint 3",
            ]
        )
        assert len(rules.constraints) == 3

    def test_rules_with_guidelines(self) -> None:
        """Test rules with categorized guidelines."""
        rules = Rules(
            guidelines={
                "performance": ["Cache results", "Use async"],
                "security": ["Validate inputs", "Encrypt data"],
            }
        )
        assert "performance" in rules.guidelines
        assert "security" in rules.guidelines

    def test_rules_flexible_structure(self) -> None:
        """Test rules with flexible/nested structure."""
        rules = Rules(
            guidelines={
                "complex": {
                    "nested": {
                        "structure": ["value1", "value2"],
                    }
                }
            }
        )
        assert rules.guidelines["complex"]["nested"]["structure"] == ["value1", "value2"]

    def test_rules_frozen(self, valid_rules: Rules) -> None:
        """Test that rules are immutable (frozen=True)."""
        with pytest.raises(ValidationError):
            valid_rules.constraints = []

    def test_rules_frozen_dict_fields(self, valid_rules: Rules) -> None:
        """Test that dict fields in frozen rules cannot be modified."""
        with pytest.raises(ValidationError):
            valid_rules.guidelines = {}

    def test_rules_export_to_dict(self, valid_rules: Rules) -> None:
        """Test exporting rules to dictionary."""
        rules_dict = valid_rules.model_dump()
        assert "constraints" in rules_dict
        assert "guidelines" in rules_dict
        assert len(rules_dict["constraints"]) == 2

    def test_rules_export_to_json(self, valid_rules: Rules) -> None:
        """Test exporting rules to JSON."""
        rules_json = valid_rules.model_dump_json()
        assert isinstance(rules_json, str)
        assert "constraints" in rules_json
        assert "guidelines" in rules_json

    def test_rules_mixed_types_in_guidelines(self) -> None:
        """Test rules with mixed types in guidelines values."""
        rules = Rules(
            guidelines={
                "strings": ["value1", "value2"],
                "numbers": [1, 2, 3],
                "mixed": ["string", 42, True],
                "nested": {"key": "value"},
            }
        )
        assert isinstance(rules.guidelines["numbers"], list)
        assert isinstance(rules.guidelines["nested"], dict)


# ============================================================================
# PROJECT MODEL TESTS
# ============================================================================


class TestProject:
    """Test Project model."""

    def test_project_creation_valid(self, valid_project: Project) -> None:
        """Test creating a valid project."""
        assert isinstance(valid_project.registry_settings, dict)
        assert valid_project.verbosity == "verbose"
        assert isinstance(valid_project.builder_configs, dict)

    def test_project_creation_minimal(self) -> None:
        """Test creating a project with defaults."""
        project = Project()
        assert project.registry_settings == {}
        assert project.verbosity == "minimal"
        assert project.builder_configs == {}

    def test_project_verbosity_minimal(self) -> None:
        """Test project with minimal verbosity."""
        project = Project(verbosity="minimal")
        assert project.verbosity == "minimal"

    def test_project_verbosity_verbose(self) -> None:
        """Test project with verbose verbosity."""
        project = Project(verbosity="verbose")
        assert project.verbosity == "verbose"

    def test_project_verbosity_invalid(self) -> None:
        """Test project with invalid verbosity value."""
        with pytest.raises(ValidationError) as exc_info:
            Project(verbosity="debug")  # type: ignore[arg-type]
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("verbosity",) for error in errors)

    def test_project_verbosity_default_minimal(self) -> None:
        """Test that verbosity defaults to minimal."""
        project = Project()
        assert project.verbosity == "minimal"

    def test_project_registry_settings_default_empty(self) -> None:
        """Test that registry_settings default to empty dict."""
        project = Project()
        assert project.registry_settings == {}

    def test_project_registry_settings_with_values(self) -> None:
        """Test project with registry settings."""
        project = Project(
            registry_settings={
                "timeout": 30,
                "retries": 3,
                "cache": True,
            }
        )
        assert project.registry_settings["timeout"] == 30
        assert project.registry_settings["retries"] == 3

    def test_project_builder_configs_default_empty(self) -> None:
        """Test that builder_configs default to empty dict."""
        project = Project()
        assert project.builder_configs == {}

    def test_project_builder_configs_with_values(self) -> None:
        """Test project with builder configurations."""
        project = Project(
            builder_configs={
                "python": {"version": "3.11", "venv": True},
                "nodejs": {"version": "18", "package_manager": "npm"},
            }
        )
        assert "python" in project.builder_configs
        assert "nodejs" in project.builder_configs

    def test_project_frozen(self, valid_project: Project) -> None:
        """Test that project is immutable (frozen=True)."""
        with pytest.raises(ValidationError):
            valid_project.verbosity = "debug"  # type: ignore[assignment]

    def test_project_frozen_dict_fields(self, valid_project: Project) -> None:
        """Test that dict fields in frozen project cannot be modified."""
        with pytest.raises(ValidationError):
            valid_project.registry_settings = {}

    def test_project_export_to_dict(self, valid_project: Project) -> None:
        """Test exporting project to dictionary."""
        project_dict = valid_project.model_dump()
        assert "registry_settings" in project_dict
        assert "verbosity" in project_dict
        assert "builder_configs" in project_dict
        assert project_dict["verbosity"] == "verbose"

    def test_project_export_to_json(self, valid_project: Project) -> None:
        """Test exporting project to JSON."""
        project_json = valid_project.model_dump_json()
        assert isinstance(project_json, str)
        assert "verbose" in project_json

    def test_project_complex_registry_settings(self) -> None:
        """Test project with complex nested registry settings."""
        project = Project(
            registry_settings={
                "server": {
                    "host": "localhost",
                    "port": 8000,
                    "ssl": {
                        "enabled": True,
                        "cert": "/path/to/cert",
                    },
                },
                "database": {
                    "connections": [
                        {"host": "db1", "port": 5432},
                        {"host": "db2", "port": 5432},
                    ]
                },
            }
        )
        assert project.registry_settings["server"]["host"] == "localhost"
        assert len(project.registry_settings["database"]["connections"]) == 2

    def test_project_all_fields_populated(self) -> None:
        """Test project with all fields populated."""
        project = Project(
            registry_settings={"key": "value"},
            verbosity="verbose",
            builder_configs={"builder": "config"},
        )
        assert project.registry_settings == {"key": "value"}
        assert project.verbosity == "verbose"
        assert project.builder_configs == {"builder": "config"}


# ============================================================================
# CROSS-MODEL INTEGRATION TESTS
# ============================================================================


class TestModelIntegration:
    """Test integration between models."""

    def test_agent_with_skill_names(self, valid_agent: Agent, valid_skill: Skill) -> None:
        """Test agent referencing skill names."""
        agent = Agent(
            name="test",
            description="Test",
            system_prompt="Prompt",
            skills=[valid_skill.name],
        )
        assert valid_skill.name in agent.skills

    def test_agent_with_tool_names(self, valid_agent: Agent, valid_tool: Tool) -> None:
        """Test agent referencing tool names."""
        agent = Agent(
            name="test",
            description="Test",
            system_prompt="Prompt",
            tools=[valid_tool.name],
        )
        assert valid_tool.name in agent.tools

    def test_skill_with_tool_names(self, valid_skill: Skill, valid_tool: Tool) -> None:
        """Test skill referencing tool names."""
        skill = Skill(
            name="test",
            description="Test",
            instructions="Instructions",
            tools_needed=[valid_tool.name],
        )
        assert valid_tool.name in skill.tools_needed

    def test_agent_with_workflow_names(self, valid_agent: Agent, valid_workflow: Workflow) -> None:
        """Test agent referencing workflow names."""
        agent = Agent(
            name="test",
            description="Test",
            system_prompt="Prompt",
            workflows=[valid_workflow.name],
        )
        assert valid_workflow.name in agent.workflows

    def test_all_models_can_be_serialized_together(
        self,
        valid_agent: Agent,
        valid_skill: Skill,
        valid_workflow: Workflow,
        valid_tool: Tool,
        valid_rules: Rules,
        valid_project: Project,
    ) -> None:
        """Test that all models can be serialized to JSON simultaneously."""
        models = {
            "agent": valid_agent.model_dump_json(),
            "skill": valid_skill.model_dump_json(),
            "workflow": valid_workflow.model_dump_json(),
            "tool": valid_tool.model_dump_json(),
            "rules": valid_rules.model_dump_json(),
            "project": valid_project.model_dump_json(),
        }
        for _key, json_str in models.items():
            assert isinstance(json_str, str)
            assert len(json_str) > 0
