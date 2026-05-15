# SQL dialect question

from prompticorn.questions.base.question import Question


class SqlDialectQuestion(Question):
    """Question handler for SQL dialect."""

    @property
    def key(self) -> str:
        return "sql_dialect"

    @property
    def question_text(self) -> str:
        return "What SQL dialect do you want to target?"

    @property
    def explanation(self) -> str:
        return """SQL dialects have different syntax and features.

- Different databases support different SQL features and syntax
- Dialect affects query syntax, functions, and data types
- Choose the dialect matching your target database"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["PostgreSQL", "MySQL", "SQLite", "SQL Server", "Oracle"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "PostgreSQL"

    config_key = "sql_dialect"
