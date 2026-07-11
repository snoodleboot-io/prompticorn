"""Database selection question for backend folders.

This is a FUNGIBLE, BACKEND-ONLY question. A backend folder may persist data in
several datastores, so it is multi-select. Frontend folders never see it.
"""

from prompticorn.questions.base.question import Question


class DatabasesQuestion(Question):
    """Databases a backend folder uses - multi-select, backend-only.

    This is a FUNGIBLE question - asked for each backend folder. A single
    folder may talk to several datastores (e.g. PostgreSQL for relational data
    plus Redis for caching), so multiple selections are allowed.
    """

    @property
    def key(self) -> str:
        return "databases"

    @property
    def question_text(self) -> str:
        return "Which database(s) does this folder use?"

    @property
    def explanation(self) -> str:
        return (
            "The datastore(s) this folder reads from and writes to. Documented in the "
            "core conventions so agents target the right persistence layer. Select all "
            "that apply."
        )

    @property
    def options(self) -> list[str]:
        return [
            "PostgreSQL",
            "MySQL",
            "MariaDB",
            "SQLite",
            "MongoDB",
            "Cassandra",
            "DynamoDB",
            "Firestore",
            "Redis",
            "Memcached",
            "Elasticsearch",
            "BigQuery",
            "Snowflake",
        ]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "PostgreSQL": "Feature-rich relational database with strong JSON and extension support",
            "MySQL": "Widely deployed relational database, simple and fast for common workloads",
            "MariaDB": "Community-driven MySQL fork with additional storage engines",
            "SQLite": "Embedded, zero-config relational database for local or single-node use",
            "MongoDB": "Document database for flexible, schema-less JSON-like data",
            "Cassandra": "Wide-column store for high write throughput and horizontal scale",
            "DynamoDB": "Managed AWS key-value / document store with predictable performance",
            "Firestore": "Managed GCP document database with realtime sync",
            "Redis": "In-memory key-value store for caching, queues, and ephemeral data",
            "Memcached": "Simple high-performance in-memory cache",
            "Elasticsearch": "Distributed search and analytics engine over JSON documents",
            "BigQuery": "Serverless GCP data warehouse for large-scale analytics",
            "Snowflake": "Cloud data warehouse with separated storage and compute",
        }

    @property
    def default(self) -> str:
        return "PostgreSQL"

    @property
    def default_indices(self) -> set[int]:
        """Default selection for multi-select: PostgreSQL (0)."""
        return {0}

    @property
    def allow_multiple(self) -> bool:
        """A folder may use several datastores."""
        return True
