from typing import Any

from pyhtmx import HtmxRequestHelper, HtmxResponseHelper, htmx_node_modules
from quart import Blueprint, Quart
from quart import make_response as base_make_response
from quart import request as base_request
from quart.wrappers import Request as BaseRequest
from quart.wrappers import Response as BaseResponse
from werkzeug.exceptions import BadRequest


class Htmx:
    """This is a Quart extension to provide server side HTMX functionality.

    Distribution files from the HTMX Node package are served as static files
    via a blueprint called "htmx", and the Request and Response classes are
    wrapped to provide helper methods for HTMX functionality.
    """

    def __init__(self, app: Quart | None = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Quart) -> None:
        """Initialises the extension for a given Quart instance.

        * Registers the extension with the app
        * Overrides the Request and Response classes
        * Creates the blueprint to serve static files
        """

        blueprint = Blueprint("htmx", __name__, static_folder=htmx_node_modules(), url_prefix="/htmx")
        app.register_blueprint(blueprint)
        app.request_class = Request
        app.response_class = Response
        app.extensions["htmx"] = self


class BadHtmxRequest(BadRequest):
    """*400* `Bad Request`

    Raise if a non-HTMX request is received at an endpoint which is not meant to handle non-HTMX requests.
    """

    description = "Requests to this endpoint must be made via HTMX."


class Request(BaseRequest):
    """Wrapper around base Quart request to add HTMX helper functions."""

    @property
    def htmx(self) -> HtmxRequestHelper:
        """Provides convenient access to [HTMX request headers](https://htmx.org/docs/#request-headers)."""

        if not hasattr(self, "_htmx"):
            self._htmx = HtmxRequestHelper(lambda key: self.headers.get(key))

        return self._htmx


class Response(BaseResponse):
    """Wrapper around base Quart response to add HTMX helper functions."""

    @property
    def htmx(self) -> HtmxResponseHelper:
        """Allows setting [HTMX response headers](https://htmx.org/docs/#response-headers) easily via methods."""

        if not hasattr(self, "_htmx"):
            self._htmx = HtmxResponseHelper(lambda key, value: (self.headers.set(key, value), self)[1])

        return self._htmx


# reannotations to add HTMX type hints
async def make_response(*args: Any) -> Response:  # type: ignore
    """Create a response, a simple wrapper function.

    This is most useful when you want to alter a Response before
    returning it, for example:

    .. code-block:: python
        response = await make_response(render_template("index.html"))
        response.headers["X-Header"] = "Something"
        response.hx_trigger("event")
    """
    ...


make_response.__code__ = base_make_response.__code__
request: Request = base_request  # type: ignore
