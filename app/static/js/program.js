function refresh_charts() {
    $.getJSON("/program_api", function(data) {
        var chart = dc.compositeChart("#program_ts");

        var data = data
        var dateFormat = d3.time.format("%Y-%m")
        var ts_data = data.data.time_series
        var ndx = crossfilter(ts_data);
    
        ts_data.forEach(function (e) {
            e.dd = dateFormat.parse(e.month);
            e.year = d3.time.year(e.dd);
            e.month = d3.time.month(e.dd); // pre-calculate month for better performance
        });
    
        var dateDim = ndx.dimension(function (d) {return d.dd;});
        var funding_sum = dateDim.group().reduceSum(function(d) {return d.donations;});
        var attendance_sum = dateDim.group().reduceSum(function(d) {return d.attendance;});
    
        var minDate = dateDim.bottom(1)[0].dd;
        var maxDate = dateDim.top(1)[0].dd;
    
        chart
        .width(615)
        .height(384)
        .dimension(dateDim)
        .x(d3.time.scale().domain([minDate,maxDate]))
        .brushOn(false)
        .elasticY(true)
        .renderHorizontalGridLines(true)
        .renderVerticalGridLines(true)
        .margins({top: 30, right: 50, bottom: 40, left: 60})
        .compose([
            dc.lineChart(chart)
                    .group(funding_sum, "Funding \(\$\)")
                    .valueAccessor(function (d) {
                        return d.value;
                    })
                    .interpolate('basis-open')
                    .ordinalColors(['#595097']),
            dc.lineChart(chart)
                    .group(attendance_sum, "Attendance")
                    .valueAccessor(function (d) {
                        return d.value;
                    })
                    .ordinalColors(["#61BCB2"])
                    .useRightYAxis(true)
                    .interpolate('basis-open')
                ])
        .rightYAxisLabel("Attendance")
        .yAxisLabel("Funding \(\$\)")
        .xAxisLabel("Date")
        .legend(dc.legend().x(90).y(30).itemHeight(13).gap(5))
    
        dc.renderAll();
    });
};

refresh_charts()