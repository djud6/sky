import React, { useEffect, useState, useRef } from "react";
import { useTranslation } from "react-i18next";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import am4themes_dark from "@amcharts/amcharts4/themes/dark";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";
import ChartCard from "./ChartCard";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import ChartLegend from "../ChartLegend";
import { isMobileDevice } from "../../../helpers/helperFunctions";

const OperationalCostChart = ({
  chartParams = [],
  title = "",
  description = "",
  dataReady,
  error,
  height,
  toggleLegend,
}) => {
  const { t } = useTranslation();
  const [dataset, setDataset] = useState([]);
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const isMobile = isMobileDevice();

  const getLocationData = (selectedLocation) => {
    const originalLocationObject = dataset.filter((location) => {
      return Object.keys(location)[0] === selectedLocation.name;
    });
    const newLocationObject = {
      ...originalLocationObject[0][selectedLocation.name],
      location: selectedLocation.name,
    };
    return newLocationObject;
  };

  const chartRef = useRef();
  const legendRef = useRef();

  useEffect(() => {
    if (!chartRef.current) {
      return;
    }

    setDataset(chartParams);
    am4core.useTheme(am4themes_dark);
    am4core.useTheme(am4themes_animated);

    let chart = am4core.create(chartRef.current, am4charts.XYChart);

    chart.paddingRight = 20;

    let listOfLocations = [];
    if (dataset.length > 0) {
      dataset.map((location) => listOfLocations.push(Object.keys(location)[0]));
      listOfLocations = listOfLocations.map((location) => ({ name: location, code: location }));

      setLocations(listOfLocations);
    }

    if (locations.length > 0) chart.data = getLocationData(selectedLocation);

    let data = [];
    for (let key in chart.data) {
      let i = parseInt(key);
      if (chart.data[i] === undefined) {
        continue;
      }
      data.push(chart.data[i]);
      if (!Number.isNaN(i)) {
        if (i > 0) {
          // add color to previous data item depending on whether current value is less or more than previous value
          if (chart.data[i].percentage_change <= 25) {
            data[i - 1].color = "#00FF00";
          } else {
            data[i - 1].color = "#FF0000";
          }
        }
        //add date
        let month = chart.data[i].month;
        let year = chart.data[i].year;
        data[i].date = new Date(month + " 1, " + year);
      }
    }
    chart.data = data;

    chart.numberFormatter.numberFormat = ".##";

    let dateAxis = chart.xAxes.push(new am4charts.DateAxis());
    dateAxis.renderer.grid.template.location = 0;
    dateAxis.renderer.axisFills.template.disabled = true;
    dateAxis.renderer.ticks.template.disabled = true;

    let valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.tooltip.disabled = true;
    valueAxis.renderer.minWidth = 35;
    valueAxis.renderer.axisFills.template.disabled = true;
    valueAxis.renderer.ticks.template.disabled = true;

    let series = chart.series.push(new am4charts.LineSeries());
    series.dataFields.dateX = "date";
    series.dataFields.valueY = "cost_per_asset";
    series.strokeWidth = 2;
    series.tooltipText =
      "Cost per asset: [bold]{valueY}[/] \n Percentage change: [bold]{percentage_change}%";

    let interfaceColors = new am4core.InterfaceColorSet();

    let bullet = series.bullets.push(new am4charts.Bullet());
    bullet.width = 10;
    bullet.height = 10;
    bullet.horizontalCenter = "middle";
    bullet.verticalCenter = "middle";
    let rectangle = bullet.createChild(am4core.Rectangle);
    rectangle.stroke = interfaceColors.getFor("background");
    rectangle.strokeWidth = 2;
    rectangle.width = 10;
    rectangle.height = 10;

    // set stroke property field
    series.propertyFields.stroke = "color";

    chart.cursor = new am4charts.XYCursor();

    chart.legend = new am4charts.Legend();
    chart.legend.position = "bottom";
    chart.legend.marginTop = 0;
    chart.legend.marginBottom = 0;
    let marker = chart.legend.markers.template;
    marker.width = 40;
    marker.height = 2;
    chart.legend.itemContainers.template.clickable = false;
    chart.legend.itemContainers.template.focusable = false;
    chart.legend.itemContainers.template.cursorOverStyle = am4core.MouseCursorStyle.default;
    chart.legend.data = [
      {
        name: "Costs increase < 25%",
        fill: "#00FF00",
      },
      {
        name: "Costs increase > 25%",
        fill: "#FF0000",
      },
    ];

    let legendContainer;
    if (isMobile) {
      legendContainer = am4core.create(legendRef.current, am4core.Container);
      legendContainer.width = am4core.percent(100);
      legendContainer.height = am4core.percent(100);
      chart.legend.parent = legendContainer;
    }

    return () => {
      chart.dispose();
      if (legendContainer) legendContainer.dispose();
    };
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    chartRef.current,
    legendRef.current,
    JSON.stringify(chartParams), // eslint-disable-line
    JSON.stringify(selectedLocation), // eslint-disable-line
    JSON.stringify(dataset), // eslint-disable-line
  ]);

  useEffect(() => {
    if (locations.length > 0) {
      if (!selectedLocation) {
        setSelectedLocation(locations[0]);
      }
    }
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [locations.length, selectedLocation]);

  const changeHandler = (code) => {
    let selected = locations.find((location) => location.code === code);
    setSelectedLocation(selected);
  };

  let filteredLocations;
  filteredLocations = locations.filter((location) => location.name.toUpperCase());
  return (
    <ChartCard
      title={title.length ? title : t("costIndicatorChartCard.operation_costs")}
      tooltipName={"operation_cost_by_location"}
    >
      {dataReady ? (
        error ? (
          <FullWidthSkeleton height={height} error />
        ) : (
          <div className="container mt-3">
            <div className="row">
              <div className="col-12">
                <div className="p-d-flex p-jc-end p-mb-2 p-mr-3">
                  {filteredLocations && !!selectedLocation ? (
                    <div className={`custom-multi-select ${!isMobile && "mt-4"}`}>
                      <FormDropdown
                        className="w-100"
                        defaultValue={selectedLocation}
                        onChange={changeHandler}
                        options={filteredLocations}
                        loading={!dataReady}
                        disabled={!dataReady}
                        dataReady={dataReady}
                        reset="disabled"
                        plain_dropdown
                      />
                    </div>
                  ) : null}
                </div>
                <div className="p-d-flex p-jc-center">
                  {isMobile ? (
                    <div style={{ width: "100%", overflow: "auto" }}>
                      <div
                        style={{ width: "500px", height: height }}
                        id="operation-cost-chart-div"
                        ref={chartRef}
                      />
                    </div>
                  ) : (
                    <div
                      style={{ width: "100%", height: height }}
                      ref={chartRef}
                      id="operation-cost-chart-div"
                    />
                  )}
                </div>
              </div>
            </div>
            {isMobile && (
              <ChartLegend
                toggleLegend={toggleLegend}
                chartId={"operational-cost-chart"}
                legendRef={legendRef}
              />
            )}
          </div>
        )
      ) : (
        <FullWidthSkeleton height={height === "500px" ? "550px" : "350px"} />
      )}
    </ChartCard>
  );
};

export default OperationalCostChart;
