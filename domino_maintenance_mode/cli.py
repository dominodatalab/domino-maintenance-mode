# Entrypoint for Command Line
import logging
import os
from typing import Any, List, Optional

import click

from domino_maintenance_mode.apps import Interface as AppInterface
from domino_maintenance_mode.model_apis import Interface as ModelApiInterface
from domino_maintenance_mode.scheduled_jobs import (
    Interface as ScheduledJobInterface,
)
from domino_maintenance_mode.shutdown_manager import (
    ExecutionTypeInterface,
    ShutdownManager,
)
from domino_maintenance_mode.workspaces import Interface as WorkspaceInterface

EXECUTION_INTERFACES: List[ExecutionTypeInterface[Any]] = [
    AppInterface(),
    ModelApiInterface(),
    WorkspaceInterface(),
    ScheduledJobInterface(),
]


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "--output",
    default=None,
    help="Specify particular output path (will not overwrite).",
    type=click.Path(exists=False),
)
def snapshot(output: Optional[str]):
    """Take a snapshot of running executions."""
    print("Snapshot")


cli.add_command(snapshot)


@click.command()
@click.argument("snapshot_path", type=click.File("r"))
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
def shutdown(snapshot: str, **kwargs):
    """Stop running Apps, Model APIs, Durable Workspaces, and Scheduled Jobs.

    SNAPSHOT_PATH : The path to snapshot output from 'dmm snapshot'.
    """
    print("Shutdown")
    print(kwargs)
    shutdown_manager = ShutdownManager(**kwargs)
    for execution_interface in EXECUTION_INTERFACES:
        shutdown_manager.shutdown(execution_interface)


cli.add_command(shutdown)


@click.command()
@click.argument("snapshot_path", type=click.File("r"))
def restore(snapshot_path: str):
    """Restore previously running Apps, Model APIs, and Scheduled Jobs."""
    print("Restore")


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
