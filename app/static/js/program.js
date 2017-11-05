$.getJSON("/program_summary_api", function(data) {
    var funding_chart = dc.barChart('#program_funding');

    var funding_data = data.data.funding_by_program,
        sndx1            = crossfilter(funding_data),
        programDimension = sndx1.dimension(function(d) {return d.program_funded;}),
        sumGroup         = programDimension.group().reduceSum(function(d) {return d.donations;});

    funding_chart
        .width(850)
        .height(330)
        .margins({top: 30, right: 50, bottom: 40, left: 60})
        .x(d3.scale.ordinal())
        .xUnits(dc.units.ordinal)
        .ordinalColors(['#595097'])
        .brushOn(false)
        .xAxisLabel('Program')
        .yAxisLabel('Funding \(\$K\)')
        .dimension(programDimension)
        .gap(10)
        .barPadding(0.5)
        .outerPadding(0.05)
        .group(sumGroup);

        funding_chart.render();
    
    var attendance_chart = dc.barChart('#program_attendance');

    var attendance_data   = data.data.attendance_by_program
            sndx2            = crossfilter(attendance_data),
            programDimension2 = sndx2.dimension(function(d) {return d.event_name;}),
            sumGroup2       = programDimension2.group().reduceSum(function(d) {return d.attendee_count;});

        attendance_chart
            .width(850)
            .height(330)
            .margins({top: 30, right: 50, bottom: 40, left: 60})
            .x(d3.scale.ordinal())
            .xUnits(dc.units.ordinal)
            .ordinalColors(['#61BCB2'])
            .brushOn(false)
            .xAxisLabel('Program')
            .yAxisLabel('Attendance')
            .dimension(programDimension2)
            .gap(10)
            .barPadding(0.5)
            .outerPadding(0.05)
            .group(sumGroup2);

        attendance_chart.render();
});

function refresh_charts(program_value) {
    $.getJSON("/program_api", {
        program: program_value
    }, function(data) {
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
        .width(1100)
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
        console.log(data.data)

        function numberWithCommas(x) {
            return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
          }
        
        $("#attendance")[0].innerHTML = "<i class='fa fa-users'></i> " + numberWithCommas(data.data.attendance_by_program[0].attendee_count)
        $("#funding")[0].innerText = "$ " + numberWithCommas(Math.round(data.data.funding_by_program[0].donations,3))
    
        chart.render();
    });
};

$('#program').change(function() {
    var program_value = $('#program')[0].value
    refresh_charts(program_value)
})

var program_value = $('#program')[0].value

refresh_charts(program_value)


