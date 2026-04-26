"""Tests for curses-based input provider."""

import curses
from unittest.mock import Mock

from promptosaurus.ui.domain.events import InputEventType
from promptosaurus.ui.input.curses_provider import CursesInputProvider


class TestCursesInputProvider:
    """Tests for CursesInputProvider."""

    def test_parse_key_enter(self):
        """Test parsing Enter key."""
        event = CursesInputProvider._parse_key(ord("\n"))
        assert event.event_type == InputEventType.ENTER

    def test_parse_key_quit_q(self):
        """Test parsing 'q' key for quit."""
        event = CursesInputProvider._parse_key(ord("q"))
        assert event.event_type == InputEventType.QUIT

    def test_parse_key_quit_Q(self):
        """Test parsing 'Q' key for quit."""
        event = CursesInputProvider._parse_key(ord("Q"))
        assert event.event_type == InputEventType.QUIT

    def test_parse_key_ctrl_c(self):
        """Test parsing Ctrl+C for quit."""
        event = CursesInputProvider._parse_key(ord("\x03"))
        assert event.event_type == InputEventType.QUIT

    def test_parse_key_number(self):
        """Test parsing number keys."""
        for i in range(10):
            event = CursesInputProvider._parse_key(ord(str(i)))
            assert event.event_type == InputEventType.NUMBER
            assert event.value == i

    def test_parse_key_letter_a(self):
        """Test parsing 'a' key for selection 0."""
        event = CursesInputProvider._parse_key(ord("a"))
        assert event.event_type == InputEventType.NUMBER
        assert event.value == 0

    def test_parse_key_letter_b(self):
        """Test parsing 'b' key for selection 1."""
        event = CursesInputProvider._parse_key(ord("b"))
        assert event.event_type == InputEventType.NUMBER
        assert event.value == 1

    def test_parse_key_letter_c(self):
        """Test parsing 'c' key for selection 2."""
        event = CursesInputProvider._parse_key(ord("c"))
        assert event.event_type == InputEventType.NUMBER
        assert event.value == 2

    def test_parse_key_letter_d(self):
        """Test parsing 'd' key for selection 3."""
        event = CursesInputProvider._parse_key(ord("d"))
        assert event.event_type == InputEventType.NUMBER
        assert event.value == 3

    def test_parse_key_letter_A_uppercase(self):
        """Test parsing 'A' key for selection 0."""
        event = CursesInputProvider._parse_key(ord("A"))
        assert event.event_type == InputEventType.NUMBER
        assert event.value == 0

    def test_parse_key_explain_e(self):
        """Test parsing 'e' key for explain."""
        event = CursesInputProvider._parse_key(ord("e"))
        assert event.event_type == InputEventType.EXPLAIN

    def test_parse_key_explain_E(self):
        """Test parsing 'E' key for explain."""
        event = CursesInputProvider._parse_key(ord("E"))
        assert event.event_type == InputEventType.EXPLAIN

    def test_parse_key_help_question_mark(self):
        """Test parsing '?' key for help."""
        event = CursesInputProvider._parse_key(ord("?"))
        assert event.event_type == InputEventType.EXPLAIN

    def test_parse_key_arrow_up(self):
        """Test parsing UP arrow key."""
        event = CursesInputProvider._parse_key(curses.KEY_UP)
        assert event.event_type == InputEventType.UP

    def test_parse_key_arrow_down(self):
        """Test parsing DOWN arrow key."""
        event = CursesInputProvider._parse_key(curses.KEY_DOWN)
        assert event.event_type == InputEventType.DOWN

    def test_parse_key_unknown(self):
        """Test parsing unknown key."""
        event = CursesInputProvider._parse_key(999)
        assert event.event_type == InputEventType.UNKNOWN

    def test_parse_key_space_separator(self):
        """Test parsing space key as SEPARATOR."""
        event = CursesInputProvider._parse_key(ord(" "))
        assert event.event_type == InputEventType.SEPARATOR

    def test_parse_key_comma_separator(self):
        """Test parsing comma key as SEPARATOR."""
        event = CursesInputProvider._parse_key(ord(","))
        assert event.event_type == InputEventType.SEPARATOR

    def test_supports_raw(self):
        """Test that raw input is supported."""
        mock_stdscr = Mock()
        provider = CursesInputProvider(mock_stdscr)
        assert provider.supports_raw() is True

    def test_init_stores_stdscr(self):
        """Test that CursesInputProvider stores the stdscr reference."""
        mock_stdscr = Mock()
        provider = CursesInputProvider(mock_stdscr)
        assert provider.stdscr is mock_stdscr

    def test_init_sets_timeout(self):
        """Test that CursesInputProvider sets a 1-second getch() timeout."""
        mock_stdscr = Mock()
        CursesInputProvider(mock_stdscr)
        mock_stdscr.timeout.assert_called_once_with(500)

    def test_events_generator_yields_timeout_on_minus_one(self):
        """Test that getch() returning -1 yields a TIMEOUT event."""
        mock_stdscr = Mock()
        mock_stdscr.getch.side_effect = [-1, KeyboardInterrupt()]

        provider = CursesInputProvider(mock_stdscr)
        event = next(provider.events)
        assert event.event_type == InputEventType.TIMEOUT

    def test_events_generator_yields_input_events(self):
        """Test that events property yields input events."""
        mock_stdscr = Mock()
        # Simulate getch() returning keys
        mock_stdscr.getch.side_effect = [ord("1"), ord("2"), KeyboardInterrupt()]

        provider = CursesInputProvider(mock_stdscr)
        events_gen = provider.events

        # Get first event
        event1 = next(events_gen)
        assert event1.event_type == InputEventType.NUMBER
        assert event1.value == 1

        # Get second event
        event2 = next(events_gen)
        assert event2.event_type == InputEventType.NUMBER
        assert event2.value == 2

        # Get third event (after KeyboardInterrupt should yield QUIT)
        event3 = next(events_gen)
        assert event3.event_type == InputEventType.QUIT
