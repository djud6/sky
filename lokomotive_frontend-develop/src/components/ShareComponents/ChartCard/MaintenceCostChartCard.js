import React from "react";
import { useTranslation } from "react-i18next";
import ChartCard from "../ChartCard/ChartCard";
import MaintenceCostChart from "./MaintenceCostChart";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/MaintenChartCard.scss";

const MaintenceCostChartCard = ({ assetUtilChartParams, dataReady, error, height }) => {
  const { t } = useTranslation();
  return (
    <ChartCard title={"Maintenance Cost per Mile"} 
    // tooltipName={"asset_utility"}
    >
      {dataReady ? (
        error ? (
          <FullWidthSkeleton height={height} error />
        ) : (
          <div id = "maintenchartdiv" className="row no-gutters text-center">
            <MaintenceCostChart
              data={dataReady}
              size={height}
            />
          </div>
        )
      ) : (
        <FullWidthSkeleton height={height} />
      )}
    </ChartCard>
  );
};

export default MaintenceCostChartCard;
