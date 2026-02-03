import React, { useEffect, useRef } from "react";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4maps from "@amcharts/amcharts4/maps";
import am4geodata_worldLow from "@amcharts/amcharts4-geodata/worldLow";
import am4themes_frozen from "@amcharts/amcharts4/themes/frozen";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";
import * as Constants from "../../../constants";

/* Chart code */
// Themes begin
am4core.useTheme(am4themes_frozen);
am4core.useTheme(am4themes_animated);
// Themes end

const RoutesMapCard = ({ transferType, originLocations, destinationLocations }) => {
  const chartRef = useRef();

  useEffect(() => {
    if (!chartRef.current) {
      return;
    }

    // Create map instance
    let chart = am4core.create(chartRef.current, am4maps.MapChart);
    let interfaceColors = new am4core.InterfaceColorSet();

    // Set map definition
    chart.geodata = am4geodata_worldLow;
    // Set projection
    chart.projection = new am4maps.projections.Mercator();
    // Export
    chart.exporting.menu = new am4core.ExportMenu();
    // Zoom control
    chart.zoomControl = new am4maps.ZoomControl();

    let targetSVG =
      "M9,0C4.029,0,0,4.029,0,9s4.029,9,9,9s9-4.029,9-9S13.971,0,9,0z M9,15.93 c-3.83,0-6.93-3.1-6.93-6.93S5.17,2.07,9,2.07s6.93,3.1,6.93,6.93S12.83,15.93,9,15.93 M12.5,9c0,1.933-1.567,3.5-3.5,3.5S5.5,10.933,5.5,9S7.067,5.5,9,5.5 S12.5,7.067,12.5,9z";
    let planeSVG =
      "M 200 16 L 56 16 C 42.746094 16 32 26.746094 32 40 L 32 200 C 32 206.824219 34.910156 213.324219 40 217.871094 L 40 227 C 40 234.179688 45.820312 240 53 240 L 67 240 C 74.179688 240 80 234.179688 80 227 L 80 224 L 176 224 L 176 227 C 176 234.179688 181.820312 240 189 240 L 203 240 C 210.179688 240 216 234.179688 216 227 L 216 217.871094 C 221.089844 213.324219 224 206.824219 224 200 L 224 40 C 224 26.746094 213.253906 16 200 16 Z M 73.734375 199.910156 C 66.988281 200.644531 60.507812 197.039062 57.574219 190.917969 C 54.640625 184.796875 55.890625 177.492188 60.691406 172.691406 C 65.492188 167.890625 72.796875 166.640625 78.917969 169.574219 C 85.039062 172.507812 88.644531 178.988281 87.910156 185.734375 C 87.097656 193.203125 81.203125 199.097656 73.734375 199.910156 Z M 118 144 L 56 144 C 51.582031 144 48 140.417969 48 136 L 48 72 C 48 67.582031 51.582031 64 56 64 L 118 64 C 119.105469 64 120 64.894531 120 66 L 120 142 C 120 143.105469 119.105469 144 118 144 Z M 128 48 L 56.230469 48 C 51.929688 48 48.230469 44.699219 48.011719 40.40625 C 47.898438 38.214844 48.691406 36.078125 50.203125 34.488281 C 51.710938 32.898438 53.808594 32 56 32 L 199.769531 32 C 204.070312 32 207.769531 35.300781 207.988281 39.59375 C 208.101562 41.785156 207.308594 43.921875 205.796875 45.511719 C 204.289062 47.101562 202.191406 48 200 48 Z M 138 64 L 200 64 C 204.417969 64 208 67.582031 208 72 L 208 136 C 208 140.417969 204.417969 144 200 144 L 138 144 C 136.894531 144 136 143.105469 136 142 L 136 66 C 136 64.894531 136.894531 64 138 64 Z M 168.089844 185.734375 C 167.355469 178.988281 170.960938 172.507812 177.082031 169.574219 C 183.203125 166.640625 190.507812 167.890625 195.308594 172.691406 C 200.109375 177.492188 201.359375 184.796875 198.425781 190.917969 C 195.492188 197.039062 189.011719 200.644531 182.265625 199.910156 C 174.796875 199.097656 168.902344 193.203125 168.089844 185.734375 Z M 168.089844 185.734375";

    // Texts
    let labelsContainer = chart.createChild(am4core.Container);
    labelsContainer.isMeasured = false;
    labelsContainer.x = 80;
    labelsContainer.y = 27;
    labelsContainer.layout = "horizontal";
    labelsContainer.zIndex = 10;

    let plane = labelsContainer.createChild(am4core.Sprite);
    plane.scale = 0.15;
    plane.path = planeSVG;
    plane.fill = am4core.color("#cc0000");

    let title = labelsContainer.createChild(am4core.Label);
    title.text = "Assets in the city";
    title.fill = am4core.color("#cc0000");
    title.fontSize = 20;
    title.valign = "middle";
    title.dy = 2;
    title.marginLeft = 15;

    let changeLink = chart.createChild(am4core.TextLink);
    changeLink.text = "Click to change origin location";
    changeLink.isMeasured = false;

    changeLink.events.on("hit", function () {
      if (currentOrigin === originImageSeries.dataItems.getIndex(0)) {
        showLines(originImageSeries.dataItems.getIndex(1));
      } else {
        showLines(originImageSeries.dataItems.getIndex(0));
      }
    });

    changeLink.x = 142;
    changeLink.y = 72;
    changeLink.fontSize = 13;

    // The world
    let worldPolygonSeries = chart.series.push(new am4maps.MapPolygonSeries());
    worldPolygonSeries.useGeodata = true;
    worldPolygonSeries.fillOpacity = 0.6;
    worldPolygonSeries.exclude = ["AQ"];

    // Origin series (big targets, London and Vilnius)
    let originImageSeries = chart.series.push(new am4maps.MapImageSeries());

    let originImageTemplate = originImageSeries.mapImages.template;

    originImageTemplate.propertyFields.latitude = "latitude";
    originImageTemplate.propertyFields.longitude = "longitude";
    originImageTemplate.propertyFields.id = "id";

    originImageTemplate.cursorOverStyle = am4core.MouseCursorStyle.pointer;
    originImageTemplate.nonScaling = true;
    originImageTemplate.tooltipText = "{tooltip}";

    originImageTemplate.setStateOnChildren = true;
    originImageTemplate.states.create("hover");

    originImageTemplate.horizontalCenter = "middle";
    originImageTemplate.verticalCenter = "middle";

    let originHitCircle = originImageTemplate.createChild(am4core.Circle);
    originHitCircle.radius = 11;
    originHitCircle.fill = interfaceColors.getFor("background");

    let originTargetIcon = originImageTemplate.createChild(am4core.Sprite);
    originTargetIcon.fill = interfaceColors.getFor("alternativeBackground");
    originTargetIcon.strokeWidth = 0;
    originTargetIcon.scale = 1.3;
    originTargetIcon.horizontalCenter = "middle";
    originTargetIcon.verticalCenter = "middle";
    originTargetIcon.path = targetSVG;

    let originHoverState = originTargetIcon.states.create("hover");
    originHoverState.properties.fill = chart.colors.getIndex(1);

    // when hit on city, change lines
    originImageTemplate.events.on("hit", function (event) {
      showLines(event.target.dataItem);
    });

    // destination series (small targets)
    let destinationImageSeries = chart.series.push(new am4maps.MapImageSeries());
    let destinationImageTemplate = destinationImageSeries.mapImages.template;

    destinationImageTemplate.nonScaling = true;
    destinationImageTemplate.tooltipText = "{title}";
    destinationImageTemplate.fill = interfaceColors.getFor("alternativeBackground");
    destinationImageTemplate.setStateOnChildren = true;
    destinationImageTemplate.states.create("hover");

    destinationImageTemplate.propertyFields.latitude = "latitude";
    destinationImageTemplate.propertyFields.longitude = "longitude";
    destinationImageTemplate.propertyFields.id = "id";

    let destinationHitCircle = destinationImageTemplate.createChild(am4core.Circle);
    destinationHitCircle.radius = 7;
    destinationHitCircle.fillOpacity = 1;
    destinationHitCircle.fill = interfaceColors.getFor("background");

    let destinationTargetIcon = destinationImageTemplate.createChild(am4core.Sprite);
    destinationTargetIcon.scale = 0.7;
    destinationTargetIcon.path = targetSVG;
    destinationTargetIcon.horizontalCenter = "middle";
    destinationTargetIcon.verticalCenter = "middle";

    originImageSeries.data = originLocations;
    destinationImageSeries.data = destinationLocations;

    // Line series
    let lineSeries = chart.series.push(new am4maps.MapLineSeries());
    lineSeries.mapLines.template.line.strokeOpacity = 0.5;

    chart.events.on("ready", function () {
      showLines(originImageSeries.dataItems.getIndex(0));
    });

    let currentOrigin;

    function createArrow(line) {
      var arrow = line.createChild(am4maps.MapLineObject);
      arrow.shouldClone = false;
      arrow.width = 1.5;
      arrow.height = 1.875;
      arrow.mapLine = line;
      arrow.position = 0.5;
      arrow.adjustRotation = true;

      var triangle = arrow.createChild(am4core.Triangle);
      //triangle.shouldClone = false;
      triangle.fillOpacity = 1;
      triangle.width = am4core.percent(100);
      triangle.height = am4core.percent(100);
      triangle.rotation = 90;
      triangle.horizontalCenter = "middle";
      triangle.verticalCenter = "middle";

      return arrow;
    }

    function showLines(origin) {
      let dataContext = origin.dataContext;
      let destinations = dataContext.destinations;

      // clear old
      lineSeries.mapLines.clear();
      lineSeries.toBack();
      worldPolygonSeries.toBack();
      currentOrigin = origin;

      if (destinations) {
        for (var i = 0; i < destinations.length; i++) {
          let line = lineSeries.mapLines.create();
          line.imagesToConnect = [origin.mapImage.id, destinations[i]];

          // Add a map object to line
          let arrow1 = createArrow(line);
          arrow1.position = 0.7;
        }
      }

      title.text = `${dataContext.asset_count} Asset(s) ${transferType} in ` + dataContext.title;
      chart.zoomToGeoPoint(
        { latitude: dataContext.zoomLatitude, longitude: dataContext.zoomLongitude },
        dataContext.zoomLevel,
        true
      );
    }

    let graticuleSeries = chart.series.push(new am4maps.GraticuleSeries());
    graticuleSeries.mapLines.template.line.strokeOpacity = 0.05;

    if (window.innerWidth < Constants.MOBILE_BREAKPOINT) {
      labelsContainer.x = 0;
      plane.scale = 0.1;
      title.wrap = true;
      title.maxWidth = 220;
      changeLink.y = 92;
      changeLink.x = 40;
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [originLocations, destinationLocations]);

  return <div ref={chartRef} style={{ width: "100%", height: "600px" }} />;
};

export default RoutesMapCard;
