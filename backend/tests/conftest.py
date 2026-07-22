"""
Shared pytest fixtures for the Habitat backend integration suite.

Configuration is resolved from the environment first, then from the committed
`.env` files (no hard-coded preview URLs). Provides authenticated HTTP sessions
and a direct MongoDB handle for DB-level assertions (audit events, opportunity
counts).
"""
import os
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[2]  # /app
_FE = dotenv_values(ROOT / "frontend" / ".env")
_BE = dotenv_values(ROOT / "backend" / ".env")


def _cfg(key: str) -> str:
    val = os.environ.get(key) or _FE.get(key) or _BE.get(key)
    if not val:
        raise RuntimeError(f"Required config '{key}' not found in env or .env files")
    return val


BASE_URL = _cfg("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"

HOMEOWNER = {"email": "alex@stratexhabitat.com", "password": "Demo123!"}
CONTRACTOR = {"email": "horizon@stratexhabitat.com", "password": "Demo123!"}
EXEC = {"email": "admin@stratexhabitat.com", "password": "Admin123!"}


def _login(creds):
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json=creds, timeout=20)
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="session")
def homeowner_session():
    return _login(HOMEOWNER)


@pytest.fixture(scope="session")
def contractor_session():
    return _login(CONTRACTOR)


@pytest.fixture(scope="session")
def exec_session():
    return _login(EXEC)


@pytest.fixture(scope="session")
def api_url():
    return API


@pytest.fixture(scope="session")
def db():
    client = MongoClient(_cfg("MONGO_URL"))
    try:
        yield client[_cfg("DB_NAME")]
    finally:
        client.close()
