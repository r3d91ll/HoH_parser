import logging
from hoh_mcp.utils.logging import get_logger
from hoh_mcp.config import settings
import importlib
import sys

def test_get_logger_returns_logger():
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"


def test_get_logger_sets_level(monkeypatch):
    # Patch settings.log_level and reload get_logger
    monkeypatch.setattr(settings, "log_level", "DEBUG")
    # Remove all handlers for a clean test
    logger = get_logger("test_logger_level")
    for h in logger.handlers:
        logger.removeHandler(h)
    logger = get_logger("test_logger_level")
    assert logger.level == logging.DEBUG


def test_logger_format_and_output(caplog):
    logger = get_logger("test_format")
    with caplog.at_level(logging.INFO):
        logger.info("Hello test!")
    # Check log output format
    found = any("Hello test!" in message for message in caplog.messages)
    assert found
    assert any(record.name == "test_format" for record in caplog.records)


def test_get_logger_adds_handler():
    # Use a unique logger name to guarantee no handlers on the logger itself
    unique_logger_name = "test_logger_no_handlers_xyz"
    logger = logging.getLogger(unique_logger_name)
    # Remove all handlers from this logger
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    logger.propagate = False  # Prevent inheriting handlers from parent/root
    assert len(logger.handlers) == 0
    logger = get_logger(unique_logger_name)
    # Should have exactly one handler, and it should be a StreamHandler
    handlers = logger.handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)
