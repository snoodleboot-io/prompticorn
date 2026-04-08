"""Repository types and configuration values."""


class RepositoryTypes:
    SINGLE = "single-language"
    MULTI_MONOREPO = "multi-language-monorepo"
    MIXED = "mixed-collocation"

    @classmethod
    def all(cls):
        return [cls.SINGLE, cls.MULTI_MONOREPO, cls.MIXED]


REPO_TYPES = RepositoryTypes.all()
