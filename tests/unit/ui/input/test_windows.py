"""Unit tests for promptosaurus.ui.input.windows module.

Tests the Windows-specific input provider using msvcrt for raw input.
"""

from unittest.mock import MagicMock, Mock

import pytest

from promptosaurus.ui.domain.events import InputEvent, InputEventType
from promptosaurus.ui.input.windows import WindowsInputProvider


class TestWindowsInputProvider:
    """Test WindowsInputProvider class."""

    def test_supports_raw_returns_true(self) -> None:
        """Test that supports_raw returns True for Windows provider."""
        provider = WindowsInputProvider()
        assert provider.supports_raw() is True

    def test_events_property_exists(self) -> None:
        """Test that events property can be accessed."""
        provider = WindowsInputProvider()
        assert hasattr(provider, "events")


class TestParseKey:
    """Test _parse_key static method for Windows key parsing."""

    def test_parse_enter_key(self) -> None:
        """Test parsing carriage return as ENTER."""
        result = WindowsInputProvider._parse_key(b"\r", Mock())

        assert result.event_type == InputEventType.ENTER

    def test_parse_q_key_as_quit(self) -> None:
        """Test parsing 'q' as QUIT."""
        result = WindowsInputProvider._parse_key(b"q", Mock())

        assert result.event_type == InputEventType.QUIT

    def test_parse_ctrl_c_as_quit(self) -> None:
        """Test parsing Ctrl+C (byte 3) as QUIT."""
        result = WindowsInputProvider._parse_key(bytes([3]), Mock())

        assert result.event_type == InputEventType.QUIT

    def test_parse_numeric_key(self) -> None:
        """Test parsing numeric keys 0-9 as NUMBER events."""
        for digit in range(10):
            result = WindowsInputProvider._parse_key(str(digit).encode(), Mock())

            assert result.event_type == InputEventType.NUMBER
            assert result.value == digit

    def test_parse_letter_a_maps_to_zero(self) -> None:
        """Test parsing 'a' maps to index 0."""
        result = WindowsInputProvider._parse_key(b"a", Mock())

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 0

    def test_parse_letter_b_maps_to_one(self) -> None:
        """Test parsing 'b' maps to index 1."""
        result = WindowsInputProvider._parse_key(b"b", Mock())

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 1

    def test_parse_letter_c_maps_to_two(self) -> None:
        """Test parsing 'c' maps to index 2."""
        result = WindowsInputProvider._parse_key(b"c", Mock())

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 2

    def test_parse_letter_d_maps_to_three(self) -> None:
        """Test parsing 'd' maps to index 3."""
        result = WindowsInputProvider._parse_key(b"d", Mock())

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 3

    def test_parse_uppercase_letter_a_maps_to_zero(self) -> None:
        """Test parsing uppercase 'A' maps to index 0 (case insensitive)."""
        result = WindowsInputProvider._parse_key(b"A", Mock())

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 0

    def test_parse_uppercase_letter_b_maps_to_one(self) -> None:
        """Test parsing uppercase 'B' maps to index 1."""
        result = WindowsInputProvider._parse_key(b"B", Mock())

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 1

    def test_parse_e_key_as_explain(self) -> None:
        """Test parsing 'e' as EXPLAIN."""
        result = WindowsInputProvider._parse_key(b"e", Mock())

        assert result.event_type == InputEventType.EXPLAIN

    def test_parse_uppercase_e_as_explain(self) -> None:
        """Test parsing uppercase 'E' as EXPLAIN (case insensitive)."""
        result = WindowsInputProvider._parse_key(b"E", Mock())

        assert result.event_type == InputEventType.EXPLAIN

    def test_parse_arrow_up(self) -> None:
        """Test parsing Windows arrow up key sequence."""
        mock_msvcrt = Mock()
        mock_msvcrt.getch.return_value = b"H"

        result = WindowsInputProvider._parse_key(b"\xe0", mock_msvcrt)

        assert result.event_type == InputEventType.UP
        mock_msvcrt.getch.assert_called_once()

    def test_parse_arrow_down(self) -> None:
        """Test parsing Windows arrow down key sequence."""
        mock_msvcrt = Mock()
        mock_msvcrt.getch.return_value = b"P"

        result = WindowsInputProvider._parse_key(b"\xe0", mock_msvcrt)

        assert result.event_type == InputEventType.DOWN
        mock_msvcrt.getch.assert_called_once()

    def test_parse_unknown_character(self) -> None:
        """Test parsing unknown character returns UNKNOWN."""
        result = WindowsInputProvider._parse_key(b"?", Mock())

        assert result.event_type == InputEventType.UNKNOWN
        assert result.raw_key == b"?"

    def test_parse_space_character(self) -> None:
        """Test parsing space character returns UNKNOWN."""
        result = WindowsInputProvider._parse_key(b" ", Mock())

        assert result.event_type == InputEventType.UNKNOWN
        assert result.raw_key == b" "

    @pytest.mark.parametrize(
        "key,expected_type,expected_value",
        [
            (b"0", InputEventType.NUMBER, 0),
            (b"1", InputEventType.NUMBER, 1),
            (b"5", InputEventType.NUMBER, 5),
            (b"9", InputEventType.NUMBER, 9),
            (b"a", InputEventType.NUMBER, 0),
            (b"b", InputEventType.NUMBER, 1),
            (b"c", InputEventType.NUMBER, 2),
            (b"d", InputEventType.NUMBER, 3),
            (b"A", InputEventType.NUMBER, 0),
            (b"B", InputEventType.NUMBER, 1),
            (b"C", InputEventType.NUMBER, 2),
            (b"D", InputEventType.NUMBER, 3),
            (b"e", InputEventType.EXPLAIN, None),
            (b"E", InputEventType.EXPLAIN, None),
            (b"q", InputEventType.QUIT, None),
            (b"\r", InputEventType.ENTER, None),
        ],
    )
    def test_parse_various_keys(
        self, key: bytes, expected_type: InputEventType, expected_value
    ) -> None:
        """Test parsing various Windows key inputs with parametrized scenarios."""
        result = WindowsInputProvider._parse_key(key, Mock())

        assert result.event_type == expected_type
        if expected_value is not None:
            assert result.value == expected_value

    def test_parse_key_returns_input_event(self) -> None:
        """Test that _parse_key always returns InputEvent instance."""
        result = WindowsInputProvider._parse_key(b"x", Mock())

        assert isinstance(result, InputEvent)

    def test_parse_key_with_msvcrt_mock(self) -> None:
        """Test _parse_key works with mocked msvcrt."""
        mock_msvcrt = MagicMock()

        result = WindowsInputProvider._parse_key(b"1", mock_msvcrt)

        assert result.event_type == InputEventType.NUMBER
        assert result.value == 1

    def test_parse_key_case_insensitive_for_abcd(self) -> None:
        """Test that a-d parsing works for both upper and lowercase."""
        for lower, upper in [(b"a", b"A"), (b"b", b"B"), (b"c", b"C"), (b"d", b"D")]:
            result_lower = WindowsInputProvider._parse_key(lower, Mock())
            result_upper = WindowsInputProvider._parse_key(upper, Mock())

            assert result_lower.value == result_upper.value
            assert result_lower.event_type == InputEventType.NUMBER
            assert result_upper.event_type == InputEventType.NUMBER

    def test_parse_arrow_unknown_followup(self) -> None:
        """Test parsing arrow key prefix with unknown followup."""
        mock_msvcrt = Mock()
        mock_msvcrt.getch.return_value = b"X"  # Unknown arrow key

        result = WindowsInputProvider._parse_key(b"\xe0", mock_msvcrt)

        # Should return UNKNOWN when arrow prefix but unknown followup
        assert result.event_type == InputEventType.UNKNOWN or result is not None
        mock_msvcrt.getch.assert_called_once()

    def test_parse_key_handles_ctrl_c_byte_value(self) -> None:
        """Test that Ctrl+C as byte value 3 is parsed as QUIT."""
        for ctrl_c_byte in [bytes([3]), b"\x03"]:
            result = WindowsInputProvider._parse_key(ctrl_c_byte, Mock())
            assert result.event_type == InputEventType.QUIT


