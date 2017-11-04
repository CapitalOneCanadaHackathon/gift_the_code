//define global variables

var left_offset=10, //50 //inherently sets the margin
    top_offset=50,
    width_margin=3*left_offset,
    margin=125,
    width = document.getElementById("canvas").offsetWidth,
    height = 500,
    prefix = prefixMatch(["webkit", "ms", "Moz", "O"]);

var default_year=2013;//start at 2010
// var to=[-79.38558, 43.7020];
var to=[-79.38433, 43.65488];

var num_format = d3.format("0,000");

var max_year;
var min_year;

var color_keys;

//circles sized by total revenue which varies year by year
var rscale; //scale for circle radius to keep max radius constant across each year

var color_scale = d3.scale.category10();

d3.json('static/data/map_data.json', function(data) {
  raw_data = data

  update(default_year);
  max_year = d3.max(raw_data, function(d) { return d.year; });
  min_year = d3.min(raw_data, function(d) { return d.year; });
  build_slider();
});


function build_slider() {
  slider_axis = d3.svg.axis().orient("bottom").tickFormat(d3.format("d")).ticks(max_year-min_year+1);

  slider = d3.slider().axis(slider_axis).min(min_year).max(max_year)
              .step(1).value(default_year)
              .on("slide", function(evt, year) {
              update(year);
              });

  d3.select('#slider').call(slider);

}

// Render the slider in the div
d3.select('#slider')
.style("width",width/3+"px")
.style("top",top_offset - 25 +"px")
.style("left",left_offset +5 + "px");


var tip = d3.tip()
  .attr('class', 'd3-tip')
  .offset([-10, 0])
  .html(function(d) {
    return "<span>" + d.postcode + "</span>" + "<br />" + "<span>" +
              "Type: " + d.stop_type + "</span>" + "<br />" + "<span>" +
              "Total Food: $" + num_format(d.total*2.5) + "</span>" + "<br />" + "<span>" +
              "Avg Nutrient Ratio: " + Math.round(d.nutrient_ratio*100)/100 + "</span>" + "<br />" + "<span>" +
              "Avg Non-Perishable Ratio: " + Math.round(d.perishable_ratio*100)/100 + "</span>";
    // return "<span style='color:black'>" + d.street_address + "</span>";
  });


var tile = d3.geo.tile()
.size([width, height]);

var zoom_level=0.5;

var projection = d3.geo.mercator()
    .scale((1 << 20) / zoom_level / Math.PI)
    .translate([-width / 2, -height / 2]);


//revised: zoom to toronto
var zoom = d3.behavior.zoom()
    .scale(projection.scale() * zoom_level * Math.PI)
    .scaleExtent([1 << 200, 1 << 25])
    .translate(projection(to).map(function (x) {
        return -x;
    }))
    .on("zoom", zoomed);

zoom.scale(projection.scale() * 2 * Math.PI)
  .translate(projection(to).map(function (x) {
      return -x;
}));

var container = d3.select("#canvas").append('div')
    .attr("id", "container")
    .style("width", width + "px")
    .style("height", height + "px")
    .style("top", top_offset + "px")
    .style("left", left_offset + "px")
    .call(zoom)
    .on("mousemove", mousemoved); //for coordinates shown on bottom left


var map = container.append("g")
    .attr("id", "map");

var points = container.append("svg")
    .attr("id", "points");

var layer = map.append("div")
    .attr("class", "layer");

var info = map.append("div")
    .attr("class", "info");
    
points.call(tip);
// zoomed();

function update(year) {
  data=raw_data.filter(function(d) {
          return d.year == year;});

  //get list of unique infraction_code's for given year
  color_keys=d3.map(data, function(d){return d.stop_type;}).keys();

  //map the new domain to the color scale
  color_scale=color_scale.domain(color_keys)

  max = d3.max(data, function(d) { return d.total; });
  min = d3.min(data, function(d) { return d.total; });

  //redefine scale based on new data
  rscale = d3.scale.linear()
  .domain([min,max])
  .range([0.0000005,0.00005]); //custom max/zoom.scale & min/zoom.scale values //[0.00000018,0.00000852]

  add_circles(data);
}

function add_circles(dataset) {
  d3.select("#points").selectAll("circle").data(dataset) //plotted 	locations on map
  .enter()
  .append("circle")
  .attr("class", "postcode")
  .attr("cx", function(d) {return projection([d.long,d.lat])[0]})
  .attr("cy", function(d) {return projection([d.long,d.lat])[1]})
  .attr("r",1)
	.style("fill", function(d) {return color_scale(d.stop_type)})
  .on('mouseover', tip.show)
  .on('mouseout', tip.hide);

  // d3.selectAll("circle")
  //     .transition().duration(2000)
  //     .attr("r", function(d) {return rscale(d.total)*zoom.scale()});

  zoomed();
}

function zoomed() {

  var tiles = tile
      .scale(zoom.scale())
      .translate(zoom.translate())
      ();

  projection
      .scale(zoom.scale() / 2 / Math.PI)
      .translate(zoom.translate());

  var circles = d3.selectAll("circle")
        .attr("cx", function(d) {return projection([d.long,d.lat])[0]})
				.attr("cy", function(d) {return projection([d.long,d.lat])[1]})
        // .transition().duration(2000)
        .attr("r", function(d) {return rscale(d.total)*zoom.scale()});

  var image = layer
      .style(prefix + "transform", matrix3d(tiles.scale, tiles.translate))
      .selectAll(".tile")
      .data(tiles, function(d) { return d; });

  image.exit()
      .remove();

//Ian: play with this to format what OSM gives you...
  image.enter().append("img")
      .attr("class", "tile")
      // .attr("src", function(d) { return "http://" + ["a", "b", "c"][Math.random() * 3 | 0] + ".tile.openstreetmap.org/" + d[2] + "/" + d[0] + "/" + d[1] + ".png"; })
      .attr("src", function(d) { return "http://" + ["a", "b", "c"][Math.random() * 3 | 0] + ".tile.openstreetmap.se/hydda/full/" + d[2] + "/" + d[0] + "/" + d[1] + ".png"; })
      .style("left", function(d) { return (d[0] << 8) + "px"; })
      .style("top", function(d) { return (d[1] << 8) + "px"; });
}

function mousemoved() {
  info.text(projection.invert(d3.mouse(this)));
  info.text(formatLocation(projection.invert(d3.mouse(this)), zoom.scale()));
}

function matrix3d(scale, translate) {
  var k = scale / 256, r = scale % 1 ? Number : Math.round;
  return "matrix3d(" + [k, 0, 0, 0, 0, k, 0, 0, 0, 0, k, 0, r(translate[0] * scale), r(translate[1] * scale), 0, 1 ] + ")";
}

function prefixMatch(p) {
  var i = -1, n = p.length, s = document.body.style;
  while (++i < n) if (p[i] + "Transform" in s) return "-" + p[i].toLowerCase() + "-";
  return "";
}

function formatLocation(p, k) {
  var format = d3.format("." + Math.floor(Math.log(k) / 2 - 2) + "f");
  return (p[1] < 0 ? format(-p[1]) + "°S" : format(p[1]) + "°N") + " "
       + (p[0] < 0 ? format(-p[0]) + "°W" : format(p[0]) + "°E");
}
