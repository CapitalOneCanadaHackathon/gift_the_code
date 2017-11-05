function refresh_charts() {
    $.getJSON("/member_api", function(data) {
        var chart = dc.lineChart("#member_ts");

        var data = data;
        var dateFormat = d3.time.format("%Y-%m");
        var ts_data = data.data.membership_over_time;
        var ndx = crossfilter(ts_data);

        ts_data.forEach(function (e) {
            e.dd = dateFormat.parse(e.month);
            e.year = d3.time.year(e.dd);
            e.month = d3.time.month(e.dd); // pre-calculate month for better performance
        });

        var dateDim = ndx.dimension(function (d) {return d.dd;});
        var member_sum = dateDim.group().reduceSum(function(d) {return d.count;});

        var minDate = dateDim.bottom(1)[0].dd;
        var maxDate = dateDim.top(1)[0].dd;

        chart
          .width(1200)
          .height(480)
          .dimension(dateDim)
          .x(d3.time.scale().domain([minDate,maxDate]))
          .brushOn(false)
          .elasticY(true)
          //.renderHorizontalGridLines(true)
          .renderVerticalGridLines(true)
          .margins({top: 30, right: 50, bottom: 40, left: 60})
          .group(member_sum, "Total number of registered members")
          .valueAccessor(function (d) {return d.value;}).interpolate('basis-open')
          .ordinalColors(['#595097'])
          .yAxisLabel("Total number of registered members")
          .xAxisLabel("Date")

        dc.renderAll();

        // d3.select("#member_ts").attr("align","center");
      });
    };

refresh_charts()