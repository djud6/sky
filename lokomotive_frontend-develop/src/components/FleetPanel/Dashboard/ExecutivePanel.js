import React, { useEffect, useState, useCallback, useMemo, useRef } from "react";
import { Responsive as ResponsiveGridLayout } from "react-grid-layout";
import { SizeMe } from "react-sizeme";
import OverviewChartCard from "../../ShareComponents/ChartCard/OverviewChartCard";
import DowntimeChartCard from "../../ShareComponents/ChartCard/DowntimeChartCardNew";
import StackedClusteredChart from "../../ShareComponents/ChartCard/StackedClusteredChart";
import OperationalCostChart from "../../ShareComponents/ChartCard/OperationalCostChart";
import AssetMapChartCard from "../../ShareComponents/ChartCard/AssetMapChartCard";
import AvgMaintenanceChartCard from "../../ShareComponents/ChartCard/AvgMaintenanceChartCard";
import TreeChartCard from "../../ShareComponents/ChartCard/TreeChartCard";
import LeaderboardChartCard from "../../ShareComponents/ChartCard/LeaderboardChartCard";
import AssetUtilChartCard from "../../ShareComponents/ChartCard/AssetUtilChartCard";
import CostPerProcess from "../../ShareComponents/ChartCard/CostPerProcess";
import AccidentChartCard from "../../ShareComponents/ChartCard/AccidentChartCard";
import MaintenceCostChartCard from "../../ShareComponents/ChartCard/MaintenceCostChartCard";
import WorkOrderCompletionTimeCard from "../../ShareComponents/ChartCard/WorkOrderCompletionTimeCard";
import { isMobileDevice } from "../../../helpers/helperFunctions";
import "../../../styles/FleetPanel/customGrid.scss";
import VehicleUtilChartCard from "../../ShareComponents/ChartCard/VehicleUtilChartCard";
import VehicleCostChartCard from "../../ShareComponents/ChartCard/VehicleCostChartCard";
import MTBFChartCard from "../../ShareComponents/ChartCard/MTBFChartCard";

