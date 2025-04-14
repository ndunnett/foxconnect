from uuid import uuid4

from dotenv import dotenv_values
from quart import Quart


def init_app(app: Quart) -> None:
    app.config["FOXCONNECT_CONTEXT"] = {"navbar_links": {}}
    app.config.from_prefixed_env()
    app.config.from_mapping(dotenv_values())

    if app.config["SECRET_KEY"] is None:
        app.logger.warning("Secret key not found in environment, generating random key.")
        app.config["SECRET_KEY"] = str(uuid4())