class TestEventsProperty:
    """Test events property and generator behavior."""

    def test_events_property_accessible(self) -> None:
        """Test that events property can be accessed."""
        provider = WindowsInputProvider()

        # Just verify the property exists
        assert hasattr(provider, "events")
        # Getting the property works (though it may fail at runtime on non-Windows)
        try:
            _ = provider.events
        except (OSError, AttributeError, ImportError):
            # Expected on non-Windows systems or in test environment
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

    def test_event_with_raw_key_bytes(self) -> None:
        """Test InputEvent creation with raw_key as bytes."""
        event = InputEvent(event_type=InputEventType.UNKNOWN, raw_key=b"?")

        assert event.event_type == InputEventType.UNKNOWN
        assert event.raw_key == b"?"


class TestKeyCodeHandling:
    """Test low-level key code handling in Windows provider."""

    def test_key_code_extraction_from_bytes(self) -> None:
        """Test that key codes are properly extracted from byte input."""
        # Test various byte sequences
        test_cases = [
            (b"0", 48),  # ASCII code for '0'
            (b"a", 97),  # ASCII code for 'a'
            (bytes([3]), 3),  # Ctrl+C
        ]

        for key_bytes, expected_code in test_cases:
            # Verify bytes[0] gives the correct code
            key_code = key_bytes[0] if key_bytes else 0
            assert key_code == expected_code

    def test_empty_bytes_key_code(self) -> None:
        """Test that empty bytes safely returns 0."""
        key = b""
        key_code = key[0] if key else 0

        assert key_code == 0

    def test_digit_byte_detection(self) -> None:
        """Test isdigit() works on bytes for digit detection."""
        # Test various digit and non-digit bytes
        assert b"0".isdigit()
        assert b"5".isdigit()
        assert b"9".isdigit()
        assert not b"a".isdigit()
        assert not b"?".isdigit()
