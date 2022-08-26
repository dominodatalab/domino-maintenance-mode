# Entrypoint for Command Line
import click
from domino_maintenance_mode.apps import fetch_apps

@click.group()
def cli():
    pass

@click.command()
def begin():
    print("Begin")
    fetch_apps()

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
    cli()

if __name__=="__main__":
    main()