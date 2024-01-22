from similarity_webservice.app import app

import click


@click.command()
@click.option("--host", default="localhost", help="Host to bind to.", show_default=True)
@click.option("--port", default=5000, help="Port to bind to.", show_default=True)
def main(host, port):
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
