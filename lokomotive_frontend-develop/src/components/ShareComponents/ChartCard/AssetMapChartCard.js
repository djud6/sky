import React from "react";
import { useTranslation } from "react-i18next";

import ChartCard from "./ChartCard";
import MapChart from "./MapChart";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";

const AssetMapChartCard = ({ chartParams, dataReady, error, height }) => {
  const { t } = useTranslation();
  return (
    <ChartCard title={t("assetMapChartCard.title")} tooltipName={"asset_map"}>
      {dataReady ? (
        error ? (
          <FullWidthSkeleton height={height} error />
        ) : (
          <div className="row no-gutters">
            <MapChart datasets={chartParams} height={height} />
          </div>
        )
      ) : (
        <FullWidthSkeleton height={height} />
      )}
    </ChartCard>
  );
};

export default AssetMapChartCard;
