"""Tests for core module."""

from example_lib import greet


def test_greet() -> None:
    """Test greet function returns correct message."""
    result = greet("World")
    assert result == "Hello, World!"


def test_greet_with_name() -> None:
    """Test greet function with custom name."""
    result = greet("Carlo")
    assert result == "Hello, Carlo!"
