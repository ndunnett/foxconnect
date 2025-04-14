from argparse import ArgumentParser

import uvloop
from hypercorn.asyncio import serve
from hypercorn.config import Config
from quart import Quart

from app import blueprints, config, extensions, middlewares


def create_app() -> Quart:
    app = Quart("FoxConnect")
    config.init_app(app)
    blueprints.init_app(app)
    extensions.init_app(app)
    middlewares.init_app(app)
    return app


def development_server(host: str, port: int) -> None:
    app = create_app()
    app.run(host, port, debug=True, use_reloader=True)


def production_server(host: str, port: int) -> None:
    app = create_app()
    hypercorn_config = Config()
    hypercorn_config.bind = [f"{host}:{port}"]
    uvloop.run(serve(app, hypercorn_config))


def cli() -> None:
    parser = ArgumentParser()
    parser.add_argument("--host", type=str, help="hostname to listen on")
    parser.add_argument("--port", type=int, help="port to listen on")
    parser.add_argument("--dev", action="store_true", help="use the development server")
    args = parser.parse_args()

    if args.host and args.port:
        server = development_server if args.dev else production_server
        server(args.host, args.port)
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
