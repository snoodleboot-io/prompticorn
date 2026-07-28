"""Question for selecting the Objective-C variant (PRO-136)."""

from prompticorn.questions.base.question import Question


class ObjcVersionQuestion(Question):
    """Question handler for Objective-C variant selection."""

    @property
    def key(self) -> str:
        return "objc_version"

    @property
    def question_text(self) -> str:
        return "What Objective-C variant?"

    @property
    def explanation(self) -> str:
        return "Select the Objective-C variant your project targets."

    @property
    def options(self) -> list[str]:
        return ["2.0", "1.0"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "2.0": "Objective-C 2.0 - Modern: properties, ARC, blocks, fast enumeration",
            "1.0": "Objective-C 1.0 - Legacy runtime, manual retain/release",
        }

    @property
    def default(self) -> str:
        return "2.0"

    config_key = "runtime"