const ExecutivePanel = ({
  overallChartParams,
  avgMaintenanceChartParams,
  downtimeChartParams,
  stackedClusteredChart,
  operationalCostParams,
  mapChartParams,
  assetUtilChartParams,
  clusterChartParams,
  leaderboardChartParams,
  costPerProcessParams,
  workOrderCompletionTimeParams,
  dataReady,
  errors,
  dashboard_layout,
  isEdit,
}) => {
  const gridRef = useRef(null);
  const [isMobile, setIsMobile] = useState(false);
  const smallWidgetHt = 4.5;
  const largeWidgetHt = 6.6;
  const mediumWidgetHt = 5;
  const minHt = 1;
  const gridWidth = gridRef?.current?.state?.size?.width;

  const defaultLayout = {
    lg: [
      { i: "a", x: 0, y: 0, w: 1, h: smallWidgetHt },
      { i: "b", x: 1, y: 0, w: 1, h: smallWidgetHt },
      { i: "c", x: 2, y: 0, w: 1, h: smallWidgetHt },
      { i: "xx", x: 0, y: smallWidgetHt, w: 3, h: largeWidgetHt },
      { i: "d", x: 0, y: smallWidgetHt + largeWidgetHt, w: 3, h: largeWidgetHt },
      { i: "e", x: 0, y: smallWidgetHt + largeWidgetHt * 2, w: 3, h: largeWidgetHt },
      { i: "f", x: 0, y: smallWidgetHt + largeWidgetHt * 3, w: 3, h: largeWidgetHt },
      { i: "g", x: 0, y: smallWidgetHt + largeWidgetHt * 4, w: 3, h: largeWidgetHt },
      { i: "h", x: 0, y: smallWidgetHt + largeWidgetHt * 5, w: 3, h: largeWidgetHt },
      { i: "i", x: 0, y: smallWidgetHt + largeWidgetHt * 6, w: 3, h: mediumWidgetHt },
      { i: "jj", x: 0, y: smallWidgetHt + largeWidgetHt * 7, w: 3, h: mediumWidgetHt },
      { i: "kk", x: 0, y: smallWidgetHt + largeWidgetHt * 7, w: 3, h: mediumWidgetHt },
      { i: "j", x: 0, y: smallWidgetHt + largeWidgetHt * 7, w: 3, h: largeWidgetHt },
    ],
    md: [
      { i: "a", x: 0, y: 0, w: 1, h: smallWidgetHt },
      { i: "b", x: 1, y: 0, w: 1, h: smallWidgetHt },
      { i: "c", x: 2, y: 0, w: 1, h: smallWidgetHt },
      { i: "xx", x: 0, y: smallWidgetHt, w: 3, h: largeWidgetHt },
      { i: "d", x: 0, y: smallWidgetHt + largeWidgetHt, w: 3, h: largeWidgetHt },
      { i: "e", x: 0, y: smallWidgetHt + largeWidgetHt * 2, w: 3, h: largeWidgetHt },
      { i: "f", x: 0, y: smallWidgetHt + largeWidgetHt * 3, w: 3, h: largeWidgetHt },
      { i: "g", x: 0, y: smallWidgetHt + largeWidgetHt * 4, w: 3, h: largeWidgetHt },
      { i: "h", x: 0, y: smallWidgetHt + largeWidgetHt * 5, w: 3, h: largeWidgetHt },
      { i: "i", x: 0, y: smallWidgetHt + largeWidgetHt * 6, w: 3, h: largeWidgetHt },
      { i: "jj", x: 0, y: smallWidgetHt + largeWidgetHt * 7, w: 3, h: largeWidgetHt },
      { i: "kk", x: 0, y: smallWidgetHt + largeWidgetHt * 8, w: 3, h: largeWidgetHt },
      { i: "ll", x: 0, y: smallWidgetHt + largeWidgetHt * 9, w: 3, h: largeWidgetHt },
      { i: "j", x: 0, y: smallWidgetHt + largeWidgetHt * 7, w: 3, h: largeWidgetHt },
    ],
    sm: [
      { i: "a", x: 0, y: 0, w: 1, h: smallWidgetHt },
      { i: "b", x: 1, y: 0, w: 1, h: smallWidgetHt },
      { i: "c", x: 2, y: 0, w: 1, h: smallWidgetHt },
      { i: "xx", x: 0, y: smallWidgetHt, w: 3, h: largeWidgetHt },
      { i: "d", x: 0, y: smallWidgetHt + largeWidgetHt, w: 3, h: largeWidgetHt },
      { i: "e", x: 0, y: smallWidgetHt + largeWidgetHt * 2, w: 3, h: largeWidgetHt },
      { i: "f", x: 0, y: smallWidgetHt + largeWidgetHt * 3, w: 3, h: largeWidgetHt },
      { i: "g", x: 0, y: smallWidgetHt + largeWidgetHt * 4, w: 3, h: largeWidgetHt },
      { i: "h", x: 0, y: smallWidgetHt + largeWidgetHt * 5, w: 3, h: largeWidgetHt },
      { i: "i", x: 0, y: smallWidgetHt + largeWidgetHt * 6, w: 3, h: largeWidgetHt },
      { i: "jj", x: 0, y: smallWidgetHt + largeWidgetHt * 7, w: 3, h: largeWidgetHt },
      { i: "kk", x: 0, y: smallWidgetHt + largeWidgetHt * 8, w: 3, h: largeWidgetHt },
      { i: "ll", x: 0, y: smallWidgetHt + largeWidgetHt * 9, w: 3, h: largeWidgetHt },
      { i: "j", x: 0, y: smallWidgetHt + largeWidgetHt * 7, w: 3, h: largeWidgetHt },
    ],
    xs: [
      { i: "a", x: 0, y: 0, w: 1, h: smallWidgetHt },
      { i: "b", x: 0, y: smallWidgetHt, w: 1, h: smallWidgetHt },
      { i: "c", x: 0, y: smallWidgetHt * 2, w: 1, h: smallWidgetHt },
      { i: "xx", x: 0, y: smallWidgetHt * 3, w: 1, h: mediumWidgetHt },
      { i: "d", x: 0, y: smallWidgetHt * 4, w: 1, h: smallWidgetHt },
      { i: "e", x: 0, y: smallWidgetHt * 5, w: 1, h: smallWidgetHt },
      { i: "f", x: 0, y: smallWidgetHt * 6, w: 1, h: smallWidgetHt },
      { i: "g", x: 0, y: smallWidgetHt * 7, w: 1, h: smallWidgetHt },
      { i: "i", x: 0, y: smallWidgetHt * 9, w: 1, h: largeWidgetHt - 0.1 },
      { i: "jj", x: 0, y: smallWidgetHt * 10, w: 1, h: largeWidgetHt - 0.1 },
      { i: "kk", x: 0, y: smallWidgetHt * 11, w: 1, h: largeWidgetHt - 0.1 },
      { i: "ll", x: 0, y: smallWidgetHt * 12, w: 1, h: largeWidgetHt - 0.1 },
      { i: "j", x: 0, y: smallWidgetHt * 10, w: 1, h: largeWidgetHt },
    ],
    xxs: [
      { i: "a", x: 0, y: 0, w: 1, h: smallWidgetHt },
      { i: "b", x: 0, y: smallWidgetHt, w: 1, h: smallWidgetHt },
      { i: "c", x: 0, y: smallWidgetHt * 2, w: 1, h: smallWidgetHt },
      { i: "xx", x: 0, y: smallWidgetHt * 3, w: 1, h: mediumWidgetHt + 0.2 },
      { i: "d", x: 0, y: smallWidgetHt * 4, w: 1, h: smallWidgetHt },
      { i: "e", x: 0, y: smallWidgetHt * 5, w: 1, h: smallWidgetHt },
      { i: "f", x: 0, y: smallWidgetHt * 6, w: 1, h: smallWidgetHt },
      { i: "g", x: 0, y: smallWidgetHt * 7, w: 1, h: smallWidgetHt },
      { i: "i", x: 0, y: smallWidgetHt * 9, w: 1, h: largeWidgetHt },
      { i: "jj", x: 0, y: smallWidgetHt * 10, w: 1, h: largeWidgetHt },
      { i: "kk", x: 0, y: smallWidgetHt * 11, w: 1, h: largeWidgetHt },
      { i: "ll", x: 0, y: smallWidgetHt * 12, w: 1, h: largeWidgetHt },
      { i: "j", x: 0, y: smallWidgetHt * 10, w: 1, h: largeWidgetHt },
    ],
  };

  const newlyAddedLayout = {
    lg: [
      { i: "jj", x: 0, y: smallWidgetHt + largeWidgetHt * 7, w: 3, h: largeWidgetHt },
      { i: "kk", x: 0, y: smallWidgetHt + largeWidgetHt * 8, w: 3, h: largeWidgetHt },
      { i: "ll", x: 0, y: smallWidgetHt + largeWidgetHt * 9, w: 3, h: mediumWidgetHt },
      { i: "mm", x: 0, y: smallWidgetHt + largeWidgetHt * 10, w: 3, h: mediumWidgetHt },
      { i: "nn", x: 0, y: smallWidgetHt + largeWidgetHt * 11, w: 3, h: mediumWidgetHt },
      { i: "oo", x: 0, y: smallWidgetHt + largeWidgetHt * 12, w: 3, h: mediumWidgetHt },
      { i: "pp", x: 0, y: smallWidgetHt + largeWidgetHt * 13, w: 3, h: mediumWidgetHt },
    ],
    md: [
      { i: "jj", x: 0, y: smallWidgetHt + largeWidgetHt * 7, w: 3, h: largeWidgetHt },
      { i: "kk", x: 0, y: smallWidgetHt + largeWidgetHt * 8, w: 3, h: largeWidgetHt },
      { i: "ll", x: 0, y: smallWidgetHt + largeWidgetHt * 9, w: 3, h: largeWidgetHt },
      { i: "mm", x: 0, y: smallWidgetHt + largeWidgetHt * 10, w: 3, h: largeWidgetHt },
      { i: "nn", x: 0, y: smallWidgetHt + largeWidgetHt * 11, w: 3, h: largeWidgetHt },
      { i: "oo", x: 0, y: smallWidgetHt + largeWidgetHt * 12, w: 3, h: largeWidgetHt },
      { i: "pp", x: 0, y: smallWidgetHt + largeWidgetHt * 13, w: 3, h: largeWidgetHt },
    ],
    sm: [
      { i: "jj", x: 0, y: smallWidgetHt + largeWidgetHt * 7, w: 3, h: largeWidgetHt },
      { i: "kk", x: 0, y: smallWidgetHt + largeWidgetHt * 8, w: 3, h: largeWidgetHt },
      { i: "ll", x: 0, y: smallWidgetHt + largeWidgetHt * 9, w: 3, h: largeWidgetHt },
      { i: "mm", x: 0, y: smallWidgetHt + largeWidgetHt * 10, w: 3, h: largeWidgetHt },
      { i: "nn", x: 0, y: smallWidgetHt + largeWidgetHt * 11, w: 3, h: largeWidgetHt },
      { i: "oo", x: 0, y: smallWidgetHt + largeWidgetHt * 12, w: 3, h: largeWidgetHt },
      { i: "pp", x: 0, y: smallWidgetHt + largeWidgetHt * 13, w: 3, h: largeWidgetHt },
    ],
    xs: [
      { i: "jj", x: 0, y: smallWidgetHt * 10, w: 1, h: largeWidgetHt - 0.1 },
      { i: "kk", x: 0, y: smallWidgetHt * 11, w: 1, h: largeWidgetHt - 0.1 },
      { i: "ll", x: 0, y: smallWidgetHt * 11, w: 1, h: largeWidgetHt - 0.1 },
      { i: "mm", x: 0, y: smallWidgetHt * 12, w: 1, h: largeWidgetHt - 0.1 },
      { i: "nn", x: 0, y: smallWidgetHt * 13, w: 1, h: largeWidgetHt - 0.1 },
      { i: "oo", x: 0, y: smallWidgetHt * 14, w: 1, h: largeWidgetHt - 0.1 },
      { i: "pp", x: 0, y: smallWidgetHt * 15, w: 1, h: largeWidgetHt - 0.1 },
    ],
    xxs: [
      { i: "jj", x: 0, y: smallWidgetHt * 10, w: 1, h: largeWidgetHt },
      { i: "kk", x: 0, y: smallWidgetHt * 11, w: 1, h: largeWidgetHt },
      { i: "ll", x: 0, y: smallWidgetHt * 11, w: 1, h: largeWidgetHt },
      { i: "mm", x: 0, y: smallWidgetHt * 12, w: 1, h: largeWidgetHt },
      { i: "nn", x: 0, y: smallWidgetHt * 13, w: 1, h: largeWidgetHt },
      { i: "oo", x: 0, y: smallWidgetHt * 14, w: 1, h: largeWidgetHt },
      { i: "pp", x: 0, y: smallWidgetHt * 15, w: 1, h: largeWidgetHt },
    ],
  };

  const addNewLayout = (dashboard_layout) => {
    for (let keys in dashboard_layout) {
      let newKeys = newlyAddedLayout[keys];
      // console.log("newKey", newKeys);
      for (let newKey of newKeys) {
        dashboard_layout[keys].push(newKey);
        // console.log("newKey", newKey);
      }
    }
    return dashboard_layout;
  };

  useEffect(() => {
    if (dashboard_layout) {
      dashboard_layout = addNewLayout(dashboard_layout);
      setLayout(dashboard_layout);
      saveToLs("exec_layout", dashboard_layout);
    }
  }, [dashboard_layout]);

  const initialLayout = JSON.parse(window.localStorage.getItem("exec_layout")) || defaultLayout;

  const [layout, setLayout] = useState(initialLayout);
  const [breakPoints, setBreakPoints] = useState([]);

  useEffect(() => {
    if (isMobile) {
      setBreakPoints(["xs", "xxs"]);
    } else {
      setBreakPoints(["lg", "md", "sm"]);
    }
  }, [isMobile]);

  const widgetHeight = useCallback(
    (layout, id, height) => {
      breakPoints.forEach((bp) => {
        if (height) {
          layout[bp][id].h = height;
        } else {
          layout[bp][id].h = defaultLayout[bp][id].h;
        }
      });
    },
    [breakPoints, defaultLayout]
  );

  const widgetPosition = useCallback(
    (layout, id, i) => {
      const currentBp = breakPoints[0];
      if (layout[currentBp][id].h > minHt) {
        breakPoints.forEach((bp) => {
          if (layout[bp][i] && layout[bp][i].y > layout[bp][id].y)
            layout[bp][i].y = layout[bp][i].y + (defaultLayout[bp][id].h - minHt);
        });
      } else {
        breakPoints.forEach((bp) => {
          if (layout[bp][i] && layout[bp][i].y > layout[bp][id].y)
            layout[bp][i].y = layout[bp][i].y - (defaultLayout[bp][id].h - minHt);
        });
      }
    },
    [breakPoints, defaultLayout]
  );

  const toggleLegend = (chartId) => {
    const newLayout = JSON.parse(JSON.stringify(layout));
    let id = chartId === "operational-cost-chart" ? 4 : 5;
    if (newLayout.xs[id].h === smallWidgetHt) {
      newLayout.xs[id].h = largeWidgetHt - 0.5;
      newLayout.xxs[id].h = largeWidgetHt - 0.5;
    } else {
      newLayout.xs[id].h = smallWidgetHt;
      newLayout.xxs[id].h = smallWidgetHt;
    }
    setLayout(newLayout);
  };

  const minimizeWidget = useCallback(
    (e, id, legend = null) => {
      const selectedChart = e.target.previousElementSibling;
      const chartFilter = selectedChart.querySelector(".chart-filter");
      const chartContent = selectedChart.querySelector(".chart-content");
      const currentBp = breakPoints[0];

      const newLayout = JSON.parse(JSON.stringify(layout));
      if (newLayout[currentBp][id].h > minHt) {
        widgetHeight(newLayout, id, minHt);
        if (chartFilter) chartFilter.hidden = true;
        if (chartContent) chartContent.hidden = true;
      } else {
        widgetHeight(newLayout, id, null);
        if (chartFilter) chartFilter.hidden = false;
        if (chartContent) chartContent.hidden = false;
      }

      if (isMobile && legend) {
        let legendToggle =
          document.getElementById(legend) && document.getElementById(legend).previousElementSibling;
        if (legendToggle && legendToggle.innerText === "Hide Legend") legendToggle.click();
      }
      if (isMobile) {
        for (let i = 0; i < newLayout.xs.length; i++) {
          widgetPosition(newLayout, id, i);
        }
      } else {
        for (let i = 0; i < newLayout.lg.length; i++) {
          widgetPosition(newLayout, id, i);
        }
      }
      setLayout(newLayout);
      saveToLs("exec_layout", newLayout);
    },
    [breakPoints, isMobile, layout, widgetHeight, widgetPosition]
  );

  const syncAllLayouts = (layout, allLayouts) => {
    let breaks;
    if (layout[layout.length - 1].w === 1) breaks = ["xs", "xxs"];
    else breaks = ["lg", "md", "sm"];

    const allLayoutsCopy = { ...allLayouts };

    layout.forEach((x, i) => {
      breaks.forEach((bp) => {
        if (allLayoutsCopy && allLayoutsCopy[bp]) {
          if (allLayoutsCopy[bp][i]) {
            allLayoutsCopy[bp][i].y = x.y;
            allLayoutsCopy[bp][i].x = x.x;
          }
        }
      });
    });
    setLayout(allLayoutsCopy);
  };

  const saveToLs = (key, layout) => {
    window.localStorage.setItem(key, JSON.stringify(layout));
  };

  return (
    <React.Fragment>
      <SizeMe ref={gridRef}>
        {({ size }) => (
          <ResponsiveGridLayout
            className="row layout"
            isDraggable={isEdit}
            isResizable={false}
            layouts={layout}
            rowHeight={100}
            draggableHandle=".drag-handle"
            width={size.width || 0}
            breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 410, xxs: 0 }}
            cols={{ lg: 3, md: 3, sm: 3, xs: 1, xxs: 1 }}
            onLayoutChange={(layout, allLayouts) => {
              syncAllLayouts(layout, allLayouts);
              saveToLs("exec_layout", allLayouts);
            }}
          >
            <div key="a" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <OverviewChartCard
                chartParams={overallChartParams}
                dataReady={dataReady[0]}
                error={errors[0]}
              />
              {isEdit && (
                <div
                  onClick={(e) => minimizeWidget(e, 0)}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
            <div key="b" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <AvgMaintenanceChartCard
                chartParams={avgMaintenanceChartParams}
                dataReady={dataReady[1]}
                error={errors[1]}
                height={isMobile ? "300px" : "350px"}
              />
              {isEdit && (
                <div
                  onClick={(e) => minimizeWidget(e, 1)}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
            <div key="c" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <DowntimeChartCard
                chartParams={downtimeChartParams}
                dataReady={dataReady[2]}
                error={errors[2]}
              />
              {isEdit && (
                <div
                  onClick={(e) => minimizeWidget(e, 2)}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                  style={{paddingLeft:"10px"}}
                />
              )}
            </div>
            <div key="xx" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <CostPerProcess
                costPerProcessParams={costPerProcessParams}
                dataReady={dataReady[9]}
                error={errors[9]}
                height={isMobile ? "350px" : "520px"}
              />
              {isEdit && (
                <div
                  onClick={(e) => minimizeWidget(e, 3)}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
            <div key="d" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <OperationalCostChart
                chartParams={operationalCostParams}
                dataReady={dataReady[8]}
                error={errors[8]}
                height={isMobile ? "260px" : "490px"}
                toggleLegend={toggleLegend}
              />
              {isEdit && (
                <div
                  onClick={(e) => minimizeWidget(e, 4, "operational-cost-chart")}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
            <div key="e" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <StackedClusteredChart
                chartParams={stackedClusteredChart}
                dataReady={dataReady[3]}
                error={errors[3]}
                height={isMobile ? "250px" : "500px"}
                toggleLegend={toggleLegend}
              />
              {isEdit && (
                <div
                  onClick={(e) => minimizeWidget(e, 5, "stack-cluster-chart")}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
            <div key="f" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <AssetMapChartCard
                chartParams={mapChartParams}
                dataReady={dataReady[4]}
                error={errors[4]}
                height={isMobile ? "350px" : "590px"}
              />
              {isEdit && (
                <div
                  onClick={(e) => minimizeWidget(e, 6)}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
            <div key="g" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <AssetUtilChartCard
                assetUtilChartParams={assetUtilChartParams}
                dataReady={dataReady[5]}
                error={errors[5]}
                height={isMobile ? "350px" : "590px"}
              />
              {isEdit && (
                <div
                  onClick={(e) => minimizeWidget(e, 7)}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
            {size && size.width > 768 && (
              <div key="h" className="p-col-12 p-mb-2">
                {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
                <TreeChartCard
                  chartParams={clusterChartParams}
                  dataReady={dataReady[6]}
                  error={errors[6]}
                  height={isMobile ? "370px" : "550px"}
                />
                {isEdit && (
                  <div
                    onClick={(e) => minimizeWidget(e, 8)}
                    className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                  />
                )}
              </div>
            )}
            <div key="i" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <LeaderboardChartCard
                chartParams={leaderboardChartParams}
                dataReady={dataReady[7]}
                error={errors[7]}
                height={isMobile ? "550px" : "400px"}
                width={size.width}
              />
              {isEdit && (
                <div
                  onClick={(e) =>
                    size && size.width <= 768 ? minimizeWidget(e, 8) : minimizeWidget(e, 9)
                  }
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
            <div key="jj" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <VehicleUtilChartCard height={isMobile ? "550px" : "300px"} />
              {isEdit && (
                <div
                  onClick={(e) => (isMobile ? minimizeWidget(e, 9) : minimizeWidget(e, 10))}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
            <div key="kk" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <VehicleCostChartCard height={isMobile ? "550px" : "300px"} />
              {isEdit && (
                <div
                  onClick={(e) => (isMobile ? minimizeWidget(e, 9) : minimizeWidget(e, 10))}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
            <div key="ll" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <MTBFChartCard height={isMobile ? "550px" : "400px"} />
              {isEdit && (
                <div
                  onClick={(e) => (isMobile ? minimizeWidget(e, 9) : minimizeWidget(e, 10))}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
            {/* <div key="jj" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <AccidentChartCard
                assetUtilChartParams={assetUtilChartParams}
                dataReady={dataReady[5]}
                error={errors[5]}
                height={isMobile ? "350px" : "900px"}
              />
              {isEdit && (
                <div
                  onClick={(e) => (isMobile ? minimizeWidget(e, 8) : minimizeWidget(e, 9))}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div> */}
            <div key="mm" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <WorkOrderCompletionTimeCard
                data={workOrderCompletionTimeParams}
                dataReady={dataReady[10]}
                error={errors[10]}
                height={isMobile ? "550px" : "410px"}
              />
              {isEdit && (
                <div
                  onClick={(e) => (isMobile ? minimizeWidget(e, 8) : minimizeWidget(e, 9))}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
          </ResponsiveGridLayout>
        )}
      </SizeMe>
    </React.Fragment>
  );
};

export default ExecutivePanel;
