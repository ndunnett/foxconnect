;(() => {
  'use strict'
  document.addEventListener('DOMContentLoaded', main, false)

  // DOM identifiers
  const spinnerId = 'spinner'
  const totalId = 'result-total'
  const paginationId = 'pagination'
  const tableBodyId = 'table-body'
  const tableHeadId = 'table-head'
  const tableFilterInputsQuery = '#filter-row input.form-control'
  const settingsApplyId = 'settings-apply'
  const settingsCancelId = 'settings-cancel'
  const parameterListId = 'parameter-list'
  const parameterListItemQuery = '#parameter-list li.list-group-item'
  const parameterInputId = 'parameter-input'
  const parameterAddId = 'add-parameter'
  const settingsLinesId = 'settings-lines'

  // API endpoints
  const bodyEndpoint = '/search/table_body'
  const headEndpoint = '/search/table_head'
  const metaDataEndpoint = '/search/table_metadata'
  const parametersEndpoint = '/search/parameters'

  // behaviour constants
  const typingTime = 1000
  const localOnlyData = ['theme']

  // app state
  let typingTimer = {}
  let metadata = {}

  function main () {
    // load local storage, then update metadata, then update dynamic content
    loadLocalStorage()
    updateMetadata().then(() => {
      hookSettingsModalButtons()
      updateSettingsModal()
      updateTableHead()
      updateTableBody()
      updateTableFoot()
    })
  }

  function saveLocalStorage () {
    // save metadata to browser local storage
    for (const [key, value] of Object.entries(metadata)) {
      if (key == 'query') {
        localStorage.setItem(key, JSON.stringify(Object.entries(value)))
      } else {
        localStorage.setItem(key, JSON.stringify(value))
      }
    }
  }

  function loadLocalStorage () {
    // load metadata from browser local storage
    for (const [key, value] of Object.entries(localStorage)) {
      if (!localOnlyData.includes(key)) {
        if (key == 'query') {
          metadata[key] = Object.fromEntries(JSON.parse(value))
        } else {
          metadata[key] = JSON.parse(value)
        }
      }
    }
  }

  async function fetchWithMetadata (endpoint) {
    // send POST request to endpoint with metadata JSON as the body
    let body = {}

    for (const [key, value] of Object.entries(metadata)) {
      if (key == 'query') {
        body[key] = Object.entries(value)
      } else {
        body[key] = value
      }
    }

    return fetch(endpoint, {
      method: 'POST',
      cache: 'no-cache',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
  }

  async function updateMetadata () {
    // download metadata json from server and save to local storage
    return fetchWithMetadata(metaDataEndpoint).then(async response => {
      const data = await response.json()

      for (const [key, value] of Object.entries(data)) {
        if (key == 'query') {
          metadata[key] = Object.fromEntries(value)
        } else {
          metadata[key] = value
        }
      }

      saveLocalStorage()
    })
  }

  async function updateElement (endpoint, elementId) {
    // download html from endpoint and replace contents of given element
    return fetchWithMetadata(endpoint).then(async r => {
      if (r.status == 200) {
        document.getElementById(elementId).innerHTML = await r.text()
      } else {
        document.getElementById(elementId).innerHTML =
          '<p>Server error: failed to fetch dynamic data.</p>'
      }
    })
  }

  function keyupCallback (element) {
    // update table when input is changed
    return () => {
      clearTimeout(typingTimer)
      typingTimer = setTimeout(() => {
        setSpinner(true)
        document.getElementById(tableBodyId).innerHTML = ''
        metadata.query[element.id] = element.value
        metadata.page = 1
        saveLocalStorage()
        updateMetadata().then(() => {
          updateTableBody()
          updateTableFoot()
        })
      }, typingTime)
    }
  }

  async function updateTableHead () {
    // update contents of table head and add callbacks to inputs
    return updateElement(headEndpoint, tableHeadId).then(() => {
      document.querySelectorAll(tableFilterInputsQuery).forEach(element => {
        element.addEventListener('keyup', keyupCallback(element))
      })
    })
  }

  async function updateTableBody () {
    // update contents of table body with queried data
    return updateElement(bodyEndpoint, tableBodyId).then(() => {
      setSpinner(false)
    })
  }

  function setSpinner (state) {
    // set visibility of loading spinner
    const classList = document.getElementById(spinnerId).classList

    if (!state && !classList.contains('visually-hidden')) {
      classList.add('visually-hidden')
    } else if (state) {
      classList.remove('visually-hidden')
    }
  }

  async function updateTableFoot () {
    // update total count and pagination
    const totalElement = document.getElementById(totalId)
    totalElement.textContent =
      metadata.total == 1
        ? '1 result'
        : metadata.total.toLocaleString() + ' results'
    totalElement.classList.remove('visually-hidden')
    return updatePagination()
  }

  function updatePagination () {
    // update pagination list based on metadata
    const totalPages = Math.ceil(metadata.total / metadata.lines)
    const paginationList = createPaginationList(metadata.page, totalPages)
    document.getElementById(paginationId).replaceChildren(paginationList)
  }

  function createPaginationList (pageNumber, totalPages) {
    // create pagination list for given current page number and total number of pages
    // <ul class="pagination pagination-sm justify-content-center">
    //   {list items}
    // </ul>

    let list = document.createElement('ul')
    list.className = 'pagination pagination-sm justify-content-center'

    // set indices; include first and last page, then current page +/- 2
    let paginationIndices = new Set([
      1,
      pageNumber,
      totalPages,
      pageNumber - 1,
      pageNumber + 1,
      pageNumber - 2,
      pageNumber + 2
    ])

    // sort and filter indices
    paginationIndices = [...paginationIndices]
      .filter(i => {
        return i > 0 && i <= totalPages
      })
      .sort((a, b) => {
        return a * 1 > b * 1 ? 1 : a == b ? 0 : -1
      })

    // add back button
    list.appendChild(
      createPaginationItem(pageNumber - 1, false, pageNumber == 1, '←')
    )

    // add page number buttons
    for (let i = 0; i < paginationIndices.length; i++) {
      // add disabled ... button if there are gaps in page numbers
      if (paginationIndices[i] - paginationIndices[i - 1] > 1) {
        list.appendChild(createPaginationItem(0, false, true, '...'))
      }

      list.appendChild(
        createPaginationItem(
          paginationIndices[i],
          pageNumber == paginationIndices[i],
          false
        )
      )
    }

    // add forward button
    list.appendChild(
      createPaginationItem(pageNumber + 1, false, pageNumber >= totalPages, '→')
    )

    return list
  }

  function createPaginationItem (
    number,
    active = false,
    disabled = false,
    label = ''
  ) {
    // create pagination item for given page number (optional title) and add event listener to update table data
    // <li class="page-item {active/disabled}">
    //   <button class="page-link">{number/title}</button>
    // </li>

    let item = document.createElement('li')
    item.className = 'page-item'
    item.className += active ? ' active' : ''
    item.className += disabled ? ' disabled' : ''

    let button = document.createElement('button')
    button.className = 'page-link'
    button.textContent = label ? label : number

    item.appendChild(button)

    if (!disabled && !active) {
      item.addEventListener('click', () => {
        metadata.page = number
        saveLocalStorage()
        updateTableBody()
        updatePagination()
      })
    }

    return item
  }

  async function hookSettingsModalButtons () {
    document
      .getElementById(settingsApplyId)
      .addEventListener('click', applySettings)
    document
      .getElementById(settingsCancelId)
      .addEventListener('click', updateSettingsModal)
    document.getElementById(parameterAddId).addEventListener('click', () => {
      document
        .getElementById(parameterListId)
        .firstChild.appendChild(
          createParameterListItem(
            document.getElementById(parameterInputId).value
          )
        )
    })
  }

  async function updateSettingsModal () {
    document
      .getElementById(parameterListId)
      .replaceChildren(createParameterList())
    document.getElementById(parameterInputId).value = ''
    document.getElementById(settingsLinesId).value = metadata.lines
  }

  function applySettings () {
    const lines = Number(document.getElementById(settingsLinesId).value)
    let parameters = []

    document.querySelectorAll(parameterListItemQuery).forEach(element => {
      parameters.push(element.getAttribute('value'))
    })

    let reloadHead = false
    let reloadBody = false
    let save = false

    if (lines != metadata.lines) {
      metadata.lines = Number(document.getElementById(settingsLinesId).value)
      metadata.page = 1
      reloadBody = true
      save = true
    }

    if (parameters != Object.keys(metadata.query)) {
      let new_query = {
        compound: metadata.query.compound,
        name: metadata.query.name
      }

      parameters.forEach(p => {
        if (Object.keys(metadata.query).includes(p)) {
          new_query[p] = metadata.query[p]
        } else {
          new_query[p] = ''
        }
      })

      metadata.query = new_query
      metadata.page = 1
      reloadHead = true
      reloadBody = true
      save = true
    }

    if (save) {
      saveLocalStorage()
      updateSettingsModal()
    }

    if (reloadHead) {
      updateTableHead()
    }

    if (reloadBody) {
      updateTableBody()
      updateTableFoot()
    }
  }

  function createParameterList () {
    let list = document.createElement('ul')
    list.className = 'list-group list-group-numbered'

    Object.keys(metadata.query).forEach(c => {
      if (c != 'compound' && c != 'name') {
        list.appendChild(createParameterListItem(c))
      }
    })

    Sortable.create(list, {})
    return list
  }

  function getParameterTitle (p) {
    return p.charAt(0).toUpperCase() + p.slice(1)
  }

  function createParameterListItem (c) {
    let item = document.createElement('li')
    item.setAttribute('class', 'list-group-item d-flex')
    item.setAttribute('value', c)

    let title = document.createElement('div')
    title.setAttribute('class', 'ms-2 me-auto')
    title.textContent = getParameterTitle(c)

    let button = document.createElement('button')
    button.setAttribute('class', 'btn-close')
    button.setAttribute('type', 'button')
    button.setAttribute('aria-label', 'Remove')
    button.addEventListener('click', () => {
      item.parentElement.removeChild(item)
    })

    item.appendChild(title)
    item.appendChild(button)
    return item
  }
})()
