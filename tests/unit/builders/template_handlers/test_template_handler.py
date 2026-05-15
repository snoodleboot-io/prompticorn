import unittest

from prompticorn.builders.template_handlers.template_handler import TemplateHandler


class ConcreteHandlerForTesting(TemplateHandler):
    """Concrete subclass that delegates to parent to trigger NotImplementedError."""

    def can_handle(self, variable_name: str) -> bool:
        return super().can_handle(variable_name)

    def handle(self, variable_name: str, config: dict) -> str:
        return super().handle(variable_name, config)


class TestTemplateHandler(unittest.TestCase):
    """Test cases for the TemplateHandler abstract base class."""

    def test_can_handle_raises_not_implemented(self):
        """Test that can_handle raises NotImplementedError."""
        handler = ConcreteHandlerForTesting()
        with self.assertRaises(NotImplementedError):
            handler.can_handle("test_variable")

    def test_handle_raises_not_implemented(self):
        """Test that handle raises NotImplementedError."""
        handler = ConcreteHandlerForTesting()
        with self.assertRaises(NotImplementedError):
            handler.handle("test_variable", {})


if __name__ == "__main__":
    unittest.main()
