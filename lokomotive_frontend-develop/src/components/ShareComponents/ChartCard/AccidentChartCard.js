import React from "react";
import { useTranslation } from "react-i18next";
import ChartCard from "../ChartCard/ChartCard";
import AccidentChart from "./AccidentChart";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/AccidentChartCard.scss";

const AccidentChartCard = ({ chartData, dataReady, error, height }) => {
  const { t } = useTranslation();
  return (
    <ChartCard title={"Accident Chart"} tooltipName={"asset_utility"}>
      {dataReady ? (
        error ? (
          <FullWidthSkeleton height={height} error />
        ) : (
          <div id = "chartdiv" className="row no-gutters text-center">
            <AccidentChart
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

export default AccidentChartCard;
