import React, { useLayoutEffect, useRef } from "react";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4plugins_forceDirected from "@amcharts/amcharts4/plugins/forceDirected";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";

am4core.useTheme(am4themes_animated);

const TreeChart = ({ chartParams, height }) => {
  const chartRef = useRef();

  useLayoutEffect(() => {
    if (!chartRef.current) {
      return;
    }
    // Create chart
    let chart = am4core.create(chartRef.current, am4plugins_forceDirected.ForceDirectedTree);
    // Create series
    let series = chart.series.push(new am4plugins_forceDirected.ForceDirectedSeries());
    // Set data
    series.data = chartParams;
    // Set up data fields
    series.dataFields.value = "value";
    series.dataFields.name = "name";
    series.dataFields.children = "children";
    series.nodes.template.outerCircle.filters.push(new am4core.DropShadowFilter());
    series.nodes.template.tooltipText = "{name}:{value}";
    // series.nodes.template.fillOpacity = 1;
    series.nodes.template.togglable = true;
    series.manyBodyStrength = -5;
    series.links.template.strokeWidth = 1;
    series.links.template.distance = 2;
    series.nodes.template.label.hideOversized = true;
    series.nodes.template.label.truncate = true;
    // Add labels
    series.nodes.template.label.text = "{name}";
    series.fontSize = 10;
    series.minRadius = am4core.percent(2);
    series.maxRadius = 80;

    return () => {
      chart.dispose();
    };
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chartRef.current, JSON.stringify(chartParams)]);

  return <div ref={chartRef} style={{ width: "100%", height: height }} />;
};

export default TreeChart;
