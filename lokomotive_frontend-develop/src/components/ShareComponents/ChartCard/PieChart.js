import React, { useLayoutEffect } from "react";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import am4themes_dark from "@amcharts/amcharts4/themes/dark";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";

am4core.useTheme(am4themes_dark);
am4core.useTheme(am4themes_animated);

const PieChart = ({ titleText, data, legend = true, legendPosition, size, innerRadius = 40 }) => {
  useLayoutEffect(() => {
    var chart = am4core.create(JSON.stringify(data), am4charts.PieChart3D);
    chart.hiddenState.properties.opacity = 0; // this creates initial fade-in

    var title = chart.titles.create();
    if (titleText) {
      title.text = titleText;
      title.fontSize = 25;
      title.marginBottom = 30;
    }

    if (legend) {
      chart.legend = new am4charts.Legend();
      chart.legend.position = legendPosition;
      chart.legend.marginTop = 0;
      chart.legend.marginBottom = 0;
    }

    chart.data = data;
    chart.innerRadius = am4core.percent(innerRadius);
    chart.radius = am4core.percent(70);

    var series = chart.series.push(new am4charts.PieSeries3D());
    series.dataFields.value = "data";
    series.dataFields.category = "label";
    series.labels.template.truncate = true;
    series.labels.template.fontSize = 12;
    series.labels.template.fontWeight = "bold";

    series.labels.template.maxWidth = 130;
    series.labels.template.wrap = true;

    series.slices.template.propertyFields.fill = "color";
    series.slices.template.cornerRadius = 5;
    series.slices.template.marginLeft = 5;
    series.colors.step = 3;

    chart.responsive.enabled = true;
    chart.responsive.useDefault = false;
    chart.responsive.rules.push({
      relevant: function (target) {
        if (target.pixelWidth <= 420) {
          return true;
        }
        return false;
      },
      state: function (target, stateId) {
        if (target instanceof am4charts.Chart) {
          var state = target.states.create(stateId);
          state.properties.paddingTop = 0;
          state.properties.paddingRight = 25;
          state.properties.paddingBottom = 0;
          state.properties.paddingLeft = 25;
          return state;
        } else if (
          target instanceof am4charts.AxisLabelCircular ||
          target instanceof am4charts.PieTick
        ) {
          //eslint-disable-next-line
          var state = target.states.create(stateId);
          state.properties.disabled = true;
          return state;
        }
        return null;
      },
    });

    return () => {
      chart.dispose();
    };
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(data), innerRadius, legendPosition, titleText]);

  return <div id={JSON.stringify(data)} style={{ width: "100%", height: size }} />;
};

export default PieChart;
