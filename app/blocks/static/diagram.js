(() => {
    'use strict';

    const compound = document.getElementById("compound").value;
    const block = document.getElementById("block").value;
    const depth = document.getElementById("depth").value;
    const graph = d3.select("#graph");
    const width = graph.node().clientWidth;
    const height = graph.node().clientHeight;
    const scale = 0.95;
    const px2pt = 3 / 4;

    function calculateViewBox(viewBox) {
        const [vx, vy, vw, vh] = viewBox.split(' ').map(Number);
        const gw = vw / px2pt;
        const gh = vh / px2pt;
        const w = gw / scale;
        const h = gh / scale;
        const x = -(w - gw) / 2;
        const y = -(h - gh) / 2;
        return [x * px2pt, y * px2pt, w * px2pt, h * px2pt].join(' ');
    }

    function handleSvgAttributes(datum) {
        if (datum.tag === "svg") {
            const viewBox = calculateViewBox(datum.attributes.viewBox);
            graph.attr('viewBox', viewBox);
            datum.attributes.viewBox = viewBox;
            datum.attributes = {
                ...datum.attributes,
                width: width,
                height: height,
            };
        }
    }

    fetch("/api/dot/" + compound + "__" + block + "__depth-" + depth)
        .then((response) => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.text();
        })
        .then((dot) => {
            graph.graphviz()
                .tweenShapes(false)
                .tweenPaths(false)
                .zoomScaleExtent([0.1, 100])
                .attributer(handleSvgAttributes)
                .renderDot(dot);
        })
        .catch((error) => {
            console.error("Error fetching DOT data:", error);
        });
})();
