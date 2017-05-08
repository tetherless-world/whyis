
  var endpoint = "http://localhost:9999/bigdata/sparql";
  var query = "prefix dcterms: <http://purl.org/dc/terms/>\
  prefix dcat: <http://www.w3.org/ns/dcat#>\
  \
  select ?keyword ?year (count(?document) as ?count) where {\
    ?document dcat:keyword ?keyword; dcterms:created ?year.\
  } group by ?keyword ?year order by ?keyword ?year";

  function prepData(data) {
      var maps = {};
      var result = [];
      var years = d3.set();
      if(data != null){

      data.results.bindings.forEach(function(row) {
          if (!maps[row.keyword.value]) {
              var group = { key: row.keyword.value, entries: {}};
              maps[row.keyword.value] = group;
              result.push(group);
          }
          maps[row.keyword.value].entries[row.year.value] = parseInt(row.count.value);
          years.add(row.year.value)
      });
      years = years.values().sort();

      result.forEach(function(category) {
          category.values = years.map(function(year) {
              if (category.entries[year]) return [parseInt(year),category.entries[year]];
              else return [parseInt(year), 0];
          });
      });
      }
      return result;
  }

  d3.json(endpoint+"?format=json&query="+encodeURIComponent(query), function(data) {
      data = prepData(data);

  nv.addGraph(function() {
    var chart = nv.models.stackedAreaChart()
                  .x(function(d) { return d[0] })
                  .y(function(d) { return d[1] })
                  .clipEdge(true)
                  .useInteractiveGuideline(true)
                  ;

      chart.showLegend(false);
      chart.xAxis
        .showMaxMin(false);
      //.tickFormat(function(d) { return d });

      chart.interactiveLayer.tooltip.contentGenerator(function(d) {
          if (d === null) {
              return '';
          }

          var table = d3.select(document.createElement("table"));

          var tbodyEnter = table.selectAll("tbody")
              .data([d])
              .enter().append("tbody");

          var trowEnter = tbodyEnter.selectAll("tr")
                  .data(function(p) {
                      return p.series.filter(function(p) {
                         return p.value > 0;
                      });
                  })
                  .enter()
                  .append("tr")
                  .classed("highlight", function(p) { return p.highlight});

          trowEnter.append("td")
              .classed("legend-color-guide",true)
              .append("div")
              .style("background-color", function(p) { return p.color});

          trowEnter.append("td")
              .classed("key",true)
              .classed("total",function(p) { return !!p.total})
              .html(function(p, i) { return p.key});

          trowEnter.append("td")
              .classed("value",true)
              .html(function(p, i) { return chart.yAxis.tickFormat()(p.value) });

          trowEnter.selectAll("td").each(function(p) {
              if (p.highlight) {
                  var opacityScale = d3.scale.linear().domain([0,1]).range(["#fff",p.color]);
                  var opacity = 0.6;
                  d3.select(this)
                      .style("border-bottom-color", opacityScale(opacity))
                      .style("border-top-color", opacityScale(opacity))
                  ;
              }
          });

          var html = table.node().outerHTML;
          if (d.footer !== undefined)
              html += "<div class='footer'>" + d.footer + "</div>";
          return html;

      });

    chart.yAxis
        .tickFormat(d3.format('g'));

    d3.select('#chart svg')
      .datum(data)
        .transition().duration(500).call(chart);

    nv.utils.windowResize(chart.update);

    return chart;
  });
})
