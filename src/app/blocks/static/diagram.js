(() => {
    'use strict';

    const compound = document.getElementById("compound").value;
    const block = document.getElementById("block").value;
    const depth = document.getElementById("depth").value;
    const navbarHeight = document.getElementById("navbar").clientHeight;
    const container = d3.select("#diagram-container");
    const scale = 0.95;
    const px2pt = 3 / 4;

    document.addEventListener("DOMContentLoaded", async () => {
        const endpoint = "/blocks/" + compound + "/" + block + "/dot?depth=" + depth;
        await fetch(endpoint).then(r => r.text()).then(dot => render(dot));
    }, false);

    window.addEventListener("resize", () => {
        const svg = document.getElementById("diagram-svg");
        svg.style.width = document.body.clientWidth;
        svg.style.height = document.body.clientHeight - navbarHeight;
    });

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

    async function render(dot) {
        container.graphviz()
            .tweenShapes(false)
            .tweenPaths(false)
            .zoomScaleExtent([0.1, 100])
            .attributer(datum => {
                if (datum.tag === "svg") {
                    datum.attributes = {
                        ...datum.attributes,
                        viewBox: calculateViewBox(datum.attributes.viewBox),
                        width: document.body.clientWidth,
                        height: document.body.clientHeight - navbarHeight,
                        id: "diagram-svg",
                    };
                }
            })
            .renderDot(dot);
    }
})();
