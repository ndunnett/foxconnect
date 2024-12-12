from dataclasses import dataclass
from functools import cache

from quart import url_for
from quart_foxdata import get_parameter
from quart_foxdata.models import Meta


@cache
def hx_attributes() -> str:
    return f'hx-post="{url_for('search.table')}" hx-target="#table-container" hx-swap="innerHTML transition:true"'


@dataclass(frozen=True)
class PaginationButton:
    label: str | None = None
    value: int | None = None
    active: bool = False
    disabled: bool = False

    def __str__(self) -> str:
        hx = (
            f""" {hx_attributes()} hx-vals='{{"page": {self.value}}}'"""
            if self.value is not None and not self.active
            else ""
        )

        label = self.label if self.label is not None else self.value if self.value is not None else "..."
        active = " active" if self.active else ""
        disabled = " disabled" if self.disabled else ""
        return f'<button class="page-link{active}{disabled}"{hx}>{label}</button>'


@dataclass(frozen=True)
class SearchInput:
    field: str
    value: str | None = None

    def __str__(self) -> str:
        label = p.name if (p := get_parameter(self.field.upper())) else "." + self.field.upper()
        value = f'value="{self.value}" ' if self.value is not None else ""

        return f"""
        <div class="form-floating">
            <input id="query-{self.field}" class="form-control" type="text" name="query-{self.field}"
                {hx_attributes()} hx-trigger="input changed delay:2000ms, keyup[key=='Enter'] changed"
                placeholder="" {value}/>
            <label for="query-{self.field}">{label}</label>
        </div>
        """


@dataclass(frozen=True)
class ParameterInfo:
    name: str

    def __str__(self) -> str:
        if p := get_parameter(self.name):
            title = p.name

            src = (
                """<span class="text-bg-primary rounded-1 px-1 me-1">metadata</span>"""
                if isinstance(p.source, Meta)
                else f"""<span class="text-bg-secondary rounded-1 px-1 me-1">.{p.source}</span>"""
            )

            desc = p.description
        else:
            title = f".{self.name}"
            src = """<span class="text-bg-danger rounded-1 px-1 me-1">unknown</span>"""
            desc = "parameter not recognised"

        return f"""
        <h6 class="mb-1">{title}</h6>
        <small class="mb-0">{src}{desc}</small>
        """


@dataclass(frozen=True)
class AddableParameter:
    name: str

    def __str__(self) -> str:
        button = f"""
        <button id="add-{self.name}" type="button" class="btn btn-sm btn-success bi bi-plus-lg"
            hx-get="{url_for("search.add_parameter")}" hx-target="#parameterList" hx-swap="beforeend">
        </button>
        """

        return f"""
        <li class="list-group-item">
            <div class="d-flex w-100 justify-content-between align-items-center">
                <div class="col">{ParameterInfo(self.name)}</div>
                {button}
            </div>
        </li>
        """


@dataclass(frozen=True)
class RemovableParameter:
    name: str
    pinned: bool = False

    def __str__(self) -> str:
        input_field = f"""<input type="hidden" id="parameter-{self.name}" name="parameter-{self.name}" value="" />"""

        if self.pinned:
            li_classes = " pinned"
            handle = ""
            button = ""
        else:
            li_classes = " draggable"
            handle = """<button type="button" class="btn btn-lg p-0 m-0 me-2 bi bi-list handle"></button>"""
            button = f"""
            <button type="button" class="btn btn-sm btn-danger bi bi-x-lg"
                hx-delete="{url_for("search.delete")}" hx-target="closest li" hx-swap="delete">
            </button>
            """

        return f"""
        <li class="list-group-item{li_classes}">
            {input_field}
            <div class="d-flex w-100 justify-content-between align-items-center">
                {handle}
                <div class="col">{ParameterInfo(self.name)}</div>
                {button}
            </div>
        </li>
        """
