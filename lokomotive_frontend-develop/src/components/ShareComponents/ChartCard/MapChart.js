import React, { useEffect, useRef } from "react";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4maps from "@amcharts/amcharts4/maps";
import am4geodata_map from "@amcharts/amcharts4-geodata/region/world/northAmericaLow";
import am4geodata_usaLow from "@amcharts/amcharts4-geodata/usaLow";
import am4geodata_caLow from "@amcharts/amcharts4-geodata/canadaLow";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";

am4core.useTheme(am4themes_animated);

const MapChart = ({ datasets = [], height = "550px" }) => {
  const chartRef = useRef();
  useEffect(() => {
    if (!chartRef.current) {
      return;
    }

    let myChart = am4core.create(chartRef.current, am4maps.MapChart);

    // this makes initial fade in effect
    myChart.hiddenState.properties.opacity = 0;

    // Set map definition
    myChart.geodata = am4geodata_map;

    // Set projection
    myChart.projection = new am4maps.projections.Albers();

    // Setup inital zoom and geo setting
    myChart.chartContainer.wheelable = false;
    myChart.zoomControl = new am4maps.ZoomControl();
    myChart.homeZoomLevel = 2.72;
    myChart.homeGeoPoint = {
      latitude: 41,
      longitude: -97,
    };

    let setupMapStyle = (polygonSeries) => {
      let polygonTemplate = polygonSeries.mapPolygons.template;
      //setup ploygonTemplate style
      polygonTemplate.tooltipText = "{name}: {value}";
      polygonTemplate.fill = myChart.colors.getIndex(0);

      // Create hover state and set alternative fill color
      let hs = polygonTemplate.states.create("hover");
      hs.properties.fill = myChart.colors.getIndex(1);
    };

    // Create map polygon series
    let polygonSeries = myChart.series.push(new am4maps.MapPolygonSeries());
    polygonSeries.useGeodata = true;
    polygonSeries.calculateVisualCenter = true;
    setupMapStyle(polygonSeries);

    // add usa series
    let usaSeries = myChart.series.push(new am4maps.MapPolygonSeries());
    usaSeries.geodata = am4geodata_usaLow;
    setupMapStyle(usaSeries);

    // add canada series
    let caSeries = myChart.series.push(new am4maps.MapPolygonSeries());
    caSeries.geodata = am4geodata_caLow;
    setupMapStyle(caSeries);

    // Load data when map polygons are ready
    myChart.events.on("ready", loadStores);

    // Loads store data
    function loadStores() {
      let mapData = [];
      datasets.forEach((location) => {
        let location_name = Object.keys(location)[0];
        let location_data = Object.values(location)[0];
        let dataPoint = { ...location_data, value: location_data["assets"], city: location_name };
        // skip the locaiton without latitude or longitude
        if (dataPoint["latitude"] !== 0 && dataPoint["longitude"] !== 0) mapData.push(dataPoint);
      });

      let imageSeries = myChart.series.push(new am4maps.MapImageSeries());

      imageSeries.data = mapData;
      imageSeries.dataFields.value = "value";

      let imageTemplate = imageSeries.mapImages.template;
      imageTemplate.nonScaling = true;
      imageTemplate.propertyFields.latitude = "latitude";
      imageTemplate.propertyFields.longitude = "longitude";

      let circle = imageTemplate.createChild(am4core.Circle);
      circle.fillOpacity = 0.7;
      // circle.propertyFields.fill = "color";
      circle.tooltipText = "{city}: [bold]{value}[/]";

      let label = imageTemplate.createChild(am4core.Label);
      label.text = "{value}";
      label.fill = am4core.color("#fff");
      label.verticalCenter = "middle";
      label.horizontalCenter = "middle";

      label.events.on("over", (e) => {
        e.target.hide();
      });

      label.events.on("out", (e) => {
        setTimeout(() => {
          e.target.show();
        }, 500);
      });

      imageSeries.heatRules.push({
        target: circle,
        property: "radius",
        min: 10,
        max: 20,
        dataField: "value",
      });
    }

    return () => {
      // Need to destroy the chart on unmount
      myChart.dispose();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chartRef.current, JSON.stringify(datasets)]);

  return <div ref={chartRef} style={{ width: "100%", height: height }} />;
};

export default MapChart;
