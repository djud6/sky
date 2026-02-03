import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import ChartCard from "./ChartCard";
import LeaderboardChart from "./LeaderboardChart";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";

const LeaderboardChartCard = ({ chartParams, dataReady, error, height, width }) => {
  const { t } = useTranslation();
  const [parsedParams, setParsedParams] = useState(null);
  const [selectedChartParams, setSelectedChartParams] = useState(null);
  const [defaultAsset, setDefaultAsset] = useState(null);

  useEffect(() => {
    if (dataReady) {
      setParsedParams(null);
      if (chartParams[0]) {
        setSelectedChartParams(Object.keys(chartParams[0])[0]);
        setDefaultAsset({
          name: Object.keys(chartParams[0])[0],
          code: Object.keys(chartParams[0])[0],
        });
      }
    }
    //  eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataReady]);

  useEffect(() => {
    if (selectedChartParams) {
      const filteredChartParams = chartParams.filter(
        (asset) => Object.keys(asset)[0] === selectedChartParams
      );
      // eslint-disable-next-line
      const parsedChartParams = filteredChartParams[0][Object.keys(filteredChartParams[0])];
      setParsedParams(parsedChartParams);
    }
    //  eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedChartParams]);

  const onPointerChange = (selected) => {
    setSelectedChartParams(selected);
  };

  const assetTypeFilter = dataReady ? (
    <FormDropdown
      className="w-100"
      defaultValue={defaultAsset}
      onChange={onPointerChange}
      options={
        chartParams &&
        chartParams.map((asset) => ({
          name: Object.keys(asset)[0],
          code: Object.keys(asset)[0],
        }))
      }
      loading={!dataReady}
      disabled={!dataReady}
      dataReady={dataReady}
      plain_dropdown
    />
  ) : null;

  return (
    <div className="chartcard-dropdown h-100">
      <ChartCard
        title={t("leaderboardChartCard.title")}
        filter={assetTypeFilter}
        tooltipName={"leader_board"}
      >
        {dataReady ? (
          error ? (
            <FullWidthSkeleton height={height} error />
          ) : (
            parsedParams && <LeaderboardChart chartParams={parsedParams} width={width} />
          )
        ) : (
          <FullWidthSkeleton height={height} />
        )}
      </ChartCard>
    </div>
  );
};

export default LeaderboardChartCard;
