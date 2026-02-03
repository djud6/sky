import React, { useEffect, useRef } from "react";
import * as am4core from "@amcharts/amcharts4/core";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";

am4core.useTheme(am4themes_animated);

const PictorialSliceCard = ({ budget = 40000, usage, height }) => {
  const chartRef = useRef();

  useEffect(() => {
    let capacity = budget;
    let value = usage;
    let circleSize = 0.8;

    if (!chartRef.current) {
      return;
    }

    let component = am4core.create(chartRef.current, am4core.Container);
    component.width = am4core.percent(100);
    component.height = am4core.percent(100);

    let chartContainer = component.createChild(am4core.Container);
    chartContainer.x = am4core.percent(50);
    chartContainer.y = am4core.percent(50);

    let circle = chartContainer.createChild(am4core.Circle);
    circle.fill = am4core.color("#dadada");

    let circleMask = chartContainer.createChild(am4core.Circle);

    let waves = chartContainer.createChild(am4core.WavedRectangle);
    waves.fill = am4core.color("#34a4eb");
    waves.mask = circleMask;
    waves.horizontalCenter = "middle";
    waves.waveHeight = 15;
    waves.waveLength = 30;
    waves.y = 500;
    circleMask.y = -500;

    component.events.on("maxsizechanged", function () {
      let smallerSize = Math.min(component.pixelWidth, component.pixelHeight);
      let radius = (smallerSize * circleSize) / 2;

      circle.radius = radius;
      circleMask.radius = radius;
      waves.height = 1000;
      waves.width = Math.max(component.pixelWidth, component.pixelHeight);

      //capacityLabel.y = radius;

      let labelRadius = radius + 20;

      capacityLabel.path =
        am4core.path.moveTo({ x: -labelRadius, y: 0 }) +
        am4core.path.arcToPoint({ x: labelRadius, y: 0 }, labelRadius, labelRadius);
      capacityLabel.locationOnPath = 0.5;

      setValue(value);
    });

    function setValue(value) {
      let k = capacity > value ? 1 - value / capacity : 1 - capacity / value;
      let y = -circle.radius - waves.waveHeight + k * circle.pixelRadius * 2;
      waves.animate(
        [
          { property: "y", to: y },
          { property: "waveHeight", to: 10, from: 15 },
          { property: "x", from: -50, to: 0 },
        ],
        5000,
        am4core.ease.elasticOut
      );
      circleMask.animate(
        [
          { property: "y", to: -y },
          { property: "x", from: 50, to: 0 },
        ],
        5000,
        am4core.ease.elasticOut
      );
    }

    let label = chartContainer.createChild(am4core.Label);
    let formattedValue = component.numberFormatter.format(value, "#.#a");
    formattedValue = formattedValue.toUpperCase();

    label.text = formattedValue + " Litres";
    label.fill = am4core.color("#fff");
    label.fontSize = 30;
    label.horizontalCenter = "middle";

    let capacityLabel = chartContainer.createChild(am4core.Label);
    // For future use one we have the budgeted value
    // let formattedCapacity = component.numberFormatter.format(capacity, "#.#a").toUpperCase();;
    // capacityLabel.text = "Capacity " + formattedCapacity + " Litres";
    capacityLabel.fill = am4core.color("#34a4eb");
    capacityLabel.fontSize = 20;
    capacityLabel.textAlign = "middle";
    capacityLabel.padding(0, 0, 0, 0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [usage]);

  return <div ref={chartRef} style={{ width: "100%", height: `${height}` }} />;
};

export default PictorialSliceCard;
