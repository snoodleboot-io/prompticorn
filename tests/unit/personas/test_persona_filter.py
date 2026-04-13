"""Unit tests for PersonaFilter"""

import pytest
from pathlib import Path
from promptosaurus.personas.registry import PersonaRegistry, PersonaFilter


@pytest.fixture
def registry():
    """Loaded PersonaRegistry instance"""
    personas_yaml_path = Path("promptosaurus/personas/personas.yaml")
    return PersonaRegistry.from_yaml(personas_yaml_path)


class TestPersonaFilter:
    """Tests for PersonaFilter class"""
    
    def test_single_persona_software_engineer(self, registry):
        """Test filtering with Software Engineer persona"""
        pfilter = PersonaFilter(registry, ["software_engineer"])
        enabled = pfilter.get_enabled_agents()
        
        # Should have agents
        assert len(enabled) > 0
        
        # Should have code agent (Software Engineer needs it)
        assert "code" in enabled
        
        # Should have test agent (Software Engineer needs it)
        assert "test" in enabled
        
        # Should have all universal agents
        for universal in ["ask", "debug", "explain", "planning", "orchestrator"]:
            assert universal in enabled, f"Missing universal agent: {universal}"
    
    def test_single_persona_qa_tester(self, registry):
        """Test filtering with QA/Tester persona"""
        pfilter = PersonaFilter(registry, ["qa_tester"])
        enabled = pfilter.get_enabled_agents()
        
        # Should have test agent (QA/Tester needs it)
        assert "test" in enabled
        
        # Should NOT have code agent (QA/Tester doesn't need it per ADR-001)
        assert "code" not in enabled
        
        # Should have all universal agents
        for universal in ["ask", "debug", "explain", "planning", "orchestrator"]:
            assert universal in enabled, f"Missing universal agent: {universal}"
    
    def test_multiple_personas_union(self, registry):
        """Test filtering with multiple personas (union of agents)"""
        pfilter = PersonaFilter(registry, ["software_engineer", "qa_tester"])
        enabled = pfilter.get_enabled_agents()
        
        # Should have code agent (from Software Engineer)
        assert "code" in enabled
        
        # Should have test agent (from both)
        assert "test" in enabled
        
        # Should have all universal agents
        for universal in ["ask", "debug", "explain", "planning", "orchestrator"]:
            assert universal in enabled, f"Missing universal agent: {universal}"
    
    def test_architect_persona(self, registry):
        """Test filtering with Architect persona"""
        pfilter = PersonaFilter(registry, ["architect"])
        enabled = pfilter.get_enabled_agents()
        
        # Architect should have architect agent
        assert "architect" in enabled
        
        # Should have all universal agents
        for universal in ["ask", "debug", "explain", "planning", "orchestrator"]:
            assert universal in enabled
    
    def test_devops_persona_has_code(self, registry):
        """Test that DevOps Engineer has code agent (for IaC)"""
        pfilter = PersonaFilter(registry, ["devops_engineer"])
        enabled = pfilter.get_enabled_agents()
        
        # DevOps should have code agent (for IaC per ADR-001)
        assert "code" in enabled
        
        # DevOps should have devops agent
        assert "devops" in enabled
    
    def test_data_scientist_has_code(self, registry):
        """Test that Data Scientist has code agent (for ML code)"""
        pfilter = PersonaFilter(registry, ["data_scientist"])
        enabled = pfilter.get_enabled_agents()
        
        # Data Scientist should have code agent (for ML code per ADR-001)
        assert "code" in enabled
        
        # Data Scientist should have mlai agent
        assert "mlai" in enabled
    
    def test_empty_personas_list(self, registry):
        """Test filtering with empty personas list (should return only universal)"""
        pfilter = PersonaFilter(registry, [])
        enabled = pfilter.get_enabled_agents()
        
        # Should only have universal agents
        expected_universal = {"ask", "debug", "explain", "planning", "orchestrator"}
        assert set(enabled) == expected_universal
    
    def test_invalid_persona_id(self, registry):
        """Test filtering with invalid persona ID"""
        with pytest.raises(KeyError, match="Invalid persona"):
            PersonaFilter(registry, ["invalid_persona_id"])
    
    def test_all_personas_selected(self, registry):
        """Test filtering with all personas selected"""
        all_persona_ids = registry.list_personas()
        pfilter = PersonaFilter(registry, all_persona_ids)
        enabled = pfilter.get_enabled_agents()
        
        # Should have many agents (most/all of them)
        assert len(enabled) >= 20  # At least 20 agents enabled
        
        # Should have all primary agents
        assert "code" in enabled
        assert "test" in enabled
        assert "architect" in enabled
        assert "devops" in enabled
        assert "security" in enabled
    
    def test_persona_filter_is_subset(self, registry):
        """Test that filtered agents are always a subset or equal to all agents"""
        # Get all possible agents by selecting all personas
        all_persona_ids = registry.list_personas()
        pfilter_all = PersonaFilter(registry, all_persona_ids)
        all_enabled = set(pfilter_all.get_enabled_agents())
        
        # Single persona should be subset
        pfilter_single = PersonaFilter(registry, ["software_engineer"])
        single_enabled = set(pfilter_single.get_enabled_agents())
        
        assert single_enabled.issubset(all_enabled)
    
    def test_universal_agents_always_enabled(self, registry):
        """Test that universal agents are always enabled regardless of persona"""
        universal_agents = set(registry.get_universal_agents())
        
        # Test with different personas
        for persona_id in ["software_engineer", "qa_tester", "architect", "devops_engineer"]:
            pfilter = PersonaFilter(registry, [persona_id])
            enabled = set(pfilter.get_enabled_agents())
            
            # Universal agents should always be in enabled set
            assert universal_agents.issubset(enabled), \
                f"Universal agents not all enabled for {persona_id}"
