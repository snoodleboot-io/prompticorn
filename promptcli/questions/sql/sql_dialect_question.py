# SQL dialect question

from promptcli.questions.base.question import Question


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
        return ["postgresql", "mysql", "sqlite", "sqlserver"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "postgresql": "PostgreSQL - most feature-rich, standards-compliant, recommended",
            "mysql": "MySQL - widely used, good performance",
            "sqlite": "SQLite - lightweight, serverless, embedded",
            "sqlserver": "SQL Server - Microsoft enterprise database",
        }

    @property
    def default(self) -> str:
        return "postgresql"
