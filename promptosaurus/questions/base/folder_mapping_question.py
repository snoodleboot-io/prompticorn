"""Question for folder to language mappings in multi-language repositories."""

from promptosaurus.questions.base.question import Question


class FolderMappingQuestion(Question):
    """Question about folder to language mappings."""

    def __init__(self, num_folders: int = 1):
        self._num_folders = num_folders

    @property
    def key(self) -> str:
        return "folder_mapping"

    @property
    def question_text(self) -> str:
        return "Enter folder paths and their languages (one per line)"

    @property
    def explanation(self) -> str:
        return """Map each folder to its primary language.

   /frontend → typescript
   /backend → python
   /shared → go

This determines which language conventions to apply for each area."""

    @property
    def options(self) -> list[str]:
        return []

    @property
    def default(self) -> str:
        return ""

    @property
    def allow_multiple(self) -> bool:
        return False
