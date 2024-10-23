from dataclasses import dataclass
from functools import cache
from typing import Optional

from quart import url_for


@cache
def hx_attributes() -> str:
    return f'hx-post="{url_for('search.table_body')}" hx-target="#table-body" hx-swap="outerHTML transition:true"'


@dataclass(frozen=True)
class PaginationButton:
    label: Optional[str] = None
    value: Optional[int] = None
    active: bool = False
    disabled: bool = False

    def __str__(self):
        label = self.label if self.label is not None else self.value if self.value is not None else "..."
        hx = f' {hx_attributes()} hx-vars="page:{self.value}"' if self.value is not None and not self.active else ""
        active = " active" if self.active else ""
        disabled = " disabled" if self.disabled else ""
        return f'<button class="page-link{active}{disabled}"{hx}>{label}</button>'


@dataclass(frozen=True)
class SearchInput:
    field: str
    label: Optional[str] = None
    value: Optional[str] = None

    def __str__(self):
        label = self.label if self.label is not None else self.field.capitalize()
        value = f'value="{self.value}" ' if self.value is not None else ""

        return f"""
        <div class="form-floating">
            <input id="query-{self.field}" class="form-control" type="text" name="query-{self.field}"
                {hx_attributes()} hx-trigger="keyup changed delay:500ms" placeholder="" {value}/>
            <label for="query-{self.field}">{label}</label>
        </div>
        """
