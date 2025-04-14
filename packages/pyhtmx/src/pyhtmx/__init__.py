"""
This module contains the HTMX distribution files and helper functionality.
"""

import importlib.resources
import json
from collections.abc import Callable
from enum import StrEnum
from importlib.abc import Traversable
from typing import Any, Literal

__all__ = ("HtmxRequestHelper", "HtmxResponseHelper", "HtmxSwapStyle", "htmx_node_modules")


def htmx_node_modules() -> Traversable:
    """Returns a traversable to the `node_modules` directory for HTMX distribution files."""
    return importlib.resources.files("pyhtmx") / "node_modules"


HTMX_TRUE = "true"
HTMX_FALSE = "false"


class HtmxSwapStyle(StrEnum):
    """Enum to represent HTMX swap styles.

    All enumerations correspond to the [hx-swap](https://htmx.org/attributes/hx-swap/) attribute:

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


class HtmxRequestHelper:
    """Provides convenient access to [HTMX request headers](https://htmx.org/docs/#request-headers)."""

    _get_header: Callable[[str], Any]

    def __init__(self, get_header: Callable[[str], Any]) -> None:
        """Construct using a function to get the header value from the request object."""
        self._get_header = get_header

    @property
    def boosted(self) -> bool:
        """Indicates that the request is via an element using hx-boost."""
        return self._get_header("HX-Boosted") == HTMX_TRUE

    @property
    def current_url(self) -> str | None:
        """Returns the current URL of the browser."""
        return self._get_header("HX-Current-URL")

    @property
    def history_restore_request(self) -> bool:
        """Returns true if the request is for history restoration after a miss in the local history cache."""
        return self._get_header("HX-History-Restore-Request") == HTMX_TRUE

    @property
    def prompt(self) -> str | None:
        """Returns the user response to an hx-prompt."""
        return self._get_header("HX-Prompt")

    @property
    def request(self) -> bool:
        """Always true for a request sent by HTMX."""
        return self._get_header("HX-Request") == HTMX_TRUE

    @property
    def target(self) -> str | None:
        """Returns the id of the target element if it exists."""
        return self._get_header("HX-Target")

    @property
    def trigger_name(self) -> str | None:
        """Returns the name of the triggered element if it exists."""
        return self._get_header("HX-Trigger-Name")

    @property
    def trigger(self) -> str | None:
        """Returns the id of the triggered element if it exists."""
        return self._get_header("HX-Trigger")


class HtmxResponseHelper[T]:
    """Allows setting [HTMX response headers](https://htmx.org/docs/#response-headers) easily via methods."""

    _set_header: Callable[[str, str], T]

    def __init__(self, set_header: Callable[[str, str], T]) -> None:
        """Construct using a function to set a header value on the response object."""
        self._set_header = set_header

    def location(self, path: str | None = None, **kwargs: dict[str, str]) -> T:
        """Allows you to do a client-side redirect that does not do a full page reload.

        Uses [HX-Location](https://htmx.org/headers/hx-location/) response header.
        """

        if len(kwargs) == 0 and path is not None:
            return self._set_header("HX-Location", path)
        else:
            return self._set_header("HX-Location", json.dumps({"path": path} | kwargs))

    def push_url(self, url: str | Literal[False]) -> T:
        """Pushes a new url into the history stack.

        Uses [HX-Push-Url](https://htmx.org/headers/hx-push-url/) response header.
        """

        if url is False:
            return self._set_header("HX-Push-Url", HTMX_FALSE)
        else:
            return self._set_header("HX-Push-Url", url)

    def redirect(self, url: str) -> T:
        """Can be used to do a client-side redirect to a new location.

        Uses [HX-Redirect](https://htmx.org/headers/hx-redirect/) response header.
        """

        return self._set_header("HX-Redirect", url)

    def refresh(self, *, refresh: bool = True) -> T:
        """If true the client-side will do a full refresh of the page.

        Uses `HX-Refresh` response header.
        """

        return self._set_header("HX-Refresh", HTMX_TRUE if refresh else HTMX_FALSE)

    def replace_url(self, url: str | Literal[False]) -> T:
        """Replaces the current URL in the location bar.

        Uses [HX-Replace-Url](https://htmx.org/headers/hx-replace-url/) response header.
        """

        if url is False:
            return self._set_header("HX-Replace-Url", HTMX_FALSE)
        else:
            return self._set_header("HX-Replace-Url", url)

    def reswap(self, swap_style: HtmxSwapStyle) -> T:
        """Allows you to specify how the response will be swapped.

        Uses [HX-Reswap](https://htmx.org/attributes/hx-swap/) response header.
        """

        return self._set_header("HX-Reswap", swap_style)

    def retarget(self, selector: str) -> T:
        """A CSS selector that updates the target of the content update to a different element on the page.

        Uses `HX-Retarget` response header.
        """

        return self._set_header("HX-Retarget", selector)

    def reselect(self, selector: str) -> T:
        """A CSS selector that allows you to choose which part of the response is used to be swapped in.

        Uses `HX-Reselect` response header.
        """

        return self._set_header("HX-Reselect", selector)

    def trigger(self, trigger: str | dict) -> T:
        """Allows you to trigger client-side events.

        Uses [HX-Trigger](https://htmx.org/headers/hx-trigger/) response header.
        """

        if isinstance(trigger, str):
            return self._set_header("HX-Trigger", trigger)
        else:
            return self._set_header("HX-Trigger", json.dumps(trigger))

    def trigger_after_settle(self, trigger: str | dict) -> T:
        """Allows you to trigger client-side events after the settle step.

        Uses [HX-Trigger-After-Settle](https://htmx.org/headers/hx-trigger/) response header.
        """

        if isinstance(trigger, str):
            return self._set_header("HX-Trigger-After-Settle", trigger)
        else:
            return self._set_header("HX-Trigger-After-Settle", json.dumps(trigger))

    def trigger_after_swap(self, trigger: str | dict) -> T:
        """Allows you to trigger client-side events after the swap step.

        Uses [HX-Trigger-After-Swap](https://htmx.org/headers/hx-trigger/) response header.
        """

        if isinstance(trigger, str):
            return self._set_header("HX-Trigger-After-Swap", trigger)
        else:
            return self._set_header("HX-Trigger-After-Swap", json.dumps(trigger))
