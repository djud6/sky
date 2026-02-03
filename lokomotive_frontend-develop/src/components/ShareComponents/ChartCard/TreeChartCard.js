import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import TreeChart from "./TreeChart";
import ChartCard from "./ChartCard";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";

const TreeChartCard = ({ chartParams, maxLocations = 5, dataReady, error, height }) => {
  const { t } = useTranslation();
  const [parsedParams, setParsedParams] = useState(null);
  // Parsing data to pass to the tree chart:

  useEffect(() => {
    if (dataReady) {
      setParsedParams(null);
      // eslint-disable-next-line
      const parsedChartParams = chartParams.map((item) => {
        return {
          name: Object.keys(item)[0],
          label: Object.keys(item)[0],
          fixed: true,
          children: item[Object.keys(item)[0]].map((asset) => {
            return {
              name: asset[0],
              value: asset[1],
              label: asset[1],
            };
          }),
        };
      });
      setParsedParams(parsedChartParams);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataReady]);

  return (
    <ChartCard
      title={t("treeChartCard.title", { maxLocations })}
      tooltipName={"live_asset_type_cluster"}
    >
      {dataReady ? (
        error ? (
          <FullWidthSkeleton height={height} error />
        ) : (
          parsedParams && (
            <div className="row no-gutters text-center">
              <TreeChart chartParams={parsedParams.slice(0, maxLocations)} height={height} />
            </div>
          )
        )
      ) : (
        <FullWidthSkeleton height={height} />
      )}
    </ChartCard>
  );
};

export default TreeChartCard;
