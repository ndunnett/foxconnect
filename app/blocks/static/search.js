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
        // get settings locally stored in browser
        getLocalSettings();

        // add event listeners
        document.getElementById(addParameterId).addEventListener("click", addParameter);

        // update columns will load all data
        updateColumns();
    }, false);

    function getLocalSettings() {
        const localSettings = JSON.parse(localStorage.getItem("columns"));
        columns = localSettings ? localSettings : ["compound", "name", "type", "cp"];
    }

    function updateColumns() {
        // fetch parameters from API, create columns and then call update data
        fetch(paramEndpoint).then(r => r.json()).then(d => {
            parameters = d;
            columns.forEach(c => document.getElementById(filtersId).appendChild(createColumn(c)));
            document.getElementById(filtersId).appendChild(createTableButtons());
            document.getElementById(settingsApplyId).addEventListener("click", applySettings);
            document.getElementById(settingsCancelId).addEventListener("click", cancelSettings);
        }).then(() => {
            updateSettings();
            updateData();
        });
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

    function updateData() {
        // fetch data from API, then call update page
        const query = Object.fromEntries(columns.map(c => [c, document.getElementById("block_" + c).value]));

        fetch(queryEndpoint, {
            method: "POST",
            cache: "no-cache",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(query)
        }).then(r => r.json()).then(d => {
            data = d;
            document.getElementById(pageNumberId).value = 1;
            updatePage();
            document.getElementById(spinnerId).style.display = "none";
        });
    }

    function updatePage() {
        const pageNumber = document.getElementById(pageNumberId).value * 1;
        const linesPerPage = document.getElementById(pageLinesId).value * 1;
        const pageStartIndex = (pageNumber - 1) * linesPerPage;
        const pageData = data.slice(pageStartIndex, pageStartIndex + linesPerPage + 1)
        const pages = Math.ceil(data.length / linesPerPage);

        // update results
        let resultsElement = document.getElementById(resultsId);
        resultsElement.innerHTML = "";

        pageData.forEach((result) => {
            resultsElement.appendChild(createResultRow(result, columns));
        });

        // update total
        let totalElement = document.getElementById(totalId);
        totalElement.textContent = data.length == 1 ? "1 result" : data.length.toLocaleString() + " results";

        // update pagination
        let paginationElement = document.getElementById(paginationId);
        paginationElement.innerHTML = "";

        // set indices; include first and last page, then current page +/- 2
        let paginationIndices = new Set([
            1, pageNumber, pages,
            pageNumber - 1, pageNumber + 1,
            pageNumber - 2, pageNumber + 2
        ]);

        // sort and filter indices
        paginationIndices = [...paginationIndices].filter((i) => {
            return i > 0 && i <= pages;
        }).sort((a, b) => {
            return (a * 1) > (b * 1) ? 1 : (a == b ? 0 : -1);
        });

        // add back button
        paginationElement.appendChild(createPaginationItem(pageNumber - 1, false, pageNumber == 1, "←"));

        for (let i = 0; i < paginationIndices.length; i++) {
            // add disabled ... button if there are gaps in page numbers
            if (paginationIndices[i] - paginationIndices[i - 1] > 1) {
                paginationElement.appendChild(createPaginationItem(0, false, true, "..."));
            }

            // add page number button
            paginationElement.appendChild(createPaginationItem(paginationIndices[i], pageNumber == paginationIndices[i], false));
        }

        // add forward button
        paginationElement.appendChild(createPaginationItem(pageNumber + 1, false, pageNumber >= pages, "→"));
    }

    function createColumn(c) {
        // create column header for given parameter and add event listener to update data
        // <td>
        //   <div class="form-floating">
        //     <input id="block_{parameter}" type="text" class="form-control" placeholder="">
        //     <label for="block_{parameter}">{title}</label>
        //   </div>
        // </td>

        let input = document.createElement("input");
        input.setAttribute("id", "block_" + c);
        input.setAttribute("type", "text");
        input.setAttribute("class", "form-control");
        input.setAttribute("placeholder", "");

        let label = document.createElement("label");
        label.setAttribute("for", "block_" + c);
        label.textContent = getParameterTitle(c);

        let div = document.createElement("div");
        div.setAttribute("class", "form-floating");
        div.appendChild(input);
        div.appendChild(label);

        let column = document.createElement("td");
        column.appendChild(div);
        column.addEventListener("keyup", () => {
            clearTimeout(typingTimer);
            typingTimer = setTimeout(updateData, typingTime);
        });

        return column;
    }

    function createResultRow(result) {
        // create row for given data point and add button links to diagram/detail
        // <tr>
        //   {for each data point}<td>{data}</td>{endfor}
        //   <td>
        //     <div class="btn-group btn-group-sm float-end" role="group" aria-label="Links">
        //       <a href="{diagram_url}" role="button" class="btn btn-outline-secondary btn-results">Diagram</a>
        //       <a href="{detail_url}" role="button" class="btn btn-outline-secondary btn-results">Detail</a>
        //     </div>
        //   </td>
        // </tr>

        let row = document.createElement("tr");

        columns.forEach((c) => {
            let column = document.createElement("td");
            column.textContent = result[c]
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
                updatePage();
            });
        }

        return item;
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
})()