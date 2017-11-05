var chart = dc.rowChart("#member_length");

d3.json("member_data.json", function(error, data) {
  var dateFormat = d3.time.format("%Y-%m")
  var ct_data = data.data.membership_length
  var ndx = crossfilter(ct_data);

  var lenDim = ndx.dimension(function (d) {return d.membership_age_range;});
  var member_sum = lenDim.group().reduceSum(function(d) {return d.count;});

  chart
    .width(768)
    .height(480)
    .dimension(lenDim)
    .margins({top: 30, right: 50, bottom: 40, left: 60})
    .group(member_sum, "Number of members")
    .valueAccessor(function (d) {return d.value;})
  dc.renderAll();
});
