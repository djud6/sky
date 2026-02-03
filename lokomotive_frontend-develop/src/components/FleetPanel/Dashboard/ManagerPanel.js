import React, { useState, useEffect } from "react";
import { Responsive as ResponsiveGridLayout } from "react-grid-layout";
import { SizeMe } from "react-sizeme";
import DowntimeChartCard from "../../ShareComponents/ChartCard/DowntimeChartCard";
import StackedClusteredChart from "../../ShareComponents/ChartCard/StackedClusteredChart";
import AssetMapChartCard from "../../ShareComponents/ChartCard/AssetMapChartCard";
import TreeChartCard from "../../ShareComponents/ChartCard/TreeChartCard";
import AssetChecksChart from "../../ShareComponents/ChartCard/AssetChecksChart";
import { isMobileDevice } from "../../../helpers/helperFunctions";

const ManagerPanel = ({
  stackedClusteredChart,
  mapChartParams,
  downtimeChartParams,
  clusterChartParams,
  assetCheckParams,
  dataReady,
  errors,
  dashboard_layout,
  isEdit,
}) => {
  const isMobile = isMobileDevice();
  const smallWidgetHt = 4.5;
  const largeWidgetHt = 6.5;
  const mediumWidgetHt = 6;
  const minHt = 1;

  const defaultLayout = {
    lg: [
      { i: "a", x: 0, y: 0, w: 3, h: largeWidgetHt },
      { i: "b", x: 0, y: 1.4, w: 3, h: largeWidgetHt },
      { i: "c", x: 0, y: 2.8, w: 3, h: smallWidgetHt },
      { i: "d", x: 0, y: 3.8, w: 3, h: largeWidgetHt },
      { i: "e", x: 0, y: 5.2, w: 3, h: largeWidgetHt },
    ],
    md: [
      { i: "a", x: 0, y: 0, w: 3, h: largeWidgetHt },
      { i: "b", x: 0, y: 1.4, w: 3, h: largeWidgetHt },
      { i: "c", x: 0, y: 2.8, w: 3, h: smallWidgetHt },
      { i: "d", x: 0, y: 3.8, w: 3, h: largeWidgetHt },
      { i: "e", x: 0, y: 5.2, w: 3, h: largeWidgetHt },
    ],
    sm: [
      { i: "a", x: 0, y: 0, w: 3, h: largeWidgetHt },
      { i: "b", x: 0, y: 1.4, w: 3, h: largeWidgetHt },
      { i: "c", x: 0, y: 2.8, w: 3, h: smallWidgetHt },
      { i: "d", x: 0, y: 3.8, w: 3, h: largeWidgetHt },
      { i: "e", x: 0, y: 5.2, w: 3, h: largeWidgetHt },
    ],
    xs: [
      { i: "a", x: 0, y: 0, w: 1, h: smallWidgetHt },
      { i: "b", x: 0, y: 1.4, w: 1, h: smallWidgetHt },
      { i: "c", x: 0, y: 2.8, w: 1, h: smallWidgetHt },
      { i: "e", x: 0, y: 5.2, w: 1, h: mediumWidgetHt },
    ],
    xxs: [
      { i: "a", x: 0, y: 0, w: 1, h: smallWidgetHt },
      { i: "b", x: 0, y: 1.4, w: 1, h: smallWidgetHt },
      { i: "c", x: 0, y: 2.8, w: 1, h: smallWidgetHt },
      { i: "e", x: 0, y: 5.2, w: 1, h: mediumWidgetHt },
    ],
  };

  useEffect(() => {
    if (dashboard_layout) {
      setLayout(dashboard_layout);
      saveToLs("mngr_layout", dashboard_layout);
    }
  }, [dashboard_layout]);

  const initialLayout = JSON.parse(window.localStorage.getItem("mngr_layout")) || defaultLayout;

  const [layout, setLayout] = useState(initialLayout);

  let breakPoints;
  if (isMobile) breakPoints = ["xs", "xxs"];
  else breakPoints = ["lg", "md", "sm"];

  const widgetHeight = (layout, id, height) => {
    breakPoints.forEach((bp) => {
      if (height) {
        layout[bp][id].h = height;
      } else {
        layout[bp][id].h = defaultLayout[bp][id].h;
      }
    });
  };

  const widgetPosition = (layout, id, i) => {
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
  };

  const toggleLegend = (chartId) => {
    const newLayout = JSON.parse(JSON.stringify(layout));
    let id = chartId === "operational-cost-chart" ? 3 : 0;
    if (newLayout.xxs[id].h === smallWidgetHt) {
      newLayout.xs[id].h = largeWidgetHt - 0.5;
      newLayout.xxs[id].h = largeWidgetHt - 0.5;
    } else {
      newLayout.xs[id].h = smallWidgetHt;
      newLayout.xxs[id].h = smallWidgetHt;
    }
    setLayout(newLayout);
  };

  const minimizeWidget = (e, id, legend = null) => {
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
      let legendToggle = document.getElementById(legend).previousElementSibling;
      if (legendToggle.innerText === "Hide Legend") legendToggle.click();
    }

    for (let i = 0; i < newLayout.lg.length; i++) {
      widgetPosition(newLayout, id, i);
    }
    setLayout(newLayout);
    saveToLs("mngr_layout", newLayout);
  };

  const syncAllLayouts = (layout, allLayouts) => {
    let breaks;
    if (layout[layout.length - 1].w === 1) breaks = ["xs", "xxs"];
    else breaks = ["lg", "md", "sm"];

    layout.forEach((x, i) => {
      breaks.forEach((bp) => {
        if (allLayouts && allLayouts[bp]) {
          if (allLayouts[bp][i]) {
            allLayouts[bp][i].y = x.y;
            allLayouts[bp][i].x = x.x;
          }
        }
      });
    });
    setLayout(allLayouts);
  };

  const saveToLs = (key, layout) => {
    window.localStorage.setItem(key, JSON.stringify(layout));
  };

  return (
    <React.Fragment>
      <SizeMe>
        {({ size }) => (
          <ResponsiveGridLayout
            className="row layout manager-grid-layout"
            isDraggable={isEdit}
            isResizable={false}
            layouts={layout}
            rowHeight={100}
            width={size.width || 0}
            draggableHandle=".drag-handle"
            breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
            cols={{ lg: 3, md: 3, sm: 3, xs: 1, xxs: 1 }}
            onLayoutChange={(layout, allLayouts) => {
              syncAllLayouts(layout, allLayouts);
              saveToLs("mngr_layout", allLayouts);
            }}
          >
            <div key="a" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <StackedClusteredChart
                chartParams={stackedClusteredChart}
                dataReady={dataReady[0]}
                error={errors[0]}
                height={isMobile ? "250px" : "500px"}
                toggleLegend={toggleLegend}
                loc="manager"
              />
              {isEdit && (
                <div
                  onClick={(e) => minimizeWidget(e, 0, "stack-cluster-chartmanager")}
                  className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                />
              )}
            </div>
            <div key="b" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <AssetMapChartCard
                chartParams={mapChartParams}
                dataReady={dataReady[1]}
                error={errors[1]}
                height={isMobile ? "350px" : "550px"}
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
                />
              )}
            </div>
            {!isMobile && (
              <div key="d" className="p-col-12 p-mb-2">
                {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
                <TreeChartCard
                  chartParams={clusterChartParams}
                  dataReady={dataReady[3]}
                  error={errors[3]}
                  height={isMobile ? "370px" : "550px"}
                />
                {isEdit && (
                  <div
                    onClick={(e) => minimizeWidget(e, 3)}
                    className="pi pi-window-minimize text-white position-absolute toggle-widget m-1"
                  />
                )}
              </div>
            )}
            <div key="e" className="p-col-12 p-mb-2">
              {isEdit && <div className="position-absolute drag-chart-handle drag-handle" />}
              <AssetChecksChart
                chartParams={assetCheckParams}
                dataReady={dataReady[4]}
                error={errors[4]}
              />
              {isEdit && (
                <div
                  onClick={(e) => (isMobile ? minimizeWidget(e, 3) : minimizeWidget(e, 4))}
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

export default ManagerPanel;
