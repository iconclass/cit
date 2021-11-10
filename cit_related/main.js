function bilink(root) {
  const map = new Map(root.descendants().map(d => [id(d), d]));
  for (const d of root.descendants()) {
    if (d.data.imports) {
      d.incoming = [], d.outgoing = d.data.imports.map(i => [d, map.get(i)]);
    } else {
      d.incoming = [], d.outgoing = [];
    }
  }
  // Links are drawn by "outgoing" connections, so "incoming" is unnecessary.
  // for (const d of root.leaves()) for (const o of d.outgoing) if (o) {o[1].incoming.push(o)};
  return root;
}

function id(node) {
  return `${node.parent ? id(node.parent) + "." : ""}${node.data.name}`;
}

const colorin = "#00f"
const colorout = "#f00"
const colornone = "#ccc"
const width=8000
const radius=2000
let radioButtons = document.querySelector('input[name="radioButtons"]:checked').value;

const textColor = d3.scaleOrdinal(d3.schemeCategory10);
const zoom = container => {
  // Zooming function translates the size of the svg container.
  function zoomed({transform}) {
      container.attr("transform", "translate(" + transform.x + ", " + transform.y + ") scale(" + transform.k + ")");
  }
  
  return d3.zoom().scaleExtent([0.5,3]).on('zoom', zoomed)
}

const line = d3.lineRadial()
    .curve(d3.curveBundle.beta(0.85))
    .radius(d => d.y)
    .angle(d => d.x)

const tree = d3.cluster()
    .size([2 * Math.PI, radius - 100])

d3.json("all_hierarchy_orig.json").then( data => {
  const root = tree(bilink(d3.hierarchy(data)
      .sort((a, b) => d3.ascending(a.height, b.height) /*|| d3.ascending(a.data.name, b.data.name)*/)));

  const svg = d3.select("#viz") .append("svg")
	.attr("preserveAspectRatio", "xMaxYMax meet")
        .attr("viewBox", [-width / 2, -width / 4, width, width/2])
	//.attr("viewBox", [0, 0, 8000, 8000])
	.classed("svg-content-responsive", true);

  var container = svg.append('g');
  // Call zoom for svg container.
  svg.call(zoom(container));

  const node = container.append("g")
      .attr("font-family", "sans-serif")
      .attr("font-size", 10)
    .selectAll("g")
    .data(root.descendants().filter(d => d.data.color !== undefined))
    .join("g")
      .attr("transform", d => `rotate(${d.x * 180 / Math.PI - 90}) translate(${d.y},0)`)
    .append("text")
      .attr("class", "node")
      .attr("dy", "0.31em")
      .attr("x", d => d.x < Math.PI ? 6 : -6)
      .attr("text-anchor", d => d.x < Math.PI ? "start" : "end")
      .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
      .attr('fill', d => textColor(d.data.color+1))
      .text(d => {if (radioButtons === "Chinese") {return d.data.name} else {return d.data.english_translation}})
      .each(function(d) { d.text = this; })
      .on("mouseover", overed)
      .on("mouseout", outed)
      .call(text => text.append("title").text(d => {
        if (d.data.imports) {
          return `This term: ${id(d)} (${d.data.english_translation})

Related terms: ${d.data.imports.map(i => `\n${i}`)}`
        } else {return `This term: ${id(d)} (${d.data.english_translation})`}
      }));

  const link = container.append("g")
      .attr("stroke", colornone)
      .attr("fill", "none")
    .selectAll("path")
    .data(root.descendants().flatMap(leaf => leaf.outgoing))
    .join("path")
      .style("mix-blend-mode", "multiply")
      .attr("class", "link")
      .attr("d", ([i, o]) => {if (o) { return line(i.path(o))}})
      .each(function(d) { d.path = this; });

  function overed(event, d) {
    link.style("mix-blend-mode", null);
    d3.select(this).attr("font-weight", "bold").attr("font-size", 30);
    d3.selectAll(d.outgoing.map(d => d.path)).attr("stroke", colorin).attr("stroke-width", 5).raise();
    d3.selectAll(d.outgoing.map(([, d]) => d.text)).attr("font-weight", "bold").attr("font-size", 30).attr("fill", "#00f");
  }

  function outed(event, d) {
    link.style("mix-blend-mode", "multiply");
    d3.select(this).attr("font-weight", null).attr("font-size", null);
    d3.selectAll(d.outgoing.map(d => d.path)).attr("stroke", null).attr("stroke-width", null);
    d3.selectAll(d.outgoing.map(([, d]) => d.text)).attr("fill", l => textColor(l.data.color+1)).attr("font-weight", null).attr("font-size", null);
  }
svg.append("g")
  .attr("class", "legendOrdinal")
  .attr("transform", "translate(3000,-1500)");

var legendOrdinal = d3.legendColor()
  .shapePadding(20)
  .labels(["Nature", "Myths and Legends", "Literary Works", "Human Being", "Society and Culture", "Religion", "History and Geography"])
  .labelOffset(20)
  .shapeHeight(80)
  .shapeWidth(80)
  .scale(textColor);

svg.select(".legendOrdinal")
  .call(legendOrdinal);
})

let label = document.querySelector('label.searchBox');
let input = document.querySelector('input.searchBox');
input.onkeyup = () => {
  var term = input.value;
  if (term !== "") {
    console.log(term);
    var selected = d3.selectAll('.node').filter(function (d, i) {
      return d.data.english_translation.toLowerCase().search(term.toLowerCase()) != -1 || d.data.name.toLowerCase().search(term.toLowerCase()) != -1;
    });
    d3.selectAll('.node').style('display', 'none').attr("fill", l => textColor(l.data.color+1)).attr("font-weight", null).attr("font-size", 10);
    selected.style('display', 'block').attr("font-weight", "bold").attr("font-size", 30);
    d3.selectAll('.link').attr('stroke-opacity', '0');
    selected.each(d => {
      d3.selectAll(d.outgoing.map(d => d.path)).attr("stroke-opacity", 1).raise();
      d3.selectAll(d.outgoing.map(([, d]) => d.text)).style('display', 'block');
    });
  } else {
    d3.selectAll('.node').style('display', 'block').attr("fill", l => textColor(l.data.color+1)).attr("font-weight", null).attr("font-size", 10);
    d3.selectAll('.link').attr('stroke-opacity', '1');
  }
}

let buttonsForm = document.querySelector("#radioButtons");

buttonsForm.onchange = () => {
	radioButtons = document.querySelector('input[name="radioButtons"]:checked').value;
	d3.selectAll(".node")
		.text(d => {if (radioButtons === "Chinese") {return d.data.name} else {return d.data.english_translation}})
	        .each(function(d) { d.text = this; })
	        .call(text => text.append("title").text(d => {
	          if (d.data.imports) {
	            return `This term: ${id(d)} (${d.data.english_translation})
	  
	  Related terms: ${d.data.imports.map(i => `\n${i}`)}`
	          } else {return `This term: ${id(d)} (${d.data.english_translation})`}
	        }));
}

