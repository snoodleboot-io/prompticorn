# Lua version question

from promptosaurus.questions.base.question import Question


class LuaVersionQuestion(Question):
    """Question handler for Lua version."""

    @property
    def key(self) -> str:
        return "lua_version"

    @property
    def question_text(self) -> str:
        return "What Lua version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Lua version affects language features and performance.

- Lua 5.4 has significant performance improvements and new features
- Lua is lightweight and embeddable, popular for game scripting
- Version affects compatibility with libraries and LuaJIT"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["5.4", "5.3", "5.2", "5.1", "LuaJIT 2.1"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "5.4"

    config_key = "runtime"
