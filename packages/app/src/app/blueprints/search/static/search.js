(() => {
  "use strict";
  document.addEventListener("DOMContentLoaded", main, false);

  function main() {
    const tooltipTriggerList = document.querySelectorAll(
      '[data-bs-toggle="tooltip"]'
    );

    const tooltipList = [...tooltipTriggerList].map(
      (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
    );
  }
})();

function initSortable() {
  Sortable.create(document.getElementById("parameterList"), {
    handle: ".handle",
    draggable: ".draggable",
    filter: ".pinned",
    animation: 100,
    forceFallback: true,
    onChoose: (_) => document.body.classList.add("grabbing"),
    onUnchoose: (_) => document.body.classList.remove("grabbing"),
  });
}
