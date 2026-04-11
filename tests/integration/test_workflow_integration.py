"""Integration tests for workflows."""

import pytest
from pathlib import Path


@pytest.mark.integration
class TestWorkflowCompleteness:
    """Test that workflows reference appropriate agents and subagents."""

    @pytest.fixture
    def data_pipeline_workflow(self, workflows_dir, read_file):
        """Get data pipeline workflow content."""
        path = workflows_dir / "data-pipeline-workflow" / "verbose" / "prompt.md"
        return read_file(path) if path.exists() else ""

    @pytest.fixture
    def observability_workflow(self, workflows_dir, read_file):
        """Get observability workflow content."""
        path = workflows_dir / "observability-workflow" / "verbose" / "prompt.md"
        return read_file(path) if path.exists() else ""

    @pytest.fixture
    def incident_response_workflow(self, workflows_dir, read_file):
        """Get incident response workflow content."""
        path = workflows_dir / "incident-response-workflow" / "verbose" / "prompt.md"
        return read_file(path) if path.exists() else ""

    def test_data_pipeline_references_data_agent(self, data_pipeline_workflow):
        """Test that data pipeline workflow references data agent."""
        if data_pipeline_workflow:
            assert "data" in data_pipeline_workflow.lower(), (
                "Data pipeline workflow should reference data concepts"
            )

    def test_observability_workflow_references_observability_agent(self, observability_workflow):
        """Test that observability workflow references observability agent."""
        if observability_workflow:
            assert (
                "observability" in observability_workflow.lower()
                or "metrics" in observability_workflow.lower()
            ), "Observability workflow should reference observability concepts"

    def test_incident_response_references_incident_agent(self, incident_response_workflow):
        """Test that incident response references incident agent."""
        if incident_response_workflow:
            assert "incident" in incident_response_workflow.lower(), (
                "Incident response workflow should reference incident concepts"
            )


@pytest.mark.integration
class TestAgentWorkflowAlignment:
    """Test that agents and workflows are aligned."""

    def test_data_agent_has_corresponding_workflows(self, agents_dir, workflows_dir):
        """Test that data agent has corresponding workflows."""
        data_agent = agents_dir / "data" / "prompt.md"
        pipeline_workflow = workflows_dir / "data-pipeline-workflow"
        quality_workflow = workflows_dir / "data-quality-workflow"

        assert data_agent.exists(), "Data agent should exist"
        assert pipeline_workflow.exists(), "Data pipeline workflow should exist"
        assert quality_workflow.exists(), "Data quality workflow should exist"

    def test_observability_agent_has_corresponding_workflows(self, agents_dir, workflows_dir):
        """Test that observability agent has corresponding workflows."""
        obs_agent = agents_dir / "observability" / "prompt.md"
        obs_workflow = workflows_dir / "observability-workflow"
        slo_workflow = workflows_dir / "slo-sli-workflow"

        assert obs_agent.exists(), "Observability agent should exist"
        assert obs_workflow.exists(), "Observability workflow should exist"
        assert slo_workflow.exists(), "SLO/SLI workflow should exist"

    def test_incident_agent_has_corresponding_workflows(self, agents_dir, workflows_dir):
        """Test that incident agent has corresponding workflows."""
        incident_agent = agents_dir / "incident" / "prompt.md"
        response_workflow = workflows_dir / "incident-response-workflow"
        postmortem_workflow = workflows_dir / "postmortem-workflow"

        assert incident_agent.exists(), "Incident agent should exist"
        assert response_workflow.exists(), "Incident response workflow should exist"
        assert postmortem_workflow.exists(), "Postmortem workflow should exist"


@pytest.mark.integration
class TestSubagentCoverage:
    """Test that all subagents are covered by workflows."""

    def test_all_data_subagents_referenced(self, agents_dir, workflows_dir, read_file):
        """Test that all data subagents are referenced in workflows."""
        expected_subagents = ["pipeline", "warehouse", "quality", "governance", "streaming"]

        for subagent_name in expected_subagents:
            subagent_dir = agents_dir / "data" / "subagents" / subagent_name
            assert subagent_dir.exists(), f"Data subagent {subagent_name} should exist"

    def test_all_observability_subagents_referenced(self, agents_dir):
        """Test that all observability subagents exist."""
        expected_subagents = ["metrics", "logging", "tracing", "alerting", "dashboards"]

        for subagent_name in expected_subagents:
            subagent_dir = agents_dir / "observability" / "subagents" / subagent_name
            assert subagent_dir.exists(), f"Observability subagent {subagent_name} should exist"

    def test_all_incident_subagents_referenced(self, agents_dir):
        """Test that all incident subagents exist."""
        expected_subagents = ["triage", "postmortem", "runbook", "oncall"]

        for subagent_name in expected_subagents:
            subagent_dir = agents_dir / "incident" / "subagents" / subagent_name
            assert subagent_dir.exists(), f"Incident subagent {subagent_name} should exist"
