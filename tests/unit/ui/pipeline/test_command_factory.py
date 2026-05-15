"""Tests for CommandFactory digit buffering and multi-select commit behavior."""

import pytest

from prompticorn.ui.commands.confirm import ConfirmCommand
from prompticorn.ui.commands.navigate import NavigateCommand
from prompticorn.ui.commands.noop import NoOpCommand
from prompticorn.ui.commands.quit import QuitCommand
from prompticorn.ui.commands.select import SelectCommand
from prompticorn.ui.domain.events import InputEvent, InputEventType
from prompticorn.ui.pipeline.command_factory import CommandFactory


def num(value: int) -> InputEvent:
    return InputEvent(event_type=InputEventType.NUMBER, value=value)


def separator() -> InputEvent:
    return InputEvent(event_type=InputEventType.SEPARATOR)


def timeout() -> InputEvent:
    return InputEvent(event_type=InputEventType.TIMEOUT)


def enter() -> InputEvent:
    return InputEvent(event_type=InputEventType.ENTER)


def up() -> InputEvent:
    return InputEvent(event_type=InputEventType.UP)


class TestSingleSelect:
    """Single-select: digits accumulate and emit SelectCommand immediately."""

    def test_single_digit_selects_immediately(self):
        factory = CommandFactory()
        cmd = factory.create_command(num(3))
        assert isinstance(cmd, SelectCommand)
        assert cmd.number == 3

    def test_two_digits_select_two_digit_number(self):
        factory = CommandFactory()
        factory.create_command(num(1))
        cmd = factory.create_command(num(2))
        assert isinstance(cmd, SelectCommand)
        assert cmd.number == 12

    def test_non_digit_clears_buffer(self):
        factory = CommandFactory()
        factory.create_command(num(1))
        factory.create_command(enter())  # clears buffer
        cmd = factory.create_command(num(5))
        assert isinstance(cmd, SelectCommand)
        assert cmd.number == 5  # not 15


class TestMultiSelectDigitBuffering:
    """Multi-select: digits buffer silently; commit on separator, timeout, or non-digit."""

    def test_single_digit_returns_noop(self):
        factory = CommandFactory()
        cmd = factory.create_command(num(3), allow_multiple=True)
        assert isinstance(cmd, NoOpCommand)

    def test_two_digits_both_return_noop(self):
        factory = CommandFactory()
        cmd1 = factory.create_command(num(1), allow_multiple=True)
        cmd2 = factory.create_command(num(0), allow_multiple=True)
        assert isinstance(cmd1, NoOpCommand)
        assert isinstance(cmd2, NoOpCommand)

    def test_space_commits_buffered_digits(self):
        factory = CommandFactory()
        factory.create_command(num(1), allow_multiple=True)
        factory.create_command(num(0), allow_multiple=True)
        cmd = factory.create_command(separator(), allow_multiple=True)
        assert isinstance(cmd, SelectCommand)
        assert cmd.number == 10

    def test_comma_commits_buffered_digits(self):
        factory = CommandFactory()
        factory.create_command(num(1), allow_multiple=True)
        factory.create_command(num(2), allow_multiple=True)
        cmd = factory.create_command(separator(), allow_multiple=True)
        assert isinstance(cmd, SelectCommand)
        assert cmd.number == 12

    def test_timeout_commits_buffered_digits(self):
        factory = CommandFactory()
        factory.create_command(num(1), allow_multiple=True)
        factory.create_command(num(1), allow_multiple=True)
        cmd = factory.create_command(timeout(), allow_multiple=True)
        assert isinstance(cmd, SelectCommand)
        assert cmd.number == 11

    def test_separator_with_empty_buffer_returns_noop(self):
        factory = CommandFactory()
        cmd = factory.create_command(separator(), allow_multiple=True)
        assert isinstance(cmd, NoOpCommand)

    def test_timeout_with_empty_buffer_returns_noop(self):
        factory = CommandFactory()
        cmd = factory.create_command(timeout(), allow_multiple=True)
        assert isinstance(cmd, NoOpCommand)

    def test_non_digit_clears_buffer(self):
        factory = CommandFactory()
        factory.create_command(num(1), allow_multiple=True)
        factory.create_command(up(), allow_multiple=True)  # clears buffer
        cmd = factory.create_command(separator(), allow_multiple=True)
        assert isinstance(cmd, NoOpCommand)  # buffer was already cleared

    def test_enter_after_digits_clears_buffer_and_confirms(self):
        factory = CommandFactory()
        factory.create_command(num(1), allow_multiple=True)
        cmd = factory.create_command(enter(), allow_multiple=True)
        assert isinstance(cmd, ConfirmCommand)

    def test_single_digit_via_separator(self):
        factory = CommandFactory()
        factory.create_command(num(5), allow_multiple=True)
        cmd = factory.create_command(separator(), allow_multiple=True)
        assert isinstance(cmd, SelectCommand)
        assert cmd.number == 5

    def test_buffer_resets_after_commit(self):
        factory = CommandFactory()
        factory.create_command(num(1), allow_multiple=True)
        factory.create_command(num(0), allow_multiple=True)
        factory.create_command(separator(), allow_multiple=True)  # commits 10
        # Now type another number
        factory.create_command(num(3), allow_multiple=True)
        cmd = factory.create_command(separator(), allow_multiple=True)
        assert isinstance(cmd, SelectCommand)
        assert cmd.number == 3  # not 103


class TestMultiSelectFallback:
    """Multi-select fallback: NUMBER events with value > 9 are already full integers."""

    def test_large_value_selects_immediately(self):
        factory = CommandFactory()
        cmd = factory.create_command(num(10), allow_multiple=True)
        assert isinstance(cmd, SelectCommand)
        assert cmd.number == 10

    def test_large_value_clears_buffer(self):
        factory = CommandFactory()
        factory.create_command(num(1), allow_multiple=True)  # buffered
        cmd = factory.create_command(num(15), allow_multiple=True)  # full integer from fallback
        assert isinstance(cmd, SelectCommand)
        assert cmd.number == 15
