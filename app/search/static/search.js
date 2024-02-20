(() => {
    'use strict'

    const pageNumberId = "page";
    const pageLinesId = "lines";
    const resultsId = "results";
    const filtersId = "filters";
    const spinnerId = "spinner";
    const paginationId = "pagination";
    const totalId = "result-total";
    const permalinkId = "permalink";
    const settingsId = "settings";
    const settingsBodyId = "settings-body";
    const settingsApplyId = "settings-apply";
    const settingsCancelId = "settings-cancel";
    const addParameterId = "add-parameter";
    const parameterInputId = "parameter-input";
    const columnListId = "columnList";
    const typingTime = 1000;
    const queryEndpoint = "/api/query";
    const paramEndpoint = "/api/parameters";

    let data = {};
    let parameters = {};
    let typingTimer = {};
    let columns = [];

    document.addEventListener("DOMContentLoaded", () => {
        getLocalSettings();
        parameters = getParameterData();
        document.getElementById(addParameterId).addEventListener("click", addParameter);
        updateColumns();
    }, false);

    async function getParameterData() {
        return await fetch(paramEndpoint).then(r => r.json());
    }

    function getSearchArgs() {
        const columnsLS = JSON.parse(localStorage.getItem("columns"));
        const columnsArg = document.getElementById("columns").value.split(',');

        if (columnsArg.length > 0) {
            columns = columnsArg;
        } else if (columnsLS.length > 0) {
            columns = columnsLS;
        } else {
            columns = ["type", "cp"];
        }
    }

    function getLocalSettings() {
        const localSettings = JSON.parse(localStorage.getItem("columns"));
        columns = localSettings ? localSettings : ["type", "cp"];
    }

    async function updateColumns() {
        document.getElementById(filtersId).replaceChildren(createFilterRow());
        document.getElementById(settingsApplyId).addEventListener("click", applySettings);
        document.getElementById(settingsCancelId).addEventListener("click", cancelSettings);
        updateSettings();
        updateData();
    }

    function updateSettings() {
        let columnList = document.getElementById(columnListId);

        columns.forEach(c => {
            columnList.appendChild(createParameterListItem(c));
        });

        Sortable.create(columnList, { /* options */ });
    }

    function createParameterListItem(c) {
        let item = document.createElement("li");
        item.setAttribute("class", "list-group-item d-flex");
        item.setAttribute("value", c);

        let title = document.createElement("div");
        title.setAttribute("class", "ms-2 me-auto");
        title.textContent = getParameterTitle(c);

        let button = document.createElement("button");
        button.setAttribute("class", "btn-close");
        button.setAttribute("type", "button");
        button.setAttribute("aria-label", "Remove");
        button.addEventListener("click", () => {
            document.getElementById(columnListId).removeChild(item);
        });

        item.appendChild(title);
        item.appendChild(button);
        return item;
    }

    function applySettings() {
        columns = [];

        document.getElementById(columnListId).querySelectorAll("li").forEach(e => {
            columns.push(e.getAttribute("value"));
        });

        localStorage.setItem("columns", JSON.stringify(columns));
        reset();
        updateColumns();
    }

    function cancelSettings() {
        document.getElementById(columnListId).innerHTML = "";
        updateSettings();
    }

    function addParameter() {
        let parameterInput = document.getElementById(parameterInputId);
        let columnList = document.getElementById(columnListId);
        columnList.appendChild(createParameterListItem(parameterInput.value));
    }

    function reset() {
        document.getElementById(resultsId).innerHTML = "";
        document.getElementById(filtersId).innerHTML = "";
        document.getElementById(paginationId).innerHTML = "";
        document.getElementById(columnListId).innerHTML = "";
        document.getElementById(totalId).textContent = "";
        document.getElementById(spinnerId).style.display = "block";
    }

    function getParameterTitle(p) {
        return p.toUpperCase() in parameters ? parameters[p.toUpperCase()].title : p.charAt(0).toUpperCase() + p.slice(1);
    }

    function getParameterDescription(p) {
        return p.toUpperCase() in parameters ? parameters[p.toUpperCase()].description : "";
    }

    async function getData() {
        const query = Object.fromEntries(["compound", "name", ...columns].map(c => {
            return [c, document.getElementById("block_" + c).value];
        }));

        return fetch(queryEndpoint, {
            method: "POST",
            cache: "no-cache",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(query)
        }).then(r => r.json());
    }

    async function updateData() {
        data = await getData();
        document.getElementById(pageNumberId).value = 1;
        updateResults();
        document.getElementById(spinnerId).style.display = "none";
    }

    function createFilterRow() {
        let row = document.createElement("tr");
        let compoundInput = createFloatingLabelInput("block_compound", getParameterTitle("compound"));
        let nameInput = createFloatingLabelInput("block_name", getParameterTitle("name"));
        let span = document.createElement("span");
        span.className = "input-group-text";
        span.textContent = ":";

        let cnDiv = document.createElement("div");
        cnDiv.className = "input-group";
        cnDiv.appendChild(compoundInput);
        cnDiv.appendChild(span);
        cnDiv.appendChild(nameInput);

        let cnColumn = document.createElement("td");
        cnColumn.setAttribute("style", "max-width: 200px;");
        cnColumn.appendChild(cnDiv);
        row.appendChild(cnColumn);

        columns.forEach(c => {
            let column = document.createElement("td");
            column.appendChild(createFloatingLabelInput("block_" + c, getParameterTitle(c)));
            row.appendChild(column);
        });

        row.childNodes.forEach(n => n.addEventListener("keyup", () => {
                clearTimeout(typingTimer);
                typingTimer = setTimeout(updateData, typingTime);
        }));

        row.appendChild(createTableButtons());
        return row;
    }

    function createFloatingLabelInput(id, title, placeholder="") {
        let inputComp = document.createElement("input");
        inputComp.setAttribute("id", id);
        inputComp.setAttribute("type", "text");
        inputComp.setAttribute("class", "form-control");
        inputComp.setAttribute("placeholder", placeholder);

        let label = document.createElement("label");
        label.setAttribute("for", id);
        label.textContent = title;

        let div = document.createElement("div");
        div.setAttribute("class", "form-floating");
        div.appendChild(inputComp);
        div.appendChild(label);
        return div;
    }

    function createTableButtons() {
        let link_button = document.createElement("button");
        link_button.setAttribute("class", "btn btn-dark btn-lg");
        link_button.setAttribute("type", "button");

        let link_icon = document.createElement("i");
        link_icon.setAttribute("class", "bi bi-link");
        link_button.appendChild(link_icon);

        let cog_button = document.createElement("button");
        cog_button.setAttribute("class", "btn btn-dark btn-lg");
        cog_button.setAttribute("type", "button");
        cog_button.setAttribute("data-bs-toggle", "modal");
        cog_button.setAttribute("data-bs-target", "#" + settingsId);

        let cog_icon = document.createElement("i");
        cog_icon.setAttribute("class", "bi bi-gear-fill");
        cog_button.appendChild(cog_icon);

        let column = document.createElement("td");
        column.setAttribute("class", "align-middle text-end");
        column.appendChild(link_button);
        column.appendChild(cog_button);
        return column;
    }

    async function updateResults() {
        const pageNumber = document.getElementById(pageNumberId).value * 1;
        const linesPerPage = document.getElementById(pageLinesId).value * 1;
        const pageStartIndex = (pageNumber - 1) * linesPerPage;
        const pageData = data.slice(pageStartIndex, pageStartIndex + linesPerPage + 1)
        const totalPages = Math.ceil(data.length / linesPerPage);

        // update results
        let resultRows = pageData.map(result => createResultRow(result, columns));
        document.getElementById(resultsId).replaceChildren(...resultRows);

        // update total
        document.getElementById(totalId).textContent = data.length == 1 ? "1 result" : data.length.toLocaleString() + " results";

        // update pagination
        let paginationList = createPaginationList(pageNumber, totalPages);
        document.getElementById(paginationId).replaceChildren(paginationList);
    }

    function createResultRow(result) {
        // create row for given data point and add button links to diagram/detail
        // <tr>
        //   {data columns}
        //   <td>
        //     <div class="btn-group btn-group-sm float-end" role="group" aria-label="Links">
        //       <a href="{diagram_url}" role="button" class="btn btn-outline-secondary btn-results">Diagram</a>
        //       <a href="{detail_url}" role="button" class="btn btn-outline-secondary btn-results">Detail</a>
        //     </div>
        //   </td>
        // </tr>

        let row = document.createElement("tr");

        let nameColumn = document.createElement("td");
        nameColumn.textContent = result["compound"] + ":" + result["name"];
        row.appendChild(nameColumn);

        columns.forEach((c) => {
            let column = document.createElement("td");
            column.textContent = result[c];
            row.appendChild(column);
        });

        let diagram_button = document.createElement("a");
        diagram_button.setAttribute("href", result["diagram_url"]);
        diagram_button.setAttribute("role", "button");
        diagram_button.setAttribute("class", "btn btn-outline-secondary btn-results");
        diagram_button.textContent = "Diagram";

        let detail_button = document.createElement("a");
        detail_button.setAttribute("href", result["detail_url"]);
        detail_button.setAttribute("role", "button");
        detail_button.setAttribute("class", "btn btn-outline-secondary btn-results");
        detail_button.textContent = "Detail";

        let column = document.createElement("td");
        let group = document.createElement("div");
        group.setAttribute("role", "group");
        group.setAttribute("class", "btn-group btn-group-sm float-end");
        group.setAttribute("aria-label", "Links");

        group.appendChild(diagram_button);
        group.appendChild(detail_button);
        column.appendChild(group);
        row.appendChild(column);

        return row;
    }

    function createPaginationList(pageNumber, totalPages) {
        // create pagination list for given current page number and total number of pages
        // <ul class="pagination pagination-sm justify-content-center">
        //   {list items}
        // </ul>

        let list = document.createElement("ul");
        list.className = "pagination pagination-sm justify-content-center";

        // set indices; include first and last page, then current page +/- 2
        let paginationIndices = new Set([
            1, pageNumber, totalPages,
            pageNumber - 1, pageNumber + 1,
            pageNumber - 2, pageNumber + 2
        ]);

        // sort and filter indices
        paginationIndices = [...paginationIndices].filter((i) => {
            return i > 0 && i <= totalPages;
        }).sort((a, b) => {
            return (a * 1) > (b * 1) ? 1 : (a == b ? 0 : -1);
        });

        // add back button
        list.appendChild(createPaginationItem(pageNumber - 1, false, pageNumber == 1, "←"));

        // add page number buttons
        for (let i = 0; i < paginationIndices.length; i++) {
            // add disabled ... button if there are gaps in page numbers
            if (paginationIndices[i] - paginationIndices[i - 1] > 1) {
                list.appendChild(createPaginationItem(0, false, true, "..."));
            }

            list.appendChild(createPaginationItem(paginationIndices[i], pageNumber == paginationIndices[i], false));
        }

        // add forward button
        list.appendChild(createPaginationItem(pageNumber + 1, false, pageNumber >= totalPages, "→"));

        return list;
    }

    function createPaginationItem(number, active = false, disabled = false, label = "") {
        // create pagination item for given page number (optional title) and add event listener to update page
        // <li class="page-item {active/disabled}">
        //   <button class="page-link">{number/title}</button>
        // </li>

        let item = document.createElement("li");
        item.className = "page-item";
        item.className += active ? " active" : "";
        item.className += disabled ? " disabled" : "";

        let button = document.createElement("button");
        button.className = "page-link"
        button.textContent = label ? label : number;

        item.appendChild(button);

        if (!disabled && !active) {
            item.addEventListener("click", () => {
                document.getElementById(pageNumberId).value = number;
                updateResults();
            });
        }

        return item;
    }
})()
