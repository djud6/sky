import React, { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";
import { Button } from "primereact/button";
import { InputText } from "primereact/inputtext";
import ChartCard from "./ChartCard";
import MultiSelectDropdown from "../../ShareComponents/Forms/MultiSelectDropdown";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import ChartLegend from "../ChartLegend";
import { isMobileDevice } from "../../../helpers/helperFunctions";

am4core.useTheme(am4themes_animated);

const StackedClusteredChart = ({
  chartParams = [],
  title = "",
  description = "",
  dataReady,
  error,
  height,
  toggleLegend,
  loc = "",
}) => {
  const { t } = useTranslation();
  const [filter, setFilter] = useState("");
  const [dataset, setDataset] = useState([]);
  const [locations, setLocations] = useState([]);
  const [topThreeLocs, setTopThreeLocs] = useState([]);
  const [selectedLocations, setSelectedLocations] = useState([]);
  const isMedianScreen = useMediaQuery({ query: `(max-width: 1300px)` });
  const isMobile = isMobileDevice();

  let maxSelectedLoctaions = 8;
  if (isMedianScreen && !isMobile) maxSelectedLoctaions = 5;
  if (isMobile) maxSelectedLoctaions = 3;

  const getLocationData = (selectedLocation) => {
    const originalLocationObject = dataset.filter((location) => {
      return Object.keys(location)[0] === selectedLocation.name;
    });
    const locationName = Object.keys(originalLocationObject[0])[0];
    const newLocationObject = {
      ...originalLocationObject[0][selectedLocation.name],
      location: locationName,
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

    // Create chart instance
    let chart = am4core.create(chartRef.current, am4charts.XYChart);

    let listOfLocations = [];
    if (dataset.length > 0) {
      dataset.map((location) => listOfLocations.push(Object.keys(location)[0]));
      listOfLocations = listOfLocations.map((location) => ({ name: location, code: location }));

      setLocations(listOfLocations);
    }

    if (locations.length > 0) {
      let arr = [];
      selectedLocations.map((loc) => arr.push(getLocationData(loc)));
      chart.data = [...arr];
    }

    const maxItemsBeforeLabelsRotate = 20;

    // Create axes
    let categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    categoryAxis.dataFields.category = t("stackedClusteredChart.location");
    if (chart.data.length > maxItemsBeforeLabelsRotate)
      categoryAxis.renderer.labels.template.rotation = 270;
    categoryAxis.title.text = t("stackedClusteredChart.events");
    categoryAxis.renderer.grid.template.location = 0;
    categoryAxis.renderer.minGridDistance = 20;
    categoryAxis.renderer.cellStartLocation = 0.1;
    categoryAxis.renderer.cellEndLocation = 0.9;

    let valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.min = 0;
    valueAxis.max = 100;
    valueAxis.title.text = t("stackedClusteredChart.event_count");

    // Create series
    function createSeries(field, name, stacked, color) {
      let series = chart.series.push(new am4charts.ColumnSeries());
      series.dataFields.valueY = field;
      series.dataFields.categoryX = t("stackedClusteredChart.location");
      series.name = name;
      series.columns.template.tooltipText = "{name}: [bold]{valueY.formatNumber('#.##')}%[/]";
      series.stacked = stacked;
      series.columns.template.width = am4core.percent(95);
      series.fill = am4core.color(color);
      series.stroke = am4core.color("white");
    }

    createSeries(
      "complete_accidents_percentage",
      t("stackedClusteredChart.complete_accidents"),
      false,
      "#0E8F24"
    );
    createSeries(
      "incomplete_accidents_percentage",
      t("stackedClusteredChart.incomplete_accidents"),
      true,
      "#350821"
    );
    createSeries(
      "complete_maintenance_percentage",
      t("stackedClusteredChart.complete_maintenance"),
      false,
      "#0E8F24"
    );
    createSeries(
      "incomplete_maintenance_percentage",
      t("stackedClusteredChart.incomplete_maintenance"),
      true,
      "#A81968"
    );
    createSeries(
      "complete_repairs_percentage",
      t("stackedClusteredChart.complete_repairs"),
      false,
      "#0E8F24"
    );
    createSeries(
      "incomplete_repairs_percentage",
      t("stackedClusteredChart.incomplete_repairs"),
      true,
      "#5C2945"
    );

    // Add legend
    let legendContainer;
    chart.legend = new am4charts.Legend();
    if (isMobile) {
      legendContainer = am4core.create(legendRef.current, am4core.Container);
      legendContainer.width = am4core.percent(100);
      legendContainer.height = am4core.percent(100);
      chart.legend.parent = legendContainer;
    }

    return () => {
      // Need to destroy the chart on unmount
      chart.dispose();
      if (legendContainer) legendContainer.dispose();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    chartRef.current,
    legendRef.current,
    JSON.stringify(chartParams), // eslint-disable-line
    JSON.stringify(selectedLocations), // eslint-disable-line
    JSON.stringify(dataset), // eslint-disable-line
  ]);

  useEffect(() => {
    if (locations.length > 0) {
      if (selectedLocations.length === 0) {
        if (topThreeLocs.length === 0) {
          let topOneCount = -1;
          let topTwoCount = -1;
          let topThreeCount = -1;
          chartParams.forEach((location) => {
            const perLocCount = Object.values(location[Object.keys(location)[0]]).reduce(
              (a, b) => a + b
            );
            if (perLocCount > topOneCount) {
              topOneCount = perLocCount;
              topThreeLocs[0] = { name: Object.keys(location)[0], code: Object.keys(location)[0] };
            } else if (perLocCount > topTwoCount) {
              topTwoCount = perLocCount;
              topThreeLocs[1] = { name: Object.keys(location)[0], code: Object.keys(location)[0] };
            } else if (perLocCount > topThreeCount) {
              topThreeCount = perLocCount;
              topThreeLocs[2] = { name: Object.keys(location)[0], code: Object.keys(location)[0] };
            }
          });
          setTopThreeLocs(topThreeLocs);
        }
        setSelectedLocations(topThreeLocs);
      }
    }
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [locations, selectedLocations]);

  const changeHandler = (e) => {
    setSelectedLocations(e.value);
  };

  const panelFooterTemplate = () => {
    const length = selectedLocations ? selectedLocations.length : 0;
    return (
      <div className="p-py-2 p-px-3 text">
        <b>{length}</b> item{length > 1 ? "s" : ""} selected out of <b>{maxSelectedLoctaions}</b>
      </div>
    );
  };
  const multiselectHeaderTemplate = () => {
    return (
      <div className="p-multiselect-header">
        <div className="p-multiselect-filter-container">
          <InputText
            className="w-100"
            type="text"
            placeholder="Filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>
        <Button
          icon="pi pi-times"
          className="p-button-rounded p-button-text p-button-secondary"
          onClick={() => setFilter("")}
        />
      </div>
    );
  };
  let filteredLocations;
  filteredLocations = locations.filter(
    (location) =>
      location.name.toUpperCase().includes(filter.toUpperCase()) ||
      selectedLocations.map((item) => item.name).includes(location.name)
  );

  return (
    <ChartCard
      title={title.length ? title : t("stackedClusteredChart.accidents_maintenance_repairs")}
      tooltipName={"accidents_maintenance_repairs"}
    >
      {dataReady ? (
        error ? (
          <FullWidthSkeleton height={height} error />
        ) : (
          <div className="container mt-3">
            <div className="row">
              <div className="col-12">
                <div className="p-d-flex p-jc-end p-mb-5 p-mr-3">
                  {filteredLocations && selectedLocations.length !== 0 ? (
                    <div className="custom-multi-select">
                      <MultiSelectDropdown
                        classNames="w-100"
                        value={selectedLocations}
                        options={filteredLocations}
                        onChange={changeHandler}
                        display="chip"
                        panelHeaderTemplate={multiselectHeaderTemplate}
                        panelFooterTemplate={panelFooterTemplate}
                        selectionLimit={maxSelectedLoctaions}
                      />
                    </div>
                  ) : null}
                </div>
                <div className="p-d-flex p-jc-center">
                  <div style={{ width: "100%", height: height }} ref={chartRef} />
                </div>
              </div>
            </div>
            {isMobile && (
              <ChartLegend
                toggleLegend={toggleLegend}
                chartId={`stack-cluster-chart${loc}`}
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

export default StackedClusteredChart;
