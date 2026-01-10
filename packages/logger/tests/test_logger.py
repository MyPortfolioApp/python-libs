"""Tests for mylogger."""

import json
from io import StringIO
from unittest.mock import patch

import pytest

from mylogger import (
    bind_context,
    clear_context,
    configure,
    get_logger,
    log_db,
    log_error,
    log_info,
    log_start,
    log_success,
    unbind_context,
)
from mylogger.core import _configured, _debug_mode


@pytest.fixture(autouse=True)
def reset_logger() -> None:
    """Reset logger state before each test."""
    import mylogger.core as core

    core._configured = False
    core._debug_mode = None
    clear_context()


def test_get_logger_returns_bound_logger() -> None:
    """Test that get_logger returns a usable logger."""
    log = get_logger("test")
    assert log is not None


def test_configure_debug_mode() -> None:
    """Test configuration in debug mode."""
    configure(debug=True)
    # Should not raise
    log_info("test message")


def test_configure_production_mode(capsys: pytest.CaptureFixture[str]) -> None:
    """Test configuration in production mode outputs JSON."""
    configure(debug=False)
    log_info("test message")

    captured = capsys.readouterr()
    # Production mode outputs JSON
    output = json.loads(captured.out.strip())
    assert output["event"] == "test message"
    assert "timestamp" in output


def test_log_success_adds_status(capsys: pytest.CaptureFixture[str]) -> None:
    """Test log_success adds status field."""
    configure(debug=False)
    log_success("operation completed")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["status"] == "success"


def test_log_start_adds_phase(capsys: pytest.CaptureFixture[str]) -> None:
    """Test log_start adds phase field."""
    configure(debug=False)
    log_start("starting process")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["phase"] == "start"


def test_log_db_adds_component(capsys: pytest.CaptureFixture[str]) -> None:
    """Test log_db adds component field."""
    configure(debug=False)
    log_db("query executed")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["component"] == "database"


def test_log_error_level(capsys: pytest.CaptureFixture[str]) -> None:
    """Test log_error uses error level."""
    configure(debug=False)
    log_error("something failed")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["log_level"] == "error"


def test_extra_kwargs_passed(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that extra kwargs are included in output."""
    configure(debug=False)
    log_info("user action", user_id=123, action="login")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["user_id"] == 123
    assert output["action"] == "login"


def test_bind_context(capsys: pytest.CaptureFixture[str]) -> None:
    """Test context binding persists across log calls."""
    configure(debug=False)
    bind_context(request_id="abc-123")

    log_info("first message")
    log_info("second message")

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert len(lines) == 2

    for line in lines:
        output = json.loads(line)
        assert output["request_id"] == "abc-123"


def test_unbind_context(capsys: pytest.CaptureFixture[str]) -> None:
    """Test unbind removes specific context."""
    configure(debug=False)
    bind_context(request_id="abc-123", user_id=456)
    unbind_context("user_id")

    log_info("message")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["request_id"] == "abc-123"
    assert "user_id" not in output


def test_clear_context(capsys: pytest.CaptureFixture[str]) -> None:
    """Test clear removes all context."""
    configure(debug=False)
    bind_context(request_id="abc-123", user_id=456)
    clear_context()

    log_info("message")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert "request_id" not in output
    assert "user_id" not in output


def test_debug_env_variable() -> None:
    """Test DEBUG environment variable is respected."""
    import mylogger.core as core

    with patch.dict("os.environ", {"DEBUG": "false"}):
        core._debug_mode = None
        assert core._get_debug_mode() is False

    with patch.dict("os.environ", {"DEBUG": "true"}):
        core._debug_mode = None
        assert core._get_debug_mode() is True
