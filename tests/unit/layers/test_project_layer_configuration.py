"""A malformed configuration override must stop the build (PRO-165).

The old failure mode was not a crash, it was a success. A project layer supplying
``personas/personas.yaml`` that said ``personas: [oops`` — or ``personas: {}`` —
produced a registry that knew no personas, a filter that matched nothing, a
``KeyError`` caught by ``except Exception``, and a build that emitted all 26 agents
and 88 skills where 15 and 51 were asked for. Exit 0, one ``⚠`` line in an action
list of ninety.

So these tests assert two things together: that the command fails, and that it
does not write the wrong output. Either alone is satisfied by a build that is
still broken.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from prompticorn.cli import cli
from prompticorn.layers import PROJECT_LAYER
from prompticorn.store import store_paths

MANIFEST = {
    "version": "2.0",
    "repository": {"type": "single-language"},
    "spec": {"language": "python"},
    "variant": "minimal",
    "active_personas": ["software_engineer"],
    "ai_tool": "claude",
}

# Each is a plausible thing to commit and each used to produce a clean exit.
# `[oops` is a typo; `{}` and `- one` are somebody starting the file and getting
# the shape wrong; a missing section is somebody renaming a key.
PERSONA_OVERRIDES = {
    "unparseable": "personas: [oops\n",
    "empty-personas": "personas: {}\n",
    "sequence-personas": "personas:\n  - software_engineer\n",
    "no-personas-section": "roles:\n  software_engineer: {}\n",
    "non-mapping-persona": "personas:\n  software_engineer: 3\n",
}


def run(*args):
    return CliRunner().invoke(cli, list(args))


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))
    monkeypatch.delenv("PROMPTICORN_USER_LAYER", raising=False)
    root = tmp_path / "project"
    (root / ".prompticorn").mkdir(parents=True)
    (root / ".prompticorn" / ".prompticorn.yaml").write_text(
        yaml.safe_dump(MANIFEST), encoding="utf-8"
    )
    monkeypatch.chdir(root)
    return root


def override_personas(project: Path, text: str) -> Path:
    path = project / ".prompticorn" / "content" / "personas" / "personas.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def override_configuration(project: Path, name: str, text: str) -> Path:
    path = project / ".prompticorn" / "content" / "configurations" / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize("text", PERSONA_OVERRIDES.values(), ids=list(PERSONA_OVERRIDES))
class TestAMalformedPersonaOverride:
    def test_the_build_fails(self, project: Path, text: str):
        override_personas(project, text)

        assert run("build").exit_code != 0

    def test_nothing_is_emitted(self, project: Path, text: str):
        """The failure has to come before the writing, or a broken override leaves
        a half-built tree that the next `verify` reports as hand edits."""
        override_personas(project, text)

        run("build")

        assert not (project / ".claude").exists()

    def test_the_message_names_the_file_and_the_layer(self, project: Path, text: str):
        path = override_personas(project, text)

        result = run("build")

        assert str(path) in result.output
        assert PROJECT_LAYER in result.output


class TestAMalformedAgentSkillMappingOverride:
    """Same class of failure through the other configuration a layer can supply.
    Its old path was different and no better: a YAMLError raised lazily from
    inside the per-agent build loop, caught there as `✗ Failed to build {agent}`
    once per agent, and a build that still exited 0."""

    def test_an_unparseable_mapping_fails_the_build(self, project: Path):
        override_configuration(project, "agent_skill_mapping", "code: [oops\n")

        assert run("build").exit_code != 0

    def test_an_empty_mapping_fails_the_build(self, project: Path):
        """`{}` parses. It used to load as "no agent has any skills", and every
        agent was emitted with an empty skills table and no SKILL.md beside it."""
        override_configuration(project, "agent_skill_mapping", "{}\n")

        assert run("build").exit_code != 0

    def test_the_message_names_the_file_and_the_layer(self, project: Path):
        path = override_configuration(project, "agent_skill_mapping", "code: 3\n")

        result = run("build")

        assert str(path) in result.output
        assert PROJECT_LAYER in result.output


class TestAValidOverrideStillWorks:
    """The narrowing must not have made every override a failure."""

    def test_a_well_formed_persona_override_changes_what_is_built(self, project: Path):
        override_personas(
            project,
            yaml.safe_dump(
                {
                    "universal_agents": ["ask"],
                    "personas": {"software_engineer": {"primary_agents": ["code"]}},
                }
            ),
        )

        result = run("build")

        assert result.exit_code == 0, result.output
        built = sorted(path.name for path in (project / ".claude" / "agents").iterdir())
        assert built == ["ask-agent.md", "code-agent.md"]

    def test_a_selection_naming_an_unknown_persona_is_still_tolerated(self, project: Path):
        """Deliberately unchanged behaviour (PRO-153 owns it). A selection that
        does not match otherwise-valid data still builds unfiltered with a
        warning — narrowing the catch to KeyError kept exactly that, and only
        that."""
        (project / ".prompticorn" / ".prompticorn.yaml").write_text(
            yaml.safe_dump({**MANIFEST, "active_personas": ["no_such_role"]}), encoding="utf-8"
        )

        result = run("build")

        assert result.exit_code == 0, result.output
        assert "Persona filtering failed" in result.output
