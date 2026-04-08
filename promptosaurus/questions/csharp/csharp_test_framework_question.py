# C# test framework question

from promptosaurus.questions.base.question import Question


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
