import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import avgBackground from "./avg-maintenance-img.png";
import ChartCard from "./ChartCard";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";
import "../../../styles/ShareComponents/ChartCard/AvgMaintenanceChartCard.scss";

const AvgMaintennaceCostChartCard = ({ chartParams, dataReady, error, height }) => {
  const { t } = useTranslation();
  const [avgMaintenanceCost, setAvgMaintenanceCost] = useState("0");

  useEffect(() => {
    if (dataReady && chartParams) {
      let cost = Object.values(chartParams)[2];
      setAvgMaintenanceCost(Math.round(cost * 100) / 100);
    }
    // eslint-disable-next-line
  }, [dataReady]);

  return (
    <div className="h-100 avg-m-card chartcard-dropdown">
      <ChartCard
        title={"Average Maintenance Cost Per Vehicle"}
        // tooltipName={"average_maintenance_cost_per_vehicle"}
      >
        {dataReady ? (
          error ? (
            <FullWidthSkeleton height={height} error />
          ) : (
            <div className="p-d-flex p-flex-column">
              <div className="p-px-5 p-mt-3 avg-m-chart" style={{ height: height }}>
                <img className="mw-100 mh-100" alt="avg_maintenance_ing" src={avgBackground} />
                <p className="avg-m-text">
                  ${avgMaintenanceCost}
                </p>
              </div>
            </div>
          )
        ) : (
          <FullWidthSkeleton height={height} />
        )}
      </ChartCard>
    </div>
  );
};

export default AvgMaintennaceCostChartCard;
