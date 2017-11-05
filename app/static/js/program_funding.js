var chart = dc.barChart('#program_funding');

d3.json('program_data.json', function(error, data) {
    if(error)
        throw new Error(error);
    var funding_data     = data.data.funding_by_program,
        ndx              = crossfilter(funding_data),
        programDimension = ndx.dimension(function(d) {return d.program_funded;}),
        sumGroup         = programDimension.group().reduceSum(function(d) {return d.donations;});

    chart
        .width(768)
        .height(380)
        .margins({top: 30, right: 50, bottom: 40, left: 60})
        .x(d3.scale.ordinal())
        .xUnits(dc.units.ordinal)
        .ordinalColors(['#595097'])
        .brushOn(false)
        .xAxisLabel('Program')
        .yAxisLabel('Funding \(\$\)')
        .dimension(programDimension)
        .gap(10)
        .barPadding(0.5)
        .outerPadding(0.05)
        .group(sumGroup);

    chart.render();
});
