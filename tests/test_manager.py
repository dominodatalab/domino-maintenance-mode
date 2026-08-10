from unittest import mock

import pytest

from domino_maintenance_mode.execution_interface import Execution
from domino_maintenance_mode.manager import Manager


@pytest.fixture
def interface():
    """An execution interface that records what `Manager` asks it to stop."""

    class FakeInterface:
        def __init__(self):
            self.stopped: list = []

        def singular(self):
            return "App"

        def stop(self, _id):
            self.stopped.append(_id)

        def is_stopped(self, _id):
            return True

    return FakeInterface()


@pytest.fixture
def executions():
    # `Manager` pops from the list it is given, so each test needs its own.
    return [Execution("app-1", "app-one", "alice")]


def test_declining_the_prompt_stops_nothing(interface, executions):
    with mock.patch("builtins.input", return_value="n"):
        Manager().stop(interface, executions)

    assert interface.stopped == []


@mock.patch("domino_maintenance_mode.manager.time.sleep")
def test_yes_stops_without_prompting(_sleep, interface, executions):
    with mock.patch("builtins.input", side_effect=AssertionError("prompted")):
        Manager(yes=True).stop(interface, executions)

    assert interface.stopped == ["app-1"]
