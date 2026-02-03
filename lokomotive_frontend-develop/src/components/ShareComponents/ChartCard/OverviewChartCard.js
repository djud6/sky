import React, { useEffect } from "react";
import { useTranslation } from "react-i18next";
import ChartCard from "./ChartCard";
import SolidGaugeChart from "./SolidGaugeChart";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";

const OverviewChartCard = ({ chartParams, dataReady, error }) => {
  const { t } = useTranslation();
  let labels;
  let colors = ["#32D500", "#FD291C", "#FD7A22", "#1A76C4", "#404040"];

  useEffect(() => {
    if (dataReady) {
      // eslint-disable-next-line
      labels = chartParams.map((chartParam) => chartParam.label);
    }
  }, [dataReady]);

  return (
    <ChartCard
      title={t("overviewChartCard.overall_asset_breakdown")}
      tooltipName={"overall_asset_breakdown"}
    >
      {dataReady ? (
        error ? (
          <FullWidthSkeleton height="350px" error />
        ) : (
          <div className="p-px-2">
            <SolidGaugeChart
              data={chartParams}
              innerRadius={10}
              labels={labels}
              colors={colors}
              size={"350px"}
              legend={false}
              fontSize={11.5}
              isMobile
            />
          </div>
        )
      ) : (
        <FullWidthSkeleton height="350px" />
      )}
    </ChartCard>
  );
};

export default OverviewChartCard;
