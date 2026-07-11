"""Project-level configuration questions (language-agnostic).

These populate the project-level fields of the core conventions (commit style,
PR size, deploy target). They are asked once during ``init`` and stored under the
config ``project`` section. The ``NOT_SPECIFIED`` option maps to an empty value so
the convention renders a clear "_(not specified)_" placeholder.

Note: ``layout_style`` and ``error_handling`` are now CORE per-language questions
(stored on each language/folder spec), and ``database``/``orm`` were replaced by
the fungible backend-only ``databases``/``data_access`` questions.
"""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class CommitStyleQuestion(Question):
    """Project commit-message style."""

    @property
    def key(self) -> str:
        return "project_commit_style"

    @property
    def question_text(self) -> str:
        return "Which commit message style does this project follow?"

    @property
    def explanation(self) -> str:
        return "How commit messages are formatted (affects commits agents author)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Conventional Commits", "Free-form"]

    @property
    def default(self) -> str:
        return NOT_SPECIFIED


class PrSizeQuestion(Question):
    """Project soft PR-size limit (lines changed)."""

    @property
    def key(self) -> str:
        return "project_pr_size"

    @property
    def question_text(self) -> str:
        return "What soft PR size limit (lines changed) should agents target?"

    @property
    def explanation(self) -> str:
        return "A soft cap on PR size to keep changes reviewable."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "200", "400", "800"]

    @property
    def default(self) -> str:
        return NOT_SPECIFIED


class DeployTargetQuestion(Question):
    """Project deployment target."""

    @property
    def key(self) -> str:
        return "project_deploy_target"

    @property
    def question_text(self) -> str:
        return "What is the primary deployment target?"

    @property
    def explanation(self) -> str:
        return "Where the project deploys (informs infra/devops guidance)."

    @property
    def options(self) -> list[str]:
        return [
            NOT_SPECIFIED,
            "AWS Lambda",
            "AWS ECS",
            "Kubernetes",
            "GKE",
            "Vercel",
            "Heroku",
            "On-prem",
        ]

    @property
    def default(self) -> str:
        return NOT_SPECIFIED


def get_project_questions() -> list[Question]:
    """Return the ordered list of project-level questions.

    The ``key`` of each question is ``project_<field>``; the ``<field>`` portion is
    the key used in the config ``project`` section.

    Returns:
        List of Question instances.
    """
    return [
        CommitStyleQuestion(),
        PrSizeQuestion(),
        DeployTargetQuestion(),
    ]
