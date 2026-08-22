"""The typed failures verification can raise (PRO-115)."""

import unittest

from prompticorn.verify import OutputTamperedError, UnknownOutputError, VerificationError


class TestOutputTamperedError(unittest.TestCase):
    def test_it_carries_what_a_caller_needs_to_act(self) -> None:
        error = OutputTamperedError(".claude/agents/code.md", "a" * 64, "b" * 64)

        self.assertEqual(error.path, ".claude/agents/code.md")
        self.assertEqual(error.expected, "a" * 64)
        self.assertEqual(error.actual, "b" * 64)

    def test_the_message_names_the_file_and_both_digests(self) -> None:
        message = str(OutputTamperedError(".claude/agents/code.md", "a" * 64, "b" * 64))

        self.assertIn(".claude/agents/code.md", message)
        self.assertIn("a" * 12, message)
        self.assertIn("b" * 12, message)

    def test_the_message_says_what_to_do(self) -> None:
        self.assertIn("source", str(OutputTamperedError("x.md", "a" * 64, "b" * 64)))

    def test_it_is_a_verification_error(self) -> None:
        self.assertIsInstance(OutputTamperedError("x.md", "a", "b"), VerificationError)


class TestUnknownOutputError(unittest.TestCase):
    def test_it_carries_the_path(self) -> None:
        self.assertEqual(UnknownOutputError(".claude/agents/rogue.md").path, ".claude/agents/rogue.md")

    def test_the_message_offers_both_resolutions(self) -> None:
        message = str(UnknownOutputError(".claude/agents/rogue.md"))

        self.assertIn("Delete", message)
        self.assertIn("lock", message)

    def test_it_is_a_verification_error(self) -> None:
        self.assertIsInstance(UnknownOutputError("x.md"), VerificationError)


if __name__ == "__main__":
    unittest.main()
