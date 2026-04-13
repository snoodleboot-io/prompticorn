"""Unit tests for PersonaRegistry"""

import pytest
from pathlib import Path
from promptosaurus.personas.registry import PersonaRegistry


@pytest.fixture
def personas_yaml_path():
    """Path to the personas.yaml file"""
    return Path("promptosaurus/personas/personas.yaml")


@pytest.fixture
def registry(personas_yaml_path):
    """Loaded PersonaRegistry instance"""
    return PersonaRegistry.from_yaml(personas_yaml_path)


class TestPersonaRegistry:
    """Tests for PersonaRegistry class"""
    
    def test_load_from_yaml(self, registry):
        """Test loading personas from YAML file"""
        assert registry is not None
        assert len(registry.list_personas()) > 0
    
    def test_list_personas(self, registry):
        """Test listing all persona IDs"""
        personas = registry.list_personas()
        
        # Should have 9 personas as defined in ADR-001
        assert len(personas) == 9
        
        # Check expected personas exist
        expected_personas = [
            "software_engineer",
            "architect",
            "qa_tester",
            "devops_engineer",
            "security_engineer",
            "product_manager",
            "data_engineer",
            "data_scientist",
            "technical_writer",
        ]
        
        for expected in expected_personas:
            assert expected in personas, f"Missing persona: {expected}"
    
    def test_get_display_name(self, registry):
        """Test getting display names for personas"""
        display_name = registry.get_display_name("software_engineer")
        assert display_name == "Software Engineer"
        
        display_name2 = registry.get_display_name("qa_tester")
        # Note: YAML has "QA / Tester" with spaces
        assert "QA" in display_name2 and "Tester" in display_name2
    
    def test_get_description(self, registry):
        """Test getting descriptions for personas"""
        desc = registry.get_description("software_engineer")
        assert desc is not None
        assert len(desc) > 0
        assert "software" in desc.lower() or "development" in desc.lower()
    
    def test_get_agents_for_persona(self, registry):
        """Test getting agents for a persona"""
        agents = registry.get_agents_for_persona("software_engineer")
        
        # Software Engineer should have agents
        assert len(agents) > 0
        
        # Should have code agent (primary for Software Engineer)
        assert "code" in agents
        
        # Should have test agent (primary for Software Engineer)
        assert "test" in agents
    
    def test_qa_tester_no_code_agent(self, registry):
        """Test that QA/Tester does NOT have code agent"""
        agents = registry.get_agents_for_persona("qa_tester")
        
        # QA/Tester should have test agent
        assert "test" in agents
        
        # QA/Tester should NOT have code agent (per ADR-001 design)
        assert "code" not in agents
    
    def test_get_workflows_for_persona(self, registry):
        """Test getting workflows for a persona"""
        workflows = registry.get_workflows_for_persona("software_engineer")
        
        # Software Engineer should have workflows
        assert len(workflows) > 0
        
        # Should have code workflow
        assert "code" in workflows
    
    def test_get_skills_for_persona(self, registry):
        """Test getting skills for a persona"""
        skills = registry.get_skills_for_persona("software_engineer")
        
        # Software Engineer should have skills
        assert len(skills) > 0
    
    def test_get_universal_agents(self, registry):
        """Test getting universal agents"""
        universal = registry.get_universal_agents()
        
        # Should have 5 universal agents (per ADR-001)
        assert len(universal) == 5
        
        # Check expected universal agents
        expected_universal = ["ask", "debug", "explain", "plan", "orchestrator"]
        for expected in expected_universal:
            assert expected in universal, f"Missing universal agent: {expected}"
    
    def test_invalid_persona_id(self, registry):
        """Test handling of invalid persona ID"""
        with pytest.raises(KeyError):
            registry.get_persona_info("invalid_persona_id")
    
    def test_persona_has_focus(self, registry):
        """Test that personas have focus field"""
        persona_info = registry.get_persona_info("software_engineer")
        focus = persona_info.get("focus")
        assert focus is not None
        assert len(focus) > 0
