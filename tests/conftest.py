"""Fixtures for the CTF V4.3 tests.

app.py reads CTF_DB and CTF_SECRET and creates the database when it is imported, so both are set
here, before the import, to keep secret.key and ctf.db out of ctf-server/. Each test then gets its
own empty database file.
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_boot = tempfile.mkdtemp(prefix="ctf-tests-")
os.environ["CTF_DB"] = os.path.join(_boot, "import.db")
os.environ["CTF_SECRET"] = "test-secret"
sys.path[:0] = [str(ROOT / "ctf-server"), str(ROOT / "reference")]

import app as ctf  # noqa: E402


class Clock:
    """Replaces time.time() so cooldowns and lockouts can be tested without waiting."""

    def __init__(self, start=1_000_000.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def server(tmp_path, monkeypatch):
    monkeypatch.setattr(ctf, "DB_PATH", str(tmp_path / "ctf.db"))
    ctf.init_db()
    ctf.LOGIN_FAILS.clear()
    ctf.GLOBAL_FAILS.clear()
    return ctf


@pytest.fixture
def clock(monkeypatch):
    c = Clock()
    monkeypatch.setattr(ctf.time, "time", c)
    return c


@pytest.fixture
def open_all(server):
    with server.app.app_context():
        server.set_levels_open(server.db(), [1, 2, 3], True)


def login(client, nick, pin="1234"):
    return client.post("/api/login", json={"nick": nick, "pin": pin})


def flag_of(server, nick, level):
    """The flag the server expects from this player (what `flask --app app respostas` prints)."""
    with server.app.app_context():
        return server.puzzle_for(nick.lower(), level)["flag"]
