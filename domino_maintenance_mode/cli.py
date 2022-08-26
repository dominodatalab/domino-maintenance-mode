# Entrypoint for Command Line
import logging
import os

import click

from domino_maintenance_mode.apps import AppInterface
from domino_maintenance_mode.shutdown_manager import ShutdownManager


@click.group()
def cli():
    pass


@click.command()
def begin():
    print("Begin")

    app_manager = ShutdownManager(AppInterface())
    app_manager.shutdown()


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
