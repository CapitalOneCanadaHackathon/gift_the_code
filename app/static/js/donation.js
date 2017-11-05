function refresh_charts() {
    $.getJSON("/donation_api", function(data) {
        var chart = dc.lineChart("#donation_ts");

        var data = data;
        var dateFormat = d3.time.format("%Y-%m");
        var ts_data = data.data.donations_over_time;
        var ndx = crossfilter(ts_data);

        ts_data.forEach(function (e) {
            e.dd = dateFormat.parse(e.month);
            e.year = d3.time.year(e.dd);
            e.month = d3.time.month(e.dd); // pre-calculate month for better performance
        });

        var dateDim = ndx.dimension(function (d) {return d.dd;});
        var donation_sum = dateDim.group().reduceSum(function(d) {return d.sum;});

        var minDate = dateDim.bottom(1)[0].dd;
        var maxDate = dateDim.top(1)[0].dd;

        chart
          .width(768)
          .height(330)
          .dimension(dateDim)
          .x(d3.time.scale().domain([minDate,maxDate]))
          .brushOn(false)
          .elasticY(true)
          //.renderHorizontalGridLines(true)
          .renderVerticalGridLines(true)
          .margins({top: 30, right: 50, bottom: 40, left: 60})
          .group(donation_sum, "Donations \(\$\)")
          .valueAccessor(function (d) {return d.value;})
          .interpolate('basis-open').ordinalColors(['#595097'])
          .yAxisLabel("Donations \(\$\)")
          .xAxisLabel("Date")
          .legend(dc.legend().x(90).y(30).itemHeight(13).gap(5))

        dc.renderAll();

        function numberWithCommas(x) {
            return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
          }
        
        var donors = [];
        donors.push("<div>");
        donor_data = data.data.top_donors
    
        $.each(donor_data, function(i) {
          d = donor_data[i]
          console.log(d)
      
          var num = '$ ' + numberWithCommas(Math.ceil(d.sum));
          
          var item = "<div class='col-sm-12 col-md-12'><div class='row'><div class='col-sm-4 col-md-4 value'>";
          item = item + num + "</div><div class='key col-sm-8 col-md-8 donor-name'>" + d.first_name + ' ' + d.last_name + "</div></div></div>";
          donors.push(item);
    
        });
        donors.push("</div>");
        $("#top_donors").append(donors);
        
        var funders = [];
        funders.push("<div>");
        funder_data = data.data.top_funders
    
        $.each(funder_data, function(i) {
          d = funder_data[i]
          console.log(d)
      
          var num = '$ ' + numberWithCommas(Math.ceil(d.sum));
          
          var item = "<div class='col-sm-12 col-md-12'><div class='row'><div class='col-sm-4 col-md-4 value'>";
          item = item + num + "</div><div class='key col-sm-8 col-md-8 donor-name'>" + d.company_name + "</div></div></div>";
          funders.push(item);
    
        });
        funders.push("</div>");
        $("#top_funders").append(funders);
      });
};

refresh_charts()