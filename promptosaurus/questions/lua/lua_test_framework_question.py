# Lua test framework question

from promptosaurus.questions.base.question import Question


class LuaTestFrameworkQuestion(Question):
    """Question handler for Lua test framework."""

    @property
    def key(self) -> str:
        return "lua_test_framework"

    @property
    def question_text(self) -> str:
        return "What test framework do you want to use for Lua?"

    @property
    def explanation(self) -> str:
        return """Test frameworks provide structure for testing Lua code.

- Busted is the most popular testing framework for Lua
- It provides expressive assertions and test organization
- Works with Lua 5.1+ and LuaJIT"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["busted", "luaunit", "telescope"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "busted"

    config_key = "test_framework"
