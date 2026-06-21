"""Project-level configuration questions (language-agnostic).

These populate the project-level fields of the core conventions (database, ORM,
commit style, PR size, deploy target). They are asked once during ``init`` and
stored under the config ``project`` section. The ``NOT_SPECIFIED`` option maps to
an empty value so the convention renders a clear "_(not specified)_" placeholder.
"""

from prompticorn.questions.base.question import Question

NOT_SPECIFIED = "Not specified"


class DatabaseQuestion(Question):
    """Project database selection."""

    @property
    def key(self) -> str:
        return "project_database"

    @property
    def question_text(self) -> str:
        return "Which database does this project use?"

    @property
    def explanation(self) -> str:
        return "The primary datastore. Documented in the core conventions for all agents."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "PostgreSQL", "MySQL", "SQLite", "MongoDB", "DynamoDB", "Redis"]

    @property
    def default(self) -> str:
        return NOT_SPECIFIED


class OrmQuestion(Question):
    """Project ORM / query layer selection."""

    @property
    def key(self) -> str:
        return "project_orm"

    @property
    def question_text(self) -> str:
        return "Which ORM / query layer does this project use?"

    @property
    def explanation(self) -> str:
        return "The data-access layer agents should use for queries and models."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "SQLAlchemy", "Prisma", "Django ORM", "GORM", "TypeORM", "Raw SQL"]

    @property
    def default(self) -> str:
        return NOT_SPECIFIED


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


class LayoutStyleQuestion(Question):
    """Source-tree layout style (flat vs src)."""

    @property
    def key(self) -> str:
        return "project_layout_style"

    @property
    def question_text(self) -> str:
        return "Which source-tree layout should the conventions document?"

    @property
    def explanation(self) -> str:
        return (
            "flat: package/modules at the repo root (idiomatic default).\n"
            "src: sources nested under a src/ directory."
        )

    @property
    def options(self) -> list[str]:
        return ["flat", "src"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "flat": "Package/modules at the repo root (recommended default).",
            "src": "Sources nested under a src/ directory.",
        }

    @property
    def default(self) -> str:
        return "flat"


class ErrorHandlingQuestion(Question):
    """Project error-handling pattern."""

    @property
    def key(self) -> str:
        return "project_error_handling"

    @property
    def question_text(self) -> str:
        return "What error-handling pattern does this project follow?"

    @property
    def explanation(self) -> str:
        return "How errors are surfaced and handled (documented in the core conventions)."

    @property
    def options(self) -> list[str]:
        return [NOT_SPECIFIED, "Exceptions", "Result type", "Error values / codes"]

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
        LayoutStyleQuestion(),
        DatabaseQuestion(),
        OrmQuestion(),
        ErrorHandlingQuestion(),
        CommitStyleQuestion(),
        PrSizeQuestion(),
        DeployTargetQuestion(),
    ]
