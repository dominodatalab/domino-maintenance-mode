import asyncio
from unittest import mock

import pytest

from domino_maintenance_mode.interfaces.apps import Interface


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    # Interface.__init__ resolves hostname/credentials from the environment.
    monkeypatch.setenv("DOMINO_HOSTNAME", "https://example.invalid")
    monkeypatch.setenv("DOMINO_API_KEY", "test-key")


def _app(id_, status, publisher={"userName": "alice"}):
    return {
        "id": id_,
        "hardwareTierId": "small-k8s",
        "projectId": "p1",
        "name": f"app-{id_}",
        "status": status,
        "publisher": publisher,
    }


def _run(apps):
    iface = Interface()
    with mock.patch.object(iface, "get", return_value=apps):
        return asyncio.run(iface.list_running(None, []))


def test_running_app_is_captured():
    result = _run([_app("1", "Running")])
    assert [e._id._id for e in result] == ["1"]


def test_never_started_app_is_skipped():
    # Regression: "Never Started" is not a running state and must be excluded,
    # regardless of publisher — previously it leaked past the status filter.
    result = _run([_app("1", "Never Started")])
    assert result == []


def test_never_started_with_null_publisher_is_skipped_not_errored():
    # A created-but-never-launched App whose publisher was a deactivated user
    # (null). Must be skipped cleanly, not error-dropped and not wrongly
    # captured.
    result = _run([_app("1", "Never Started", publisher=None)])
    assert result == []


def test_stopped_states_are_skipped():
    apps = [_app(s, s) for s in ("Stopped", "Succeeded", "Failed", "Error")]
    assert _run(apps) == []


def test_mixed_batch_keeps_only_running():
    apps = [
        _app("run", "Running"),
        _app("never", "Never Started", publisher=None),
        _app("stopped", "Stopped"),
    ]
    assert [e._id._id for e in _run(apps)] == ["run"]
