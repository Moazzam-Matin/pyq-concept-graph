const width = window.innerWidth - 220;
const height = window.innerHeight - 90;

const svg = d3.select("#graph")
  .attr("viewBox", [0, 0, width, height]);

const container = svg.append("g");

// We declare "label" here, outside the fetch, using `let` (not `const`),
// specifically so our zoom handler below can reference it even though
// it won't actually be created until the data finishes loading further down
let label;

const zoomBehavior = d3.zoom()
  .scaleExtent([0.2, 8])
  .on("zoom", (event) => {
    container.attr("transform", event.transform);

    // Only try to update labels if they've actually been created yet
    // (guards against this running before our fetch() below finishes)
    if (label) {
      const k = event.transform.k;
      const visibilityThreshold = 14 / k; // shrinks as you zoom in
      label.style("display", d => (d._radius >= visibilityThreshold ? "block" : "none"));
    }
  });

svg.call(zoomBehavior);

fetch("../output/graph_colored.json")
  .then(response => response.json())
  .then(data => {
    console.log("Loaded:", data.nodes.length, "nodes,", data.edges.length, "edges");

    const radiusScale = d3.scaleSqrt()
      .domain([1, d3.max(data.nodes, d => d.freq)])
      .range([3, 26]);

    // We store each node's computed radius directly on the node object itself,
    // under a new key "_radius" -- this saves us recalculating radiusScale(d.freq)
    // repeatedly later (in the zoom handler, on every single scroll event)
    data.nodes.forEach(d => { d._radius = radiusScale(d.freq); });

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.edges)
        .id(d => d.id)
        .distance(d => 100 - Math.min(d.weight * 3, 80))
        .strength(d => Math.min(d.weight / 20, 1)))
      .force("charge", d3.forceManyBody().strength(-60))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide(d => d._radius + 2));

    const link = container.append("g")
    .selectAll("path")
    .data(data.edges)
    .join("path")
    .attr("fill", "none")
    .attr("stroke", d => d.source.color || "#555")
    .attr("stroke-opacity", 0.25)
    .attr("stroke-width", d => Math.min(Math.sqrt(d.weight) * 0.5, 3));

    const node = container.append("g")
      .selectAll("circle")
      .data(data.nodes)
      .join("circle")
      .attr("r", d => d._radius)
      .attr("fill", "none")
      .attr("stroke", d => d.color)
      .attr("stroke-width", 1);

    label = container.append("g")
      .selectAll("text")
      .data(data.nodes)
      .join("text")
      .text(d => d.id)
      .attr("text-anchor", "middle")
      .attr("dy", d => d._radius + 10)
      .attr("font-size", 10)
      .attr("fill", "#ccc")
      .style("display", d => (d._radius >= 14 ? "block" : "none")); // initial state, before any zooming

    simulation.on("tick", () => {
    link.attr("d", d => {
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        const dr = Math.sqrt(dx * dx + dy * dy) * 1.3; // bigger dr = flatter curve
        return `M${d.source.x},${d.source.y} A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
    });

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

    label
        .attr("x", d => d.x)
        .attr("y", d => d.y);
    });
  });