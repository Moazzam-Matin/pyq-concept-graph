const width = window.innerWidth - 220;
const height = window.innerHeight - 90;

const svg = d3.select("#graph")
  .attr("viewBox", [0, 0, width, height]);

const container = svg.append("g");

// We declare "label" here, outside the fetch, using `let` (not `const`),
// specifically so our zoom handler below can reference it even though
// it won't actually be created until the data finishes loading further down
let node, link, label;

// Shared state used by both the zoom handler and the search highlight logic,
// so the two don't fight over whether a label should be visible.
let currentZoomK = 1;
let activeMatches = null;

function updateLabelVisibility() {
  const visibilityThreshold = 14 / currentZoomK; // shrinks as you zoom in
  label.style("display", d => {
    if (activeMatches && activeMatches.has(d.id)) return "block"; // matched labels always show
    return d._radius >= visibilityThreshold ? "block" : "none";
  });
}

function renderResultsPanel(results) {
  const panel = document.getElementById("results-panel");
  panel.innerHTML = ""; // clear any previous results

  if (!results || results.length === 0) return;

  results.forEach(r => {
    const chip = document.createElement("div");
    chip.className = "result-chip";
    chip.innerHTML = `
      <span class="term-name">${r.term}</span>
      <span class="term-stat">${r.recurrence_pct}% of years (${r.years_count}/19) · last ${r.last_year}</span>
    `;
    panel.appendChild(chip);
  });
}

function applyHighlight(matchedTerms) {
  activeMatches = matchedTerms === null ? null : new Set(matchedTerms);
  const hasSearch = activeMatches !== null;

  node
    .attr("opacity", d => (!hasSearch || activeMatches.has(d.id)) ? 1 : 0.15)
    .attr("stroke-width", d => (hasSearch && activeMatches.has(d.id)) ? 3 : 1);

  link.attr("stroke-opacity", d =>
    (!hasSearch || (activeMatches.has(d.source.id) && activeMatches.has(d.target.id))) ? 0.25 : 0.03
  );

  label.attr("fill", d => (hasSearch && activeMatches.has(d.id)) ? "#ffffff" : "#666");

  updateLabelVisibility();
}

async function runSearch(query) {
  if (!query.trim()) {
    applyHighlight(null);
    renderResultsPanel(null);
    return;
  }

  const response = await fetch("https://pyq-concept-graph.onrender.com/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: query }),
  });

  const data = await response.json();
  applyHighlight(data.terms);
  renderResultsPanel(data.results);
}

const zoomBehavior = d3.zoom()
  .scaleExtent([0.2, 8])
  .on("zoom", (event) => {
    container.attr("transform", event.transform);
    currentZoomK = event.transform.k;

    // Only try to update labels if they've actually been created yet
    // (guards against this running before our fetch() below finishes)
    if (label) {
      updateLabelVisibility();
    }
  });

svg.call(zoomBehavior);

fetch("graph_colored.json")
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

    link = container.append("g")
    .selectAll("path")
    .data(data.edges)
    .join("path")
    .attr("fill", "none")
    .attr("stroke", d => d.source.color || "#555")
    .attr("stroke-opacity", 0.25)
    .attr("stroke-width", d => Math.min(Math.sqrt(d.weight) * 0.5, 3));

    node = container.append("g")
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

document.getElementById("search-btn").addEventListener("click", () => {
  const query = document.getElementById("search-input").value;
  runSearch(query);
});

document.getElementById("search-input").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    const query = event.target.value;
    runSearch(query);
  }
});