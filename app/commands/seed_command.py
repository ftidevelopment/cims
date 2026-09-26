import click

from flask.cli import with_appcontext

from app.services.seeder_service import (
    SeederService,
)


@click.command("seed")
@with_appcontext
def seed():

    print("=" * 50)
    print("Seed Master Data")
    print("=" * 50)

    service = SeederService()

    result = service.seed_all()

    click.echo(result.message)


@click.command("seed-admin")
@with_appcontext
def seed_admin():

    print("=" * 50)
    print("Create Admin")
    print("=" * 50)

    service = SeederService()

    result = service.create_admin()

    click.echo(result.message)