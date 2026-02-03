import React, { useEffect, useRef } from "react";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";
import { isMobileDevice } from "../../../helpers/helperFunctions";

am4core.useTheme(am4themes_animated);

const MultipleAxesCard = ({ chartParams, height, chartName, processName, timeUnit = null}) => {

  const chartRef = useRef();
  const isMobile = isMobileDevice();

  chartParams.sort(function (a, b) {
    return new Date(b.date) - new Date(a.date);
  });

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
    var dateAxis = chart.xAxes.push(new am4charts.DateAxis());
    dateAxis.renderer.minGridDistance = 50;

    if (!timeUnit) {
      dateAxis.baseInterval= {
        timeUnit: timeUnit,
        count: 1
      };
    }

    let valueAxis = null;

    // Create series
    function createAxisAndSeries(
      field,
      name,
      opposite,
      bullet,
      makeAxis = true,
      seriesData = null
    ) {
      if (makeAxis || !valueAxis) {
        valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
      }
      if (chart.yAxes.indexOf(valueAxis) !== 0) {
        valueAxis.syncWithAxis = chart.yAxes.getIndex(0);
      }

      var series = chart.series.push(new am4charts.LineSeries());
      if (seriesData) {
        seriesData.sort(function (a, b) {
          return new Date(b.date) - new Date(a.date);
        });
        series.data = seriesData;
      }
      series.dataFields.valueY = field;
      series.dataFields.dateX = "date";
      series.strokeWidth = 2;
      series.yAxis = valueAxis;
      series.name = name;
      series.tensionX = 1;
      series.showOnInit = true;
      if (name === "Mileage") {
        series.tooltipText = "{name}: [bold]{valueY}[/] \n {average_mileage_label}";
      } else if (name === "Hours") {
        series.tooltipText = "{name}: [bold]{valueY}[/] \n {average_hours_label}";
      }

      if (chartName === "cost-per-process") {
        series.tooltipText = "{name}: [bold] $ {valueY}";
      } else if (chartName === "vehicle-util") {
        if (name === "Mileage") {
          series.tooltipText = "{name}: [bold]{valueY}[/] \n Yearly Average: {average_mileage_label}";
        } else if (name === "Hours") {
          series.tooltipText = "{name}: [bold]{valueY}[/] \n Yearly Average: {average_hours_label}";
        }
      }else if (chartName === "vehicle-cost") {
        series.tooltipText = "{name}: [bold]{valueY}[/]";
        // series.tooltipText = "{name}: [bold]{valueY}[/] \n Average Cost per Vehicle: {average}";
      }

      var interfaceColors = new am4core.InterfaceColorSet();

      switch (bullet) {
        case "triangle":
          var bullet = series.bullets.push(new am4charts.Bullet()); // eslint-disable-line
          bullet.width = 12;
          bullet.height = 12;
          bullet.horizontalCenter = "middle";
          bullet.verticalCenter = "middle";

          var triangle = bullet.createChild(am4core.Triangle);
          triangle.stroke = interfaceColors.getFor("background");
          triangle.strokeWidth = 2;
          triangle.direction = "top";
          triangle.width = 12;
          triangle.height = 12;
          break;
        case "rectangle":
          var bullet = series.bullets.push(new am4charts.Bullet()); // eslint-disable-line
          bullet.width = 10;
          bullet.height = 10;
          bullet.horizontalCenter = "middle";
          bullet.verticalCenter = "middle";

          var rectangle = bullet.createChild(am4core.Rectangle);
          rectangle.stroke = interfaceColors.getFor("background");
          rectangle.strokeWidth = 2;
          rectangle.width = 10;
          rectangle.height = 10;
          break;
        default:
          var bullet = series.bullets.push(new am4charts.CircleBullet()); // eslint-disable-line
          bullet.circle.stroke = interfaceColors.getFor("background");
          bullet.circle.strokeWidth = 2;
          break;
      }
      valueAxis.renderer.line.strokeOpacity = 1;
      valueAxis.renderer.line.strokeWidth = 2;
      valueAxis.renderer.line.stroke = series.stroke;
      valueAxis.renderer.labels.template.fill = series.stroke;
      valueAxis.renderer.opposite = opposite;
    }
    if (chartName === "avg-daily-usage") {
      createAxisAndSeries("mileage", "Mileage", false, "triangle");
      createAxisAndSeries("hours", "Hours", true, "rectangle");
    } else if (chartName === "cost-per-process") {
      chartParams.forEach((val) => {
        createAxisAndSeries(
          processName,
          Object.keys(val)[0],
          false,
          "circle",
          false,
          val[Object.keys(val)[0]]
        );
      });
    } else if (chartName === "vehicle-util") {
      if (timeUnit === 'day') {
        createAxisAndSeries(`daily_average_per_asset_mileage`, "Mileage", false, "triangle");
        createAxisAndSeries(`daily_average_per_asset_hour`, "Hours", true, "rectangle");
      } else {
        createAxisAndSeries(`${timeUnit}ly_average_per_asset_mileage`, "Mileage", false, "triangle");
        createAxisAndSeries(`${timeUnit}ly_average_per_asset_hour`, "Hours", true, "rectangle");
      }
    } else if (chartName === "vehicle-cost") {
      createAxisAndSeries(`cost`, "Vehicle Cost", false, "triangle");
      // createAxisAndSeries(`daily_average_per_asset_hour`, "Hours", true, "rectangle");
    }

    // Add legend
    chart.legend = new am4charts.Legend();

    // Add cursor
    chart.cursor = new am4charts.XYCursor();
    chart.cursor.behavior = 'selectX';

    return () => chart.dispose();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chartRef.current, chartParams]);

  if (isMobile) {
    return (
      <div style={{ width: "100%", overflow: "auto" }}>
        <div ref={chartRef} style={{ width: "500px", height: height }} />
      </div>
    );
  } else {
    return <div ref={chartRef} style={{ width: "100%", height: height }} />;
  }
};

export default MultipleAxesCard;
