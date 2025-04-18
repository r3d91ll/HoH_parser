import os
import importlib
import sys
import types
import pytest

def test_settings_defaults():
    # Import the config module fresh to avoid cached settings
    if "HoH_parser.config" in sys.modules:
        del sys.modules["HoH_parser.config"]
    config = importlib.import_module("HoH_parser.config")
    settings = config.settings
    assert settings.debug is False
    assert settings.log_level == "INFO"
    assert settings.arangodb_url == "http://localhost:8529"
    assert settings.arangodb_user == "root"
    assert settings.arangodb_password == ""

def test_settings_env(monkeypatch):
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("ARANGODB_URL", "http://test:9999")
    monkeypatch.setenv("ARANGODB_USER", "tester")
    monkeypatch.setenv("ARANGODB_PASSWORD", "secret")
    # Remove module from sys.modules to force reload with new env vars
    if "HoH_parser.config" in sys.modules:
        del sys.modules["HoH_parser.config"]
    config = importlib.import_module("HoH_parser.config")
    settings = config.Settings()
    assert settings.debug is True
    assert settings.log_level == "DEBUG"
    assert settings.arangodb_url == "http://test:9999"
    assert settings.arangodb_user == "tester"
    assert settings.arangodb_password == "secret"
