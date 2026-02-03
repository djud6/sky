import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import avgBackground from "./avg-maintenance-img.png";
import ChartCard from "./ChartCard";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";
import "../../../styles/ShareComponents/ChartCard/AvgMaintenanceChartCard.scss";

const AvgMaintenanceChartCard = ({ chartParams, dataReady, error, height }) => {
  const { t } = useTranslation();
  const [defaultLocation, setDefaultLocation] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [selectedDowntime, setSelectedDowntime] = useState("0");

  useEffect(() => {
    if (dataReady && chartParams[0]) {
      setDefaultLocation({
        name: Object.keys(chartParams[0])[0],
        code: Object.keys(chartParams[0])[0],
      });
      setSelectedLocation(Object.keys(chartParams[0])[0]);
    }
    // eslint-disable-next-line
  }, [dataReady]);

  useEffect(() => {
    if (selectedLocation) {
      let locationDowntime = chartParams.find(
        (location) => Object.keys(location)[0] === selectedLocation
      );
      setSelectedDowntime(locationDowntime[selectedLocation].toFixed(2));
    }
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedLocation]);

  const onLocationChange = (selected) => {
    setSelectedLocation(selected);
  };

  const locationFilter = dataReady ? (
    <div className="w-50">
      <FormDropdown
        defaultValue={defaultLocation}
        className="w-100"
        onChange={onLocationChange}
        options={
          chartParams &&
          chartParams.map((location) => ({
            name: Object.keys(location)[0],
            code: Object.keys(location)[0],
          }))
        }
        loading={!dataReady}
        disabled={!dataReady}
        dataReady={dataReady}
        plain_dropdown
      />
    </div>
  ) : null;

  return (
    <div className="h-100 avg-m-card chartcard-dropdown">
      <ChartCard
        title={"Average Maintenance Downtime"}
        tooltipName={"average_maintenance_downtime"}
      >
        {dataReady ? (
          error ? (
            <FullWidthSkeleton height={height} error />
          ) : (
            <div className="p-d-flex p-flex-column">
              <div className="p-d-flex p-jc-end p-mr-3">
                {locationFilter}
              </div>
              <div className="p-px-5 p-mt-3 avg-m-chart" style={{ height: height }}>
                <img className="mw-100 mh-100" alt="avg_maintenance_ing" src={avgBackground} />
                <p className="avg-m-text">
                  {selectedDowntime}
                  <br />
                  {t("general.hours")}
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

export default AvgMaintenanceChartCard;
