import React, { useEffect, useRef } from "react";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import am4themes_dark from "@amcharts/amcharts4/themes/dark";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";

am4core.useTheme(am4themes_dark);
am4core.useTheme(am4themes_animated);

const SolidGaugeChart = ({
  titleText,
  data,
  legend = true,
  legendPosition,
  legendValign,
  size,
  colors,
  labels,
  innerRadius,
  fontSize,
  isMobile,
  withoutPercent = null,
}) => {
  const chartRef = useRef();
  useEffect(() => {
    if (!chartRef.current) {
      return;
    }
    let chart = am4core.create(chartRef.current, am4charts.RadarChart);

    chart.data = data;

    // Make chart not full circle
    chart.startAngle = -90;
    chart.endAngle = 180;
    chart.innerRadius = am4core.percent(innerRadius);

    // Set number format
    if (withoutPercent) {
      chart.numberFormatter.numberFormat = "#.#";
    } else {
      chart.numberFormatter.numberFormat = "#.#'%'";
    }

    //chart colors
    chart.colors.list = colors.map((color) => am4core.color(color));

    // Create axes
    let categoryAxis = chart.yAxes.push(new am4charts.CategoryAxis());
    categoryAxis.dataFields.category = "label";
    categoryAxis.renderer.grid.template.location = 0;
    categoryAxis.renderer.grid.template.strokeOpacity = 0;
    categoryAxis.renderer.labels.template.horizontalCenter = "right";
    categoryAxis.renderer.labels.template.fontWeight = 500;
    categoryAxis.renderer.labels.template.fontSize = !isMobile ? 0 : fontSize ? fontSize : 10;
    categoryAxis.renderer.labels.template.paddingRight = 45;
    categoryAxis.renderer.labels.template.adapter.add("fill", function (fill, target) {
      return target.dataItem.index >= 0 ? chart.colors.getIndex(target.dataItem.index) : fill;
    });
    categoryAxis.renderer.minGridDistance = 10;

    let categoryAxis2 = chart.yAxes.push(new am4charts.CategoryAxis());
    categoryAxis2.dataFields.category = "data";
    categoryAxis2.renderer.grid.template.location = 0;
    categoryAxis2.renderer.grid.template.strokeOpacity = 0;
    categoryAxis2.renderer.labels.template.horizontalCenter = "right";
    categoryAxis2.renderer.labels.template.fontWeight = 500;
    categoryAxis2.renderer.labels.template.fontSize = !isMobile
      ? 0
      : isMobile && fontSize
      ? fontSize
      : 10;
    categoryAxis2.renderer.labels.template.paddingRight = 10;
    categoryAxis2.renderer.labels.template.adapter.add("fill", function (fill, target) {
      return target.dataItem.index >= 0 ? chart.colors.getIndex(target.dataItem.index) : fill;
    });
    categoryAxis2.renderer.minGridDistance = 10;

    let valueAxis = chart.xAxes.push(new am4charts.ValueAxis());
    valueAxis.renderer.grid.template.strokeOpacity = 0;
    valueAxis.renderer.labels.template.fontSize = 15;
    valueAxis.min = 0;
    valueAxis.max = 100;
    valueAxis.strictMinMax = true;

    // Create series
    let series1 = chart.series.push(new am4charts.RadarColumnSeries());
    series1.dataFields.valueX = "full";
    series1.dataFields.categoryY = "label";
    series1.clustered = false;
    series1.columns.template.cornerRadiusTopLeft = 100;
    series1.columns.template.strokeWidth = 0;
    series1.columns.template.radarColumn.cornerRadius = 100;

    series1.columns.template.adapter.add("fill", function (fill, target) {
      return chart.colors.getIndex(colors.length - 1);
    });

    let series2 = chart.series.push(new am4charts.RadarColumnSeries());
    series2.dataFields.valueX = "data";
    series2.dataFields.categoryY = "label";
    series2.clustered = false;
    series2.columns.template.strokeWidth = 0;
    series2.columns.template.tooltipText = "{label}: [bold]{data}[/]";
    series2.columns.template.radarColumn.cornerRadius = 100;

    series2.columns.template.adapter.add("fill", function (fill, target) {
      return chart.colors.getIndex(target.dataItem.index);
    });

    //Legend
    if (legend && !isMobile) {
      chart.legend = new am4charts.Legend();
      chart.legend.position = legendPosition;
      chart.legend.valign = legendValign;
      chart.legend.marginTop = 70;
      chart.legend.marginLeft = 0;
      chart.legend.marginBottom = 0;
      chart.legend.width = am4core.percent(100);
      let marker = chart.legend.markers.template;
      marker.width = 40;
      marker.height = 40;
      chart.legend.itemContainers.template.clickable = false;
      chart.legend.itemContainers.template.focusable = false;
      chart.legend.labels.template.truncate = false;
      chart.legend.itemContainers.template.cursorOverStyle = am4core.MouseCursorStyle.default;
      for (let i = 0; i < labels.length; i++) {
        chart.legend.data[labels.length - i - 1] = {
          name: labels[i].toUpperCase(),
          fill: colors[i],
        };
      }

      chart.legend.labels.template.fontSize = 20;
    }

    // Add cursor
    chart.cursor = new am4charts.RadarCursor();

    chart.responsive.enabled = true;
    chart.responsive.useDefault = false;

    const createSpriteState = (sprite, stateId) => {
      let res = sprite.states.create(stateId);
      if (res.sprite) {
        return res;
      } else {
        res.sprite = sprite;
        return res;
      }
    }

    if (isMobile) {
      chart.responsive.rules.push({
        relevant: function (target) {
          if (target.pixelWidth < 360) {
            return true;
          }

          return false;
        },
        state: function (target, stateId) {
          if (target instanceof am4charts.RadarChart) {
            const state = createSpriteState(target, stateId);
            if(state.sprite) {
              state.sprite.radius = am4core.percent(75);
            }
            return state;
          }
          return null;
        },
      });
      chart.responsive.rules.push({
        relevant: function (target) {
          if (target.pixelWidth < 340 && target.pixelWidth >= 305) {
            return true;
          }

          return false;
        },
        state: function (target, stateId) {
          if (target instanceof am4charts.RadarChart) {
            if (target.pixelWidth < 340 && target.pixelWidth >= 305) {
              const state = createSpriteState(target, stateId);
              state.sprite.yAxes.values[0].renderer.labels.template.fontSize = 10;
              state.sprite.yAxes.values[1].renderer.labels.template.fontSize = 10;
              state.sprite.yAxes.values[0].renderer.labels.template.paddingRight = 44;
              state.sprite.xAxes.values[0].renderer.labels.template.fontSize = 12;
              return state;
            }
          }
          return null;
        },
      });
      chart.responsive.rules.push({
        relevant: function (target) {
          if (target.pixelWidth < 305 && target.pixelWidth >= 270) {
            return true;
          }

          return false;
        },
        state: function (target, stateId) {
          if (target instanceof am4charts.RadarChart) {
            if (target.pixelWidth < 305 && target.pixelWidth >= 270) {
              const state = createSpriteState(target, stateId);
              state.sprite.yAxes.values[0].renderer.labels.template.fontSize = 9;
              state.sprite.yAxes.values[1].renderer.labels.template.fontSize = 9;
              state.sprite.yAxes.values[0].renderer.labels.template.paddingRight = 38;
              state.sprite.yAxes.values[1].renderer.labels.template.paddingRight = 8;
              state.sprite.xAxes.values[0].renderer.labels.template.fontSize = 10;
              return state;
            }
          }
          return null;
        },
      });
      chart.responsive.rules.push({
        relevant: function (target) {
          if (target.pixelWidth < 270 && target.pixelWidth >= 235) {
            return true;
          }

          return false;
        },
        state: function (target, stateId) {
          if (target instanceof am4charts.RadarChart) {
            if (target.pixelWidth < 270 && target.pixelWidth >= 235) {
              const state = createSpriteState(target, stateId);
              state.sprite.yAxes.values[0].renderer.labels.template.fontSize = 8;
              state.sprite.yAxes.values[1].renderer.labels.template.fontSize = 8;
              state.sprite.yAxes.values[0].renderer.labels.template.paddingRight = 30;
              state.sprite.yAxes.values[1].renderer.labels.template.paddingRight = 6;
              state.sprite.xAxes.values[0].renderer.labels.template.fontSize = 10;
              return state;
            }
          }
          return null;
        },
      });
      chart.responsive.rules.push({
        relevant: function (target) {
          if (target.pixelWidth < 235 && target.pixelWidth >= 215) {
            return true;
          }

          return false;
        },
        state: function (target, stateId) {
          if (target instanceof am4charts.RadarChart) {
            if (target.pixelWidth < 235 && target.pixelWidth >= 215) {
              const state = createSpriteState(target, stateId);
              state.sprite.yAxes.values[0].renderer.labels.template.fontSize = 7.2;
              state.sprite.yAxes.values[1].renderer.labels.template.fontSize = 7.2;
              state.sprite.yAxes.values[0].renderer.labels.template.paddingRight = 28;
              state.sprite.yAxes.values[1].renderer.labels.template.paddingRight = 5;
              state.sprite.xAxes.values[0].renderer.labels.template.fontSize = 10;
              return state;
            }
          }
          return null;
        },
      });
      chart.responsive.rules.push({
        relevant: function (target) {
          if (target.pixelWidth < 215) {
            return true;
          }

          return false;
        },
        state: function (target, stateId) {
          if (target instanceof am4charts.RadarChart) {
            if (target.pixelWidth < 215) {
              const state = createSpriteState(target, stateId);
              state.sprite.yAxes.values[0].renderer.labels.template.fontSize = 6.5;
              state.sprite.yAxes.values[1].renderer.labels.template.fontSize = 6.5;
              state.sprite.yAxes.values[0].renderer.labels.template.paddingRight = 28;
              state.sprite.yAxes.values[1].renderer.labels.template.paddingRight = 5;
              state.sprite.xAxes.values[0].renderer.labels.template.fontSize = 9;
              return state;
            }
          }
          return null;
        },
      });
    }

    return () => {
      chart.dispose();
    };
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    chartRef,
    innerRadius,
    legendPosition,
    titleText,
    isMobile,
    colors,
    data,
    labels,
    fontSize,
    legend,
    legendValign,
  ]);

  return (
    <div
      className="solid-gauge-chart mx-auto"
      ref={chartRef}
      style={{ width: isMobile ? "100%" : "60%", height: size }}
    />
  );
};

export default SolidGaugeChart;
