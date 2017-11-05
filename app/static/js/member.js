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
          .height(350)
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
        
          // Member Age Chart
        var chart2 = dc.rowChart("#member_age");

        var ct_data = data.data.age_of_members
        var ndx2 = crossfilter(ct_data);
      
        var ageDim = ndx2.dimension(function (d) {return d.age_range;});
        var member_sum_age = ageDim.group().reduceSum(function(d) {return d.count;});
      
        chart2
          .width(500)
          .height(338)
          .dimension(ageDim)
          .margins({top: 30, right: 50, bottom: 40, left: 10})
          .group(member_sum_age, "Number of members")
          .valueAccessor(function (d) {return d.value;})

          // Member Length Chart
        var chart3 = dc.rowChart("#member_length");

        var ct_data2 = data.data.membership_length
        console.log(ct_data2)
        var ndx3 = crossfilter(ct_data2);
      
        var lenDim = ndx3.dimension(function (d) {return d.membership_age_range;});
        var member_sum_len = lenDim.group().reduceSum(function(d) {return d.count;});
      
        chart3
          .width(500)
          .height(350)
          .dimension(lenDim)
          .margins({top: 30, right: 50, bottom: 40, left: 10})
          .group(member_sum_len, "Number of members")
          .valueAccessor(function (d) {return d.value;})

        dc.renderAll();

        // d3.select("#member_ts").attr("align","center");
      });
    };

refresh_charts()