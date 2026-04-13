"""Repository types and configuration values."""

from enum import Enum


class RepositoryTypes(str, Enum):
    """Repository type enumeration.

    This enum provides type-safe constants for the three supported repository types.
    Inherits from str to maintain backward compatibility with string comparisons.

    Usage:
        repo_type = RepositoryTypes.SINGLE
        if repo_type == "single-language":  # Still works due to str inheritance
            ...
    """

    SINGLE = "single-language"
    MULTI_MONOREPO = "multi-language-monorepo"
    MIXED = "mixed-collocation"

    @classmethod
    def all(cls) -> list[str]:
        """Get list of all repository types.

        Returns:
            List of all valid repository type strings.
        """
        return [member.value for member in cls]

    @classmethod
    def from_string(cls, value: str) -> "RepositoryTypes":
        """Convert string to RepositoryTypes enum member.

        Args:
            value: Repository type string.

        Returns:
            RepositoryTypes enum member.

        Raises:
            ValueError: If value is not a valid repository type.
        """
        try:
            return cls(value)
        except ValueError:
            valid_values = ", ".join([t.value for t in cls])
            raise ValueError(
                f"Invalid repository type: {value}. Valid types: {valid_values}"
            ) from None

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a string is a valid repository type.

        Args:
            value: String to check.

        Returns:
            True if value is a valid repository type, False otherwise.
        """
        try:
            cls(value)
            return True
        except ValueError:
            return False
