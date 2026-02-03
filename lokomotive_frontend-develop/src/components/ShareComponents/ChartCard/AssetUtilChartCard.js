import React from "react";
import { useTranslation } from "react-i18next";
import ChartCard from "../ChartCard/ChartCard";
import MultipleAxesCard from "./MultipleAxesCard";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";

const AssetUtilChartCard = ({ assetUtilChartParams, dataReady, error, height }) => {
  const { t } = useTranslation();
  return (
    <ChartCard title={t("assetUtilChartCard.title")} tooltipName={"asset_utility"}>
      {dataReady ? (
        error ? (
          <FullWidthSkeleton height={height} error />
        ) : (
          <div className="row no-gutters text-center">
            <MultipleAxesCard
              chartParams={assetUtilChartParams}
              height={height}
              chartName="avg-daily-usage"
            />
          </div>
        )
      ) : (
        <FullWidthSkeleton height={height} />
      )}
    </ChartCard>
  );
};

export default AssetUtilChartCard;
