"""
This module contains the HTMX Quart extension and associated functionality.
"""

from __future__ import annotations

import importlib.resources
import json
from enum import StrEnum
from typing import Any, Literal

from quart import Blueprint, Quart
from quart import make_response as base_make_response
from quart import request as base_request
from quart.wrappers import Request as BaseRequest
from quart.wrappers import Response as BaseResponse
from werkzeug.exceptions import BadRequest

__all__ = ("HTMX", "BadHtmxRequest", "Request", "Response", "make_response", "request")

HTMX_TRUE = "true"
HTMX_FALSE = "false"


class BadHtmxRequest(BadRequest):
    """*400* `Bad Request`

    Raise if the browser sends something to an endpoint which is not meant to handle non-HTMX requests.
    """

    description = "Requests to this endpoint must be made via HTMX."


class HTMX:
    """This is a Quart extension to provide server side HTMX functionality.

    Distribution files from the HTMX node module are served as static files
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

        app.extensions["htmx"] = self
        app.request_class = Request
        app.response_class = Response

        node_modules = importlib.resources.files("quart_htmx") / "node_modules"
        blueprint = Blueprint("htmx", __name__, static_folder=node_modules, url_prefix="/htmx")
        app.register_blueprint(blueprint)


class Request(BaseRequest):
    """Provides convenient access to [HTMX request headers](https://htmx.org/docs/#request-headers)."""

    @property
    def hx_boosted(self) -> bool:
        """Indicates that the request is via an element using hx-boost."""
        return self.headers.get("HX-Boosted") == HTMX_TRUE

    @property
    def hx_current_url(self) -> str | None:
        """Returns the current URL of the browser."""
        return self.headers.get("HX-Current-URL")

    @property
    def hx_history_restore_request(self) -> bool:
        """Returns true if the request is for history restoration after a miss in the local history cache."""
        return self.headers.get("HX-History-Restore-Request") == HTMX_TRUE

    @property
    def hx_prompt(self) -> str | None:
        """Returns the user response to an hx-prompt."""
        return self.headers.get("HX-Prompt")

    @property
    def hx_request(self) -> bool:
        """Always true for a request sent by HTMX."""
        return self.headers.get("HX-Request") == HTMX_TRUE

    @property
    def hx_target(self) -> str | None:
        """Returns the id of the target element if it exists."""
        return self.headers.get("HX-Target")

    @property
    def hx_trigger_name(self) -> str | None:
        """Returns the name of the triggered element if it exists."""
        return self.headers.get("HX-Trigger-Name")

    @property
    def hx_trigger(self) -> str | None:
        """Returns the id of the triggered element if it exists."""
        return self.headers.get("HX-Trigger")


class SwapStyle(StrEnum):
    """Enum to represent HTMX swap styles.

    All options correspond to the [hx-swap](https://htmx.org/attributes/hx-swap/) attribute:

    * `inner_html` - Replace the inner html of the target element
    * `outer_html` - Replace the entire target element with the response
    * `text_content` - Replace the text content of the target element, without parsing the response as HTML
    * `before_begin` - Insert the response before the target element
    * `after_begin` - Insert the response before the first child of the target element
    * `before_end` - Insert the response after the last child of the target element
    * `after_end` - Insert the response after the target element
    * `delete` - Deletes the target element regardless of the response
    * `none` - Does not append content from response (out of band items will still be processed)
    """

    inner_html = "innerHTML"
    outer_html = "outerHTML"
    text_content = "textContent"
    before_begin = "beforeBegin"
    after_begin = "afterBegin"
    before_end = "beforeEnd"
    after_end = "afterEnd"
    delete = "delete"
    none = "none"


class Response(BaseResponse):
    """Allows setting [HTMX response headers](https://htmx.org/docs/#response-headers) easily via methods."""

    def hx_location(self, path: str | None = None, **kwargs: dict[str, str]) -> Response:
        """Allows you to do a client-side redirect that does not do a full page reload.

        Uses [HX-Location](https://htmx.org/headers/hx-location/) response header.
        """

        if len(kwargs) == 0 and path is not None:
            self.headers.set("HX-Location", path)
        else:
            self.headers.set("HX-Location", json.dumps({"path": path} | kwargs))
        return self

    def hx_push_url(self, url: str | Literal[False]) -> Response:
        """Pushes a new url into the history stack.

        Uses [HX-Push-Url](https://htmx.org/headers/hx-push-url/) response header.
        """

        if url is False:
            self.headers.set("HX-Push-Url", HTMX_FALSE)
        else:
            self.headers.set("HX-Push-Url", url)
        return self

    def hx_redirect(self, url: str) -> Response:
        """Can be used to do a client-side redirect to a new location.

        Uses [HX-Redirect](https://htmx.org/headers/hx-redirect/) response header.
        """

        self.headers.set("HX-Redirect", url)
        return self

    def hx_refresh(self, refresh: bool = True) -> Response:  # noqa: FBT001, FBT002
        """If true the client-side will do a full refresh of the page.

        Uses `HX-Refresh` response header.
        """

        self.headers.set("HX-Refresh", HTMX_TRUE if refresh else HTMX_FALSE)
        return self

    def hx_replace_url(self, url: str | Literal[False]) -> Response:
        """Replaces the current URL in the location bar.

        Uses [HX-Replace-Url](https://htmx.org/headers/hx-replace-url/) response header.
        """

        if url is False:
            self.headers.set("HX-Replace-Url", HTMX_FALSE)
        else:
            self.headers.set("HX-Replace-Url", url)
        return self

    def hx_reswap(self, swap_style: SwapStyle) -> Response:
        """Allows you to specify how the response will be swapped.

        Uses [HX-Reswap](https://htmx.org/attributes/hx-swap/) response header.
        """

        self.headers.set("HX-Reswap", swap_style)
        return self

    def hx_retarget(self, selector: str) -> Response:
        """A CSS selector that updates the target of the content update to a different element on the page.

        Uses `HX-Retarget` response header.
        """

        self.headers.set("HX-Retarget", selector)
        return self

    def hx_reselect(self, selector: str) -> Response:
        """A CSS selector that allows you to choose which part of the response is used to be swapped in.

        Uses `HX-Reselect` response header.
        """

        self.headers.set("HX-Reselect", selector)
        return self

    def hx_trigger(self, trigger: str | dict) -> Response:
        """Allows you to trigger client-side events.

        Uses [HX-Trigger](https://htmx.org/headers/hx-trigger/) response header.
        """

        if isinstance(trigger, str):
            self.headers.set("HX-Trigger", trigger)
        else:
            self.headers.set("HX-Trigger", json.dumps(trigger))
        return self

    def hx_trigger_after_settle(self, trigger: str | dict) -> Response:
        """Allows you to trigger client-side events after the settle step.

        Uses [HX-Trigger-After-Settle](https://htmx.org/headers/hx-trigger/) response header.
        """

        if isinstance(trigger, str):
            self.headers.set("HX-Trigger-After-Settle", trigger)
        else:
            self.headers.set("HX-Trigger-After-Settle", json.dumps(trigger))
        return self

    def hx_trigger_after_swap(self, trigger: str | dict) -> Response:
        """Allows you to trigger client-side events after the swap step.

        Uses [HX-Trigger-After-Swap](https://htmx.org/headers/hx-trigger/) response header.
        """

        if isinstance(trigger, str):
            self.headers.set("HX-Trigger-After-Swap", trigger)
        else:
            self.headers.set("HX-Trigger-After-Swap", json.dumps(trigger))
        return self


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
