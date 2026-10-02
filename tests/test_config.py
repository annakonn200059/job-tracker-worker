import pytest

from worker.config import Config


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ("DATABASE_URL", "LOG_LEVEL", "SHUTDOWN_WAIT", "POLL_INTERVAL"):
        monkeypatch.delenv(name, raising=False)


def test_requires_database_url():
    with pytest.raises(ValueError, match="DATABASE_URL"):
        Config.load()


def test_defaults(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/db")

    cfg = Config.load()

    assert cfg.database_url == "postgresql://localhost/db"
    assert cfg.log_level == "info"
    assert cfg.shutdown_wait == 15.0
    assert cfg.poll_interval == 5.0


def test_overrides(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/db")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("SHUTDOWN_WAIT", "30")
    monkeypatch.setenv("POLL_INTERVAL", "0.5")

    cfg = Config.load()

    assert cfg.log_level == "debug"
    assert cfg.shutdown_wait == 30.0
    assert cfg.poll_interval == 0.5
