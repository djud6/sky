import React, { useLayoutEffect } from "react";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";

am4core.useTheme(am4themes_animated);

const AccidentChart = ({ titleText, data, size}) => {
    useLayoutEffect(() => {
      var chart = am4core.create("chartdiv", am4charts.XYChart);
      chart.hiddenState.properties.opacity = 0; // this creates initial fade-in
  
      var title = chart.titles.create();
      if (titleText) {
        title.text = titleText;
        title.fontSize = 25;
        title.marginBottom = 30;
      }
  
      //chart.data = data;
  
      chart.data = [{
        "months": "Jan",
        "accidents": 501,
      }, {
        "months": "Feb",
        "accidents": 301,
      }, {
        "months": "Mar",
        "accidents": 201,
      }, {
        "months": "Apr",
        "accidents": 165,
      }, {
        "months": "May",
        "accidents": 139,
      }, {
        "months": "Jun",
        "accidents": 128,
      }];

      let categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
      categoryAxis.dataFields.category = "months";
      categoryAxis.title.text = "Months";
      
      let valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
      valueAxis.title.text = "Number of Accidents";

      let series = chart.series.push(new am4charts.ColumnSeries());
      series.dataFields.valueY = "accidents";
      series.dataFields.categoryX = "months";
      series.name = "Accidents for the month";
      series.columns.template.tooltipText = "Series: {name}\nMonth: {categoryX}\nAccident: {valueY}";
      series.columns.template.fill = am4core.color("#104547"); // fill
  
      return () => {
        chart.dispose();
      };
      //eslint-disable-next-line react-hooks/exhaustive-deps
    }, [JSON.stringify(data), titleText, size]);
  
    return <div id={JSON.stringify(data)} style={{ width: "100%", height: {size} }} />;
  };
  
  export default AccidentChart;
  
