(() => {
  "use strict";
  document.addEventListener("DOMContentLoaded", main, false);

  function main() {
    const startGrab = (_) => document.body.classList.add("grabbing");
    const endGrab = (_) => document.body.classList.remove("grabbing");
    const onMove = (event) => {
      if (event.related.classList.contains("pinned")) {
        return false;
      }
    };

    var sortable = new Sortable(document.getElementById("parameterList"), {
      handle: ".handle",
      filter: ".pinned",
      animation: 100,
      forceFallback: true,
      onChoose: startGrab,
      onStart: startGrab,
      onUnchoose: endGrab,
      onEnd: endGrab,
      onMove: onMove,
    });
  }
})();
