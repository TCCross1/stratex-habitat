import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://exciting-torvalds-7.preview.emergentagent.com").rstrip("/")
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
