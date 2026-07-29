"""No workflow or skill may ship as an unfilled authoring template (PRO-138).

PRO-7 filled the 76 hollow skills; 12 workflows were left as templates and shipped
placeholder prose to users for months. This guards the whole tree so the next one
cannot be added silently.
"""

import pytest

# Placeholder prose left behind by the authoring templates. These are deliberately
# specific: a legitimate document may well contain "[optional]" or a markdown link,
# so match only the template's own wording.
TEMPLATE_MARKERS = [
    "[First Pattern]",
    "[Second Pattern]",
    "[Third Pattern]",
    "[Details about pattern]",
    "[Code or configuration examples]",
    "[When to use this pattern]",
    "[Specific use cases]",
    "[How to implement]",
    "[Pros and cons]",
    "[Practice 1]",
    "[Mistake 1 and how to avoid it]",
    "[Link to related workflow patterns]",
    "[Define key concepts and patterns]",
    "[List 4-5 pattern types with brief descriptions]",
    "[When this pattern is applicable]",
    "[Important factors to consider]",
]

# The generic sentence the template opens with. Real content states what the
# workflow is for; this states only that it covers its own description.
FILLER_OPENER = "This workflow covers comprehensive approaches to"

# The step-list template's filler body. A second, distinct hollow shape: the step
# headings are real but every body is this sentence.
FILLER_STEP_BODY = "Detailed instructions for this step."


def _content_files(root):
    return sorted(root.rglob("*.md"))


@pytest.mark.unit
class TestNoHollowContent:
    def test_no_workflow_is_an_unfilled_template(self, workflows_dir):
        hollow = {}
        for path in _content_files(workflows_dir):
            found = [m for m in TEMPLATE_MARKERS if m in path.read_text(encoding="utf-8")]
            if found:
                hollow[path.relative_to(workflows_dir).as_posix()] = found
        assert not hollow, f"unfilled workflow templates: {sorted(hollow)}"

    def test_no_skill_is_an_unfilled_template(self, skills_dir):
        hollow = {}
        for path in _content_files(skills_dir):
            found = [m for m in TEMPLATE_MARKERS if m in path.read_text(encoding="utf-8")]
            if found:
                hollow[path.relative_to(skills_dir).as_posix()] = found
        assert not hollow, f"unfilled skill templates: {sorted(hollow)}"

    def test_no_workflow_keeps_the_filler_opening_sentence(self, workflows_dir):
        """The template's generic opener restates the description and says nothing.
        Its presence means the body was never written even if the placeholder
        brackets were removed."""
        filler = [
            path.relative_to(workflows_dir).as_posix()
            for path in _content_files(workflows_dir)
            if FILLER_OPENER in path.read_text(encoding="utf-8")
        ]
        assert not filler, f"workflows still carrying the template opener: {sorted(filler)}"

    def test_no_workflow_keeps_the_filler_step_bodies(self, workflows_dir):
        """The step-list template's hollow shape: real step headings, every body
        replaced by the same filler sentence."""
        filler = [
            path.relative_to(workflows_dir).as_posix()
            for path in _content_files(workflows_dir)
            if FILLER_STEP_BODY in path.read_text(encoding="utf-8")
        ]
        assert not filler, f"workflows with unwritten step bodies: {sorted(filler)}"

    def test_every_workflow_has_both_variants(self, workflows_dir):
        missing = [
            d.name
            for d in sorted(workflows_dir.iterdir())
            if d.is_dir()
            and not (
                (d / "minimal" / "workflow.md").exists() and (d / "verbose" / "workflow.md").exists()
            )
        ]
        assert not missing, f"workflows missing a variant: {missing}"

    def test_verbose_variants_are_substantive(self, workflows_dir):
        """A verbose workflow shorter than its own frontmatter plus a heading is a
        stub by another name."""
        thin = {
            path.relative_to(workflows_dir).as_posix(): len(
                path.read_text(encoding="utf-8").splitlines()
            )
            for path in workflows_dir.rglob("verbose/workflow.md")
            if len(path.read_text(encoding="utf-8").splitlines()) < 40
        }
        assert not thin, f"verbose workflows with too little content: {thin}"
