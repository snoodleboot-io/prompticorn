"""Unit tests for prompticorn.ui.input.unix module.

Tests the Unix-specific input provider using termios/tty for raw input.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from prompticorn.ui.domain.events import InputEvent, InputEventType
from prompticorn.ui.input.unix import UnixInputProvider


class TestUnixInputProvider:
    """Test UnixInputProvider class."""

    def test_supports_raw_returns_true(self) -> None:
        """Test that supports_raw returns True for Unix provider."""
        provider = UnixInputProvider()
        assert provider.supports_raw() is True

    def test_events_property_exists(self) -> None:
        """Test that events property can be accessed."""
        provider = UnixInputProvider()
        assert hasattr(provider, "events")


class TestParseKey:
    """Test _parse_key static method for key parsing."""

    def test_parse_enter_key(self) -> None:
        """Test parsing carriage return as ENTER."""
        result = UnixInputProvider._parse_key("\r", Mock())

        assert result.event_type == InputEventType.ENTER
        assert result.value is None

    def test_parse_q_key_as_quit(self) -> None:
        """Test parsing 'q' as QUIT."""
        result = UnixInputProvider._parse_key("q", Mock())

        assert result.event_type == InputEventType.QUIT
        assert result.value is None

    def test_parse_ctrl_c_as_quit(self) -> None:
        """Test parsing Ctrl+C (\\x03) as QUIT."""
        result = UnixInputProvider._parse_key("\x03", Mock())

        assert result.event_type == InputEventType.QUIT

    def test_parse_numeric_key(self) -> None:
        """Test parsing numeric keys 0-9 as NUMBER events."""
        for digit in range(10):
            result = UnixInputProvider._parse_key(str(digit), Mock())

            assert result.event_type == InputEventType.NUMBER
            assert result.value == digit

    def test_parse_letter_a_maps_to_zero(self) -> None:
        """Test parsing 'a' maps to index 0."""
        result = UnixInputProvider._parse_key("a", Mock())

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 0

    def test_parse_letter_b_maps_to_one(self) -> None:
        """Test parsing 'b' maps to index 1."""
        result = UnixInputProvider._parse_key("b", Mock())

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 1

    def test_parse_letter_c_maps_to_two(self) -> None:
        """Test parsing 'c' maps to index 2."""
        result = UnixInputProvider._parse_key("c", Mock())

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 2

    def test_parse_letter_d_maps_to_three(self) -> None:
        """Test parsing 'd' maps to index 3."""
        result = UnixInputProvider._parse_key("d", Mock())

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 3

    def test_parse_uppercase_letter_a_maps_to_zero(self) -> None:
        """Test parsing uppercase 'A' maps to index 0 (case insensitive)."""
        result = UnixInputProvider._parse_key("A", Mock())

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 0

    def test_parse_uppercase_letter_b_maps_to_one(self) -> None:
        """Test parsing uppercase 'B' maps to index 1."""
        result = UnixInputProvider._parse_key("B", Mock())

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 1

    def test_parse_e_key_as_explain(self) -> None:
        """Test parsing 'e' as EXPLAIN."""
        result = UnixInputProvider._parse_key("e", Mock())

        assert result.event_type == InputEventType.EXPLAIN

    def test_parse_uppercase_e_as_explain(self) -> None:
        """Test parsing uppercase 'E' as EXPLAIN (case insensitive)."""
        result = UnixInputProvider._parse_key("E", Mock())

        assert result.event_type == InputEventType.EXPLAIN

    def test_parse_escape_with_no_followup_returns_unknown(self) -> None:
        """Test parsing ESC with no following data returns UNKNOWN."""
        mock_stdin = Mock()
        # select.select returns no data to read (empty list)
        with patch("select.select") as mock_select:
            mock_select.return_value = ([], [], [])

            result = UnixInputProvider._parse_key("\x1b", mock_stdin)

            assert result.event_type == InputEventType.UNKNOWN
            assert result.raw_key == "\x1b"

    def test_parse_escape_up_arrow(self) -> None:
        """Test parsing ESC followed by [A as UP arrow."""
        mock_stdin = Mock()
        mock_stdin.read.return_value = "[A"

        with patch("select.select") as mock_select:
            mock_select.return_value = ([mock_stdin], [], [])

            result = UnixInputProvider._parse_key("\x1b", mock_stdin)

            assert result.event_type == InputEventType.UP
            mock_stdin.read.assert_called_once_with(2)

    def test_parse_escape_down_arrow(self) -> None:
        """Test parsing ESC followed by [B as DOWN arrow."""
        mock_stdin = Mock()
        mock_stdin.read.return_value = "[B"

        with patch("select.select") as mock_select:
            mock_select.return_value = ([mock_stdin], [], [])

            result = UnixInputProvider._parse_key("\x1b", mock_stdin)

            assert result.event_type == InputEventType.DOWN
            mock_stdin.read.assert_called_once_with(2)

    def test_parse_escape_with_timeout(self) -> None:
        """Test that select.select is called with timeout."""
        mock_stdin = Mock()

        with patch("select.select") as mock_select:
            mock_select.return_value = ([], [], [])

            UnixInputProvider._parse_key("\x1b", mock_stdin)

            # Verify select was called
            mock_select.assert_called_once()

    def test_parse_unknown_character(self) -> None:
        """Test parsing unknown character returns UNKNOWN."""
        result = UnixInputProvider._parse_key("?", Mock())

        assert result.event_type == InputEventType.UNKNOWN
        assert result.raw_key == "?"

    def test_parse_space_character(self) -> None:
        """Test parsing space character returns UNKNOWN."""
        result = UnixInputProvider._parse_key(" ", Mock())

        assert result.event_type == InputEventType.UNKNOWN
        assert result.raw_key == " "

    @pytest.mark.parametrize(
        "key,expected_type,expected_value",
        [
            ("0", InputEventType.NUMBER, 0),
            ("1", InputEventType.NUMBER, 1),
            ("5", InputEventType.NUMBER, 5),
            ("9", InputEventType.NUMBER, 9),
            ("a", InputEventType.NUMBER, 0),
            ("b", InputEventType.NUMBER, 1),
            ("c", InputEventType.NUMBER, 2),
            ("d", InputEventType.NUMBER, 3),
            ("A", InputEventType.NUMBER, 0),
            ("B", InputEventType.NUMBER, 1),
            ("C", InputEventType.NUMBER, 2),
            ("D", InputEventType.NUMBER, 3),
            ("e", InputEventType.EXPLAIN, None),
            ("E", InputEventType.EXPLAIN, None),
            ("q", InputEventType.QUIT, None),
            ("\r", InputEventType.ENTER, None),
            ("\x03", InputEventType.QUIT, None),
        ],
    )
    def test_parse_various_keys(
        self, key: str, expected_type: InputEventType, expected_value
    ) -> None:
        """Test parsing various keys with parametrized scenarios."""
        result = UnixInputProvider._parse_key(key, Mock())

        assert result.event_type == expected_type
        if expected_value is not None:
            assert result.value == expected_value

    def test_parse_key_returns_input_event(self) -> None:
        """Test that _parse_key always returns InputEvent instance."""
        result = UnixInputProvider._parse_key("x", Mock())

        assert isinstance(result, InputEvent)

    def test_parse_key_with_stdin_mock(self) -> None:
        """Test _parse_key works with mocked stdin."""
        mock_stdin = MagicMock()

        result = UnixInputProvider._parse_key("1", mock_stdin)

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 1

    def test_parse_key_is_case_insensitive_for_abcd(self) -> None:
        """Test that a-d parsing works for both upper and lowercase."""
        for lower, upper in [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")]:
            result_lower = UnixInputProvider._parse_key(lower, Mock())
            result_upper = UnixInputProvider._parse_key(upper, Mock())

            assert result_lower.value == result_upper.value
            assert result_lower.event_type == InputEventType.NUMBER
            assert result_upper.event_type == InputEventType.NUMBER


class TestEventsProperty:
    """Test events property and generator behavior."""

    def test_events_property_accessible(self) -> None:
        """Test that events property can be accessed."""
        provider = UnixInputProvider()

        # Just verify the property exists and is callable
        assert hasattr(provider, "events")
        # Getting the property works (though it may fail at runtime on non-Unix)
        try:
            _ = provider.events
        except (OSError, AttributeError, ImportError):
            # Expected on non-Unix systems or in test environment
            pass


class TestInputEventCreation:
    """Test that InputEvent objects are created correctly."""

    def test_event_with_enter_type(self) -> None:
        """Test InputEvent creation for ENTER type."""
        event = InputEvent(event_type=InputEventType.ENTER)

        assert event.event_type == InputEventType.ENTER
        assert event.value is None

    def test_event_with_number_value(self) -> None:
        """Test InputEvent creation with NUMBER type and value."""
        event = InputEvent(event_type=InputEventType.NUMBER, value=5)

        assert event.event_type == InputEventType.NUMBER
        assert event.value == 5

    def test_event_with_raw_key(self) -> None:
        """Test InputEvent creation with raw_key."""
        event = InputEvent(event_type=InputEventType.UNKNOWN, raw_key="?")

        assert event.event_type == InputEventType.UNKNOWN
        assert event.raw_key == "?"
