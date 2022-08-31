# Entrypoint for Command Line
import json
import logging
import os
from dataclasses import asdict
from typing import Any, Dict, List

import click

from domino_maintenance_mode.interfaces.apps import Interface as AppInterface
from domino_maintenance_mode.execution_interface import ExecutionInterface
from domino_maintenance_mode.manager import ShutdownManager
from domino_maintenance_mode.interfaces.model_apis import Interface as ModelApiInterface
from domino_maintenance_mode.projects import fetch_projects
from domino_maintenance_mode.interfaces.scheduled_jobs import (
    Interface as ScheduledJobInterface,
)
from domino_maintenance_mode.interfaces.workspaces import Interface as WorkspaceInterface

__INTERFACES: List[ExecutionInterface[Any]] = [
    AppInterface(),
    ModelApiInterface(),
    WorkspaceInterface(),
    ScheduledJobInterface(),
]

EXECUTION_INTERFACES: Dict[str, ExecutionInterface[Any]] = {
    interface.singular(): interface for interface in __INTERFACES
}


def __load_state(f) -> Dict[str, Any]:
    state = {}
    for k, v in json.load(f).items():
        interface = EXECUTION_INTERFACES[k]
        state[k] = list(map(interface.execution_from_dict, v))
    return state


@click.group()
def cli():
    pass


@click.command()
@click.argument("output", type=click.File("x"))
def snapshot(output):
    """Take a snapshot of running executions.

    OUTPUT: Path to write snapshot file to. Must not exist.
    """
    projects = fetch_projects()
    state = {
        interface.singular(): list(
            map(asdict, interface.list_running(projects))
        )
        for interface in EXECUTION_INTERFACES.values()
    }
    json.dump(state, output)


cli.add_command(snapshot)


@click.command()
@click.argument("snapshot", type=click.File("r"))
@click.option(
    "-b",
    "--batch-size",
    type=click.IntRange(min=0),
    default=5,
    help=(
        "Number of concurrent requests to make when "
        "stopping executions or polling for status."
    ),
)
@click.option(
    "-i",
    "--batch-interval_s",
    type=click.IntRange(min=0),
    default=30,
    help="Interval to wait between batches of API calls.",
)
@click.option(
    "-m",
    "--max-failures",
    type=click.IntRange(min=0),
    default=5,
    help=(
        "Maximum number of failed API calls for a given "
        "execution before it is reported for manual cleanup."
    ),
)
@click.option(
    "-g",
    "--grace-period-s",
    type=click.IntRange(min=0),
    default=600,
    help="Amount of time to wait for executions to complete.",
)
def shutdown(snapshot, **kwargs):
    """Stop running Apps, Model APIs, Durable Workspaces, and Scheduled Jobs.

    SNAPSHOT : The path to snapshot output from 'dmm snapshot'.
    """
    state = __load_state(snapshot)
    shutdown_manager = ShutdownManager(**kwargs)
    for execution_interface in EXECUTION_INTERFACES.values():
        shutdown_manager.shutdown(execution_interface, state)


cli.add_command(shutdown)


@click.command()
@click.argument("snapshot", type=click.File("r"))
def restore(snapshot):
    """Restore previously running Apps, Model APIs, and Scheduled Jobs.

    SNAPSHOT : The path to snapshot output from 'dmm snapshot'.
    """
    # state = __load_state(snapshot)
    for interface in EXECUTION_INTERFACES.values():
        if interface.is_restartable():
            # TODO
            pass


cli.add_command(restore)


@click.command()
@click.option(
    "--discard", default=False, help="Discard Job results when stopping."
)
def stop_jobs(discard: bool):
    """Stop running Jobs."""
    print("Shutdown Jobs")


cli.add_command(stop_jobs)


@click.command()
def stop_builds():
    """Stop running Image Builds."""
    print("Shutdown Builds")


cli.add_command(stop_builds)


def main():
    logging.basicConfig(
        level=logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO"))
    )
    cli()


if __name__ == "__main__":
    main()
