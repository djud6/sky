import React, { useEffect, useRef } from "react";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import am4themes_dark from "@amcharts/amcharts4/themes/dark";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";
import { isMobileDevice } from "../../../helpers/helperFunctions";

am4core.useTheme(am4themes_dark);
am4core.useTheme(am4themes_animated);

const MultipleValueAxesCard = ({ chartParams, height }) => {
  const chartRef = useRef();
  const isMobile = isMobileDevice();

  useEffect(() => {
    if (!chartRef.current) {
      return;
    }

    // Create chart instance
    let chart = am4core.create(chartRef.current, am4charts.XYChart);

    // Increase contrast by taking evey second color
    chart.colors.step = 2;

    // Add data
    chart.data = chartParams;

    // Create axes
    let dateAxis = chart.xAxes.push(new am4charts.DateAxis());
    dateAxis.renderer.minGridDistance = 50;

    // Create series
    function createAxisAndSeries(cost, name, opposite, bullet) {
      let valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
      if (chart.yAxes.indexOf(valueAxis) !== 0) {
        valueAxis.syncWithAxis = chart.yAxes.getIndex(0);
      }

      let series = chart.series.push(new am4charts.LineSeries());
      series.dataFields.valueY = cost;
      series.dataFields.dateX = "date";
      series.strokeWidth = 2;
      series.yAxis = valueAxis;
      series.name = name;
      series.tensionX = 0.93;
      series.showOnInit = true;
      if (name === "Cost") {
        series.tooltipText = "{name}: [bold]{valueY}[/] \n {label}";
      } else {
        series.tooltipText = "{name}: [bold]{valueY}[/]";
      }

      let interfaceColors = new am4core.InterfaceColorSet();

      switch (bullet) {
        case "triangle":
          let bullet = series.bullets.push(new am4charts.Bullet());
          bullet.width = 12;
          bullet.height = 12;
          bullet.horizontalCenter = "middle";
          bullet.verticalCenter = "middle";

          let triangle = bullet.createChild(am4core.Triangle);
          triangle.stroke = interfaceColors.getFor("background");
          triangle.strokeWidth = 2;
          triangle.direction = "top";
          triangle.width = 12;
          triangle.height = 12;
          break;

        default:
          let circlebullet = series.bullets.push(new am4charts.CircleBullet());
          circlebullet.circle.stroke = interfaceColors.getFor("background");
          circlebullet.circle.strokeWidth = 2;
          break;
      }

      valueAxis.renderer.line.strokeOpacity = 1;
      valueAxis.renderer.line.strokeWidth = 2;
      valueAxis.renderer.line.stroke = series.stroke;
      valueAxis.renderer.labels.template.fill = series.stroke;
      valueAxis.renderer.opposite = opposite;
    }

    createAxisAndSeries("fuel_cost", "Cost", false, "circle");
    createAxisAndSeries("projected_cost", "Budget", true, "triangle");

    // Add legend
    // chart.legend = new am4charts.Legend();
    // Add cursor
    chart.cursor = new am4charts.XYCursor();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chartParams]);

  if (isMobile) {
    return (
      <div style={{ width: "100%", overflow: "auto" }}>
        <div ref={chartRef} style={{ width: "550px", height: height }} />
      </div>
    );
  } else {
    return <div ref={chartRef} style={{ width: "100%", height: height }} />;
  }
};

export default MultipleValueAxesCard;
