import React, { useLayoutEffect } from "react";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";

am4core.useTheme(am4themes_animated);

const MaintenceCostChart = ({ titleText, data, size}) => {
    useLayoutEffect(() => {
      var chart = am4core.create("maintenchartdiv", am4charts.XYChart);
      chart.hiddenState.properties.opacity = 0; // this creates initial fade-in
  
      var title = chart.titles.create();
      if (titleText) {
        title.text = titleText;
        title.fontSize = 25;
        title.marginBottom = 30;
      }
  
      chart.data = data;
  /*
      chart.data = [{
        "month": "1",
        "maintenance_cost": 1.65,
      }, {
        "month": "2",
        "maintenance_cost": 2.23,
      }, {
        "month": "3",
        "maintenance_cost": 2.24,
      }, {
        "month": "4",
        "maintenance_cost": 1.90,
      }, {
        "month": "5",
        "maintenance_cost": 1.00,
      }, {
        "month": "6",
        "maintenance_cost": 1.41,
      }];
*/
      let categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
      categoryAxis.dataFields.category = "month";
      categoryAxis.title.text = "Vehicle ID";
      categoryAxis.renderer.labels.template.fill = am4core.color("#FFFFFF");
      categoryAxis.title.fill = am4core.color("#FFFFFF");
      
      let valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
      valueAxis.title.text = "Maintenance Cost($) Per Km for Jaunary";
      valueAxis.renderer.labels.template.fill = am4core.color("#FFFFFF");
      valueAxis.title.fill = am4core.color("#FFFFFF");

      let series = chart.series.push(new am4charts.ColumnSeries());
      series.dataFields.valueY = "maintenance_cost";
      series.dataFields.categoryX = "month";
      series.name = "Maintenance Cost($)";
      series.columns.template.tooltipText = "Series: {name}\nMonth: {categoryX}\nCost: {valueY}";
      series.columns.template.fill = am4core.color("#104547"); // fill
  
      return () => {
        chart.dispose();
      };
      //eslint-disable-next-line react-hooks/exhaustive-deps
    }, [JSON.stringify(data), titleText, size]);
  
    return <div id={JSON.stringify(data)} style={{ width: "100%", height: {size} }} />;
  };
  
  export default MaintenceCostChart;
  
