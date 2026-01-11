"""Tests for mylogger."""

import json
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


@pytest.fixture(autouse=True)
def reset_logger() -> None:
    """Reset logger state before each test."""
    import mylogger.core as core

    core._configured = False
    core._log_format = None
    core._exclude_levels = None
    clear_context()


def test_get_logger_returns_bound_logger() -> None:
    """Test that get_logger returns a usable logger."""
    log = get_logger("test")
    assert log is not None


def test_configure_console_mode() -> None:
    """Test configuration in console mode."""
    configure(format="console")
    # Should not raise
    log_info("test message")


def test_configure_json_mode(capsys: pytest.CaptureFixture[str]) -> None:
    """Test configuration in json mode outputs JSON."""
    configure(format="json")
    log_info("test message")

    captured = capsys.readouterr()
    # Production mode outputs JSON
    output = json.loads(captured.out.strip())
    assert output["event"] == "test message"
    assert "timestamp" in output


def test_log_success_adds_status(capsys: pytest.CaptureFixture[str]) -> None:
    """Test log_success adds status field."""
    configure(format="json")
    log_success("operation completed")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["status"] == "success"


def test_log_start_adds_phase(capsys: pytest.CaptureFixture[str]) -> None:
    """Test log_start adds phase field."""
    configure(format="json")
    log_start("starting process")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["phase"] == "start"


def test_log_db_adds_component(capsys: pytest.CaptureFixture[str]) -> None:
    """Test log_db adds component field."""
    configure(format="json")
    log_db("query executed")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["component"] == "database"


def test_log_error_level(capsys: pytest.CaptureFixture[str]) -> None:
    """Test log_error uses error level."""
    configure(format="json")
    log_error("something failed")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["level"] == "error"


def test_extra_kwargs_passed(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that extra kwargs are included in output."""
    configure(format="json")
    log_info("user action", user_id=123, action="login")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["user_id"] == 123
    assert output["action"] == "login"


def test_bind_context(capsys: pytest.CaptureFixture[str]) -> None:
    """Test context binding persists across log calls."""
    configure(format="json")
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
    configure(format="json")
    bind_context(request_id="abc-123", user_id=456)
    unbind_context("user_id")

    log_info("message")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["request_id"] == "abc-123"
    assert "user_id" not in output


def test_clear_context(capsys: pytest.CaptureFixture[str]) -> None:
    """Test clear removes all context."""
    configure(format="json")
    bind_context(request_id="abc-123", user_id=456)
    clear_context()

    log_info("message")

    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert "request_id" not in output
    assert "user_id" not in output


def test_format_env_variable() -> None:
    """Test MYLOGGER_FORMAT environment variable is respected."""
    import mylogger.core as core

    with patch.dict("os.environ", {"MYLOGGER_FORMAT": "json"}):
        core._log_format = None
        assert core._get_format() == "json"

    with patch.dict("os.environ", {"MYLOGGER_FORMAT": "console"}):
        core._log_format = None
        assert core._get_format() == "console"


def test_exclude_env_variable() -> None:
    """Test MYLOGGER_EXCLUDE environment variable is respected."""
    import mylogger.core as core

    with patch.dict("os.environ", {"MYLOGGER_EXCLUDE": "debug,info"}):
        core._exclude_levels = None
        assert core._get_exclude_levels() == {"debug", "info"}

    with patch.dict("os.environ", {"MYLOGGER_EXCLUDE": ""}):
        core._exclude_levels = None
        assert core._get_exclude_levels() == set()


def test_exclude_filters_logs(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that excluded levels are not logged."""
    configure(format="json", exclude=["debug"])
    log = get_logger("test")

    log.debug("should not appear")
    log.info("should appear")

    captured = capsys.readouterr()
    lines = [line for line in captured.out.strip().split("\n") if line]
    assert len(lines) == 1
    output = json.loads(lines[0])
    assert output["event"] == "should appear"


def test_exclude_multiple_levels(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that multiple levels can be excluded."""
    configure(format="json", exclude=["debug", "info"])
    log = get_logger("test")

    log.debug("debug - excluded")
    log.info("info - excluded")
    log.warning("warning - should appear")

    captured = capsys.readouterr()
    lines = [line for line in captured.out.strip().split("\n") if line]
    assert len(lines) == 1
    output = json.loads(lines[0])
    assert output["event"] == "warning - should appear"
