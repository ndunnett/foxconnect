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
