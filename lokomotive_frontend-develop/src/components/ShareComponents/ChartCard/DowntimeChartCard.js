import React, { useEffect } from "react";
import { useTranslation } from "react-i18next";
import ChartCard from "./ChartCard";
import SolidGaugeChart from "./SolidGaugeChart";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";

const DowntimeChartCard = ({ chartParams, title = "", description = "", dataReady, error }) => {
  const { t } = useTranslation();
  let labels;
  let colors = ["#1A76C4", "#32D500", "#404040"];

  useEffect(() => {
    if (dataReady && chartParams) {
      // eslint-disable-next-line
      labels = chartParams.map((chartParam) => chartParam.label);
    }
  }, [dataReady]);

  return (
    <ChartCard
      title={title.length ? title : t("downTime.fleet_downtime_title")}
      tooltipName={"downtime_fleet"}
      moreSpace={'true'}
    >
      {dataReady ? (
        error ? (
          <FullWidthSkeleton height="350px" error />
        ) : (
          <div className="p-px-2">
            <SolidGaugeChart
              data={chartParams}
              innerRadius={35}
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

export default DowntimeChartCard;
