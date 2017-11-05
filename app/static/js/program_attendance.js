var attendance_chart = dc.barChart('#program_attendance');

d3.json('program_data.json', function(error, data) {
    if(error)
        throw new Error(error);
    var attendance_data   = data.data.attendance_by_program
        ndx            = crossfilter(attendance_data),
        programDimension = ndx.dimension(function(d) {return d.event_name;}),
        sumGroup       = programDimension.group().reduceSum(function(d) {return d.attendee_count;});

    attendance_chart
        .width(768)
        .height(380)
        .margins({top: 30, right: 50, bottom: 40, left: 60})
        .x(d3.scale.ordinal())
        .xUnits(dc.units.ordinal)
        .ordinalColors(['#595097'])
        .brushOn(false)
        .xAxisLabel('Program')
        .yAxisLabel('Attendance')
        .dimension(programDimension)
        .gap(10)
        .barPadding(0.5)
        .outerPadding(0.05)
        .group(sumGroup);

    attendance_chart.render();
});
