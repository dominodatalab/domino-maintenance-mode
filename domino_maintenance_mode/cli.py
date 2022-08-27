# Entrypoint for Command Line
import logging
import os

import click

from domino_maintenance_mode.apps import Interface as AppInterface
from domino_maintenance_mode.model_apis import Interface as ModelApiInterface
from domino_maintenance_mode.scheduled_jobs import (
    Interface as ScheduledJobInterface,
)
from domino_maintenance_mode.shutdown_manager import ShutdownManager

# from domino_maintenance_mode.jobs import Interface as JobInterface
from domino_maintenance_mode.workspaces import Interface as WorkspaceInterface

EXECUTION_INTERFACES = [
    AppInterface(),
    ModelApiInterface(),
    WorkspaceInterface(),
    ScheduledJobInterface(),
]


@click.group()
def cli():
    pass


@click.command()
def begin():
    print("Begin")
    shutdown_manager = ShutdownManager()
    for execution_interface in EXECUTION_INTERFACES:
        shutdown_manager.shutdown(execution_interface)


@click.command()
def restore():
    print("Restore")


@click.command()
def shutdown_jobs():
    print("Shutdown Jobs")


cli.add_command(begin)
cli.add_command(restore)
cli.add_command(shutdown_jobs)


def main():
    logging.basicConfig(
        level=logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO"))
    )
    cli()


if __name__ == "__main__":
    main()
