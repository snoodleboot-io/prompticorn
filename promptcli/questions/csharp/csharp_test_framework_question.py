# C# test framework question

from promptcli.questions.base.question import Question


class CSharpTestFrameworkQuestion(Question):
    """Question for C# test framework selection."""

    @property
    def key(self) -> str:
        return "csharp_test_framework"

    @property
    def question_text(self) -> str:
        return "What testing framework do you want to use?"

    @property
    def explanation(self) -> str:
        return """Test framework affects how tests are written, organized, and executed:
- xunit: Modern, extensible, community-driven, default for .NET Core
- nunit: Mature, flexible, strong constraint model, widely used
- mstest: Microsoft's framework, integrates well with Visual Studio"""

    @property
    def options(self) -> list[str]:
        return ["xunit", "nunit", "mstest"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "xunit": "Modern standard - extensible, community-driven, default for .NET Core, recommended",
            "nunit": "Mature and flexible - strong constraint model, attribute-based, widely adopted",
            "mstest": "Microsoft framework - Visual Studio integration, data-driven tests, MSTest V2",
        }

    @property
    def default(self) -> str:
        return "xunit"
