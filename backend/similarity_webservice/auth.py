import contextlib
import click
import datetime
import flask
import secrets

from similarity_webservice.model import db, add_new_apikey


@contextlib.contextmanager
def faked_app():
    app = flask.Flask("similarity_webservice")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///similarity_webservice.db"
    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield


@click.group()
def auth():
    pass


@auth.command()
@click.option(
    "--name",
    default="default",
    help="Human readable name of the API key.",
    show_default=True,
)
def create(name):
    """Create a new API key."""

    key = secrets.token_urlsafe(64)

    with faked_app():
        add_new_apikey(name=name, key=key)

    click.echo(f"Created the following API key:\n\n{key}\n")
    click.echo("It gives full (potentially destructive) access to our entire service.")
    click.echo("Please only share this with trusted parties through secure channels.")
    click.echo(
        "You can revoke this key at any time through the 'similarity_auth delete' command"
    )


@auth.command()
def list():
    """List all API keys."""

    with faked_app():
        keys = ApiKey.query.all()

    click.echo(f"There are currently {len(keys)} active API keys:")
    for key in keys:
        click.echo(f"#{str(key.id).zfill(4)} {key.name} (issued {key.created})")


@auth.command()
@click.argument("id", type=int)
def delete(id):
    """Delete an API key."""

    with faked_app():
        key = ApiKey.query.filter_by(id=id).first()
        if key is None:
            click.echo(f"Could not find API key with id {id}")
            return

        db.session.delete(key)
        db.session.commit()

    click.echo(f"Successfully Deleted API key with id {id}")


if __name__ == "__main__":
    auth()
