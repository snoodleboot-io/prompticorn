"""Tests for the claude.ai / Claude Desktop skills packager (PRO-10)."""

import zipfile
from pathlib import Path

import pytest

from prompticorn.skills_packager import package_skills


def _make_skill(root: Path, name: str, extra: dict[str, str] | None = None) -> Path:
    d = root / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Does {name}\n---\n\n# Body\n", encoding="utf-8"
    )
    for rel, content in (extra or {}).items():
        target = d / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return d


@pytest.mark.unit
class TestSkillsPackager:
    def test_packages_folder_at_zip_root(self, tmp_path):
        src = tmp_path / "skills"
        _make_skill(src, "code-review")
        (out := tmp_path / "out").mkdir()
        results = package_skills(src, out)

        assert [r.name for r in results] == ["code-review"]
        zip_path = out / "code-review.zip"
        assert results[0].zip_path == zip_path
        # The accepted form: the folder is the top-level entry, SKILL.md inside it.
        assert zipfile.ZipFile(zip_path).namelist() == ["code-review/SKILL.md"]

    def test_one_skill_per_zip(self, tmp_path):
        src = tmp_path / "skills"
        _make_skill(src, "alpha")
        _make_skill(src, "beta")
        results = package_skills(src, tmp_path / "out")
        assert {r.name for r in results} == {"alpha", "beta"}
        assert (tmp_path / "out" / "alpha.zip").exists()
        assert (tmp_path / "out" / "beta.zip").exists()
        assert zipfile.ZipFile(tmp_path / "out" / "alpha.zip").namelist() == ["alpha/SKILL.md"]

    def test_bundled_resources_are_included_under_the_folder(self, tmp_path):
        src = tmp_path / "skills"
        _make_skill(src, "with-res", extra={"resources/data.txt": "x"})
        package_skills(src, out := tmp_path / "out")
        names = zipfile.ZipFile(out / "with-res.zip").namelist()
        assert set(names) == {"with-res/SKILL.md", "with-res/resources/data.txt"}

    @pytest.mark.parametrize(
        ("name", "reason_fragment"),
        [
            ("claude-helper", "reserved word 'claude'"),
            ("anthropic-tool", "reserved word 'anthropic'"),
            ("Bad_Name", "lowercase"),
            ("has space", "lowercase"),
        ],
    )
    def test_invalid_names_are_skipped_not_zipped(self, tmp_path, name, reason_fragment):
        src = tmp_path / "skills"
        _make_skill(src, name)
        (results,) = package_skills(src, out := tmp_path / "out")
        assert not results.ok
        assert reason_fragment in results.skipped_reason
        assert not (out / f"{name}.zip").exists()

    def test_valid_and_invalid_mix(self, tmp_path):
        src = tmp_path / "skills"
        _make_skill(src, "good-skill")
        _make_skill(src, "claude-thing")
        results = package_skills(src, tmp_path / "out")
        ok = [r for r in results if r.ok]
        skipped = [r for r in results if not r.ok]
        assert [r.name for r in ok] == ["good-skill"]
        assert [r.name for r in skipped] == ["claude-thing"]

    def test_missing_source_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="does not exist"):
            package_skills(tmp_path / "nope", tmp_path / "out")

    def test_empty_source_raises(self, tmp_path):
        (src := tmp_path / "skills").mkdir()
        (src / "not-a-skill").mkdir()  # no SKILL.md
        with pytest.raises(FileNotFoundError, match="no <name>/SKILL.md"):
            package_skills(src, tmp_path / "out")

    def test_packaged_zip_contains_valid_agent_skill_frontmatter(self, tmp_path):
        src = tmp_path / "skills"
        _make_skill(src, "real-skill")
        package_skills(src, out := tmp_path / "out")
        with zipfile.ZipFile(out / "real-skill.zip") as zf:
            body = zf.read("real-skill/SKILL.md").decode()
        assert body.startswith("---\n")
        assert "name: real-skill" in body
        assert "description:" in body
