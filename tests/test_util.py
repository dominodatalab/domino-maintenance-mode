import pytest

from domino_maintenance_mode.util import get_auth_headers

LEGACY_KEY = "abc123opaquekey"
# Header-only JWT shape (three dot-separated segments, "eyJ" prefix).
# Not a real token.
PAT_JWT = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.sig"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("DOMINO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("DOMINO_API_KEY", raising=False)


def test_auth_token_env_takes_precedence(monkeypatch):
    monkeypatch.setenv("DOMINO_AUTH_TOKEN", PAT_JWT)
    monkeypatch.setenv("DOMINO_API_KEY", LEGACY_KEY)

    assert get_auth_headers() == {"Authorization": f"Bearer {PAT_JWT}"}


def test_legacy_api_key_still_works(monkeypatch):
    monkeypatch.setenv("DOMINO_API_KEY", LEGACY_KEY)

    assert get_auth_headers() == {"X-Domino-Api-Key": LEGACY_KEY}


def test_jwt_shaped_api_key_is_sent_as_bearer(monkeypatch):
    monkeypatch.setenv("DOMINO_API_KEY", PAT_JWT)

    assert get_auth_headers() == {"Authorization": f"Bearer {PAT_JWT}"}


def test_no_credentials_raises_with_both_var_names(monkeypatch):
    with pytest.raises(Exception) as exc_info:
        get_auth_headers()

    message = str(exc_info.value)
    assert "DOMINO_AUTH_TOKEN" in message
    assert "DOMINO_API_KEY" in message
