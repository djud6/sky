import React, { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";
import { InputText } from "primereact/inputtext";
import { Button } from "primereact/button";
import ChartCard from "./ChartCard";
import MultiSelectDropdown from "../Forms/MultiSelectDropdown";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import { isMobileDevice } from "../../../helpers/helperFunctions";

am4core.useTheme(am4themes_animated);

const AssetChecksChart = ({ chartParams = [], title = "", description = "", dataReady, error }) => {
  const locations = chartParams.map((item) => {
    return {
      name: Object.keys(item)[0],
      code: Object.keys(item)[0],
    };
  });
  const [dataset, setDataset] = useState([]);
  const [selectedLocations, setSelectedLocations] = useState(locations.slice(0, 1));
  const [filter, setFilter] = useState("");
  const { t } = useTranslation();
  const isMobile = isMobileDevice();
  const chartRef = useRef();

  useEffect(() => {
    if (dataReady) {
      setSelectedLocations(locations.slice(0, 1));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataReady]);

  useEffect(() => {
    setDataset(chartParams);
    if (!chartRef.current) {
      return;
    }

    // Create chart instance
    let chart = am4core.create(chartRef.current, am4charts.XYChart);
    chart.colors.step = 2;

    chart.legend = new am4charts.Legend();
    chart.legend.position = "top";
    chart.legend.paddingBottom = 5;
    chart.legend.labels.template.maxWidth = 95;

    let yAxis = chart.yAxes.push(new am4charts.CategoryAxis());
    yAxis.dataFields.category = "category";
    yAxis.renderer.cellStartLocation = 0.1;
    yAxis.renderer.cellEndLocation = 0.9;
    yAxis.renderer.grid.template.location = 0;

    let xAxis = chart.xAxes.push(new am4charts.ValueAxis());
    xAxis.min = 0;

    function createSeries(value, name) {
      let series = chart.series.push(new am4charts.ColumnSeries());
      series.dataFields.valueX = value;
      series.dataFields.categoryY = "category";
      series.columns.template.tooltipText = "{name}: [bold]{valueX}[/]";
      series.columns.template.height = am4core.percent(100);
      series.name = name;

      series.events.on("hidden", arrangeColumns);
      series.events.on("shown", arrangeColumns);

      let bullet = series.bullets.push(new am4charts.LabelBullet());
      bullet.interactionsEnabled = false;
      bullet.dx = 30;
      bullet.label.text = "{valueX}";
      bullet.label.fill = am4core.color("#000");

      return series;
    }

    chart.data = chartParams
      .map((item) => {
        return {
          category: Object.keys(item)[0],
          asset_count: item[Object.keys(item)[0]].reduce(
            (acc, value) => Math.max(acc, value.asset_count),
            0
          ),
          checks_count: item[Object.keys(item)[0]].reduce(
            (acc, value) => acc + value.daily_check_count,
            0
          ),
        };
      })
      .filter((location) => selectedLocations.map((item) => item.name).includes(location.category));

    createSeries("asset_count", t("assetChecksChart.number_of_assets"));
    createSeries("checks_count", t("assetChecksChart.number_of_checks"));

    function arrangeColumns() {
      let series = chart.series.getIndex(0);

      let w = 1 - xAxis.renderer.cellStartLocation - (1 - xAxis.renderer.cellEndLocation);
      if (series.dataItems.length > 1) {
        let x0 = yAxis.getX(series.dataItems.getIndex(0), "categoryY");
        let x1 = yAxis.getX(series.dataItems.getIndex(1), "categoryY");
        let delta = ((x1 - x0) / chart.series.length) * w;
        if (am4core.isNumber(delta)) {
          let middle = chart.series.length / 2;

          let newIndex = 0;
          chart.series.each(function (series) {
            if (!series.isHidden && !series.isHiding) {
              series.dummyData = newIndex;
              newIndex++;
            } else {
              series.dummyData = chart.series.indexOf(series);
            }
          });
          let visibleCount = newIndex;
          let newMiddle = visibleCount / 2;

          chart.series.each(function (series) {
            let trueIndex = chart.series.indexOf(series);
            let newIndex = series.dummyData;

            let dx = (newIndex - trueIndex + middle - newMiddle) * delta;

            series.animate(
              { property: "dx", to: dx },
              series.interpolationDuration,
              series.interpolationEasing
            );
            series.bulletsContainer.animate(
              { property: "dx", to: dx },
              series.interpolationDuration,
              series.interpolationEasing
            );
          });
        }
      }
    }

    return () => {
      // Need to destroy the chart on unmount
      chart.dispose();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    chartRef.current,
    JSON.stringify(chartParams), // eslint-disable-line
    JSON.stringify(selectedLocations), // eslint-disable-line
    JSON.stringify(dataset), // eslint-disable-line
  ]);

  let maxSelectedLoctaions = 3;
  if (!isMobile) maxSelectedLoctaions = 5;

  const changeHandler = (e) => {
    setSelectedLocations(e.value);
  };

  const panelFooterTemplate = () => {
    const length = selectedLocations ? selectedLocations.length : 0;
    return (
      <div className="p-py-2 p-px-3">
        <b>{length}</b> item{length > 1 ? "s" : ""} selected out of <b>{maxSelectedLoctaions}</b>
      </div>
    );
  };
  const multiselectHeaderTemplate = () => {
    return (
      <div className="p-multiselect-header">
        <div className="p-multiselect-filter-container">
          <InputText
            type="text"
            className="p-inputtext-sm"
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
  const filteredLocations = locations.filter(
    (location) =>
      location.name.toUpperCase().includes(filter.toUpperCase()) ||
      selectedLocations.map((item) => item.name).includes(location.name)
  );
  return (
    <ChartCard
      title={title.length ? title : t("assetChecksChart.title")}
      tooltipName={"asset_checks"}
    >
      {dataReady ? (
        error ? (
          <FullWidthSkeleton height={"550px"} error />
        ) : (
          <div className="container mt-3">
            <div className="row">
              <div className="p-d-flex p-jc-end p-mb-3 p-mr-3 w-100">
                <div className="custom-multi-select">
                  <MultiSelectDropdown
                    value={selectedLocations}
                    options={filteredLocations}
                    onChange={changeHandler}
                    placeholder={t("stackedClusteredChart.select_location")}
                    display="chip"
                    panelHeaderTemplate={multiselectHeaderTemplate}
                    panelFooterTemplate={panelFooterTemplate}
                    optionLabel="name"
                    selectionLimit={maxSelectedLoctaions}
                  />
                </div>
              </div>
              <div className="w-100">
                <div className="p-d-flex p-jc-center">
                  {isMobile ? (
                    <div style={{ width: "100%", overflow: "auto" }}>
                      <div ref={chartRef} style={{ width: "500px", height: "400px" }} />
                    </div>
                  ) : (
                    <div ref={chartRef} style={{ width: "100%", height: "400px" }} />
                  )}
                </div>
              </div>
            </div>
          </div>
        )
      ) : (
        <FullWidthSkeleton height={"550px"} />
      )}
    </ChartCard>
  );
};

export default AssetChecksChart;
