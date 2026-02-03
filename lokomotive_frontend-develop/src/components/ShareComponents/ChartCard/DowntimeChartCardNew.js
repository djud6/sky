import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import ChartCard from "./ChartCard";
import SolidGaugeChart from "./SolidGaugeChart";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";
import DatePicker from "../../DatePicker/DateRangePicker";
import axios from "axios";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import ConsoleHelper from "../../../helpers/ConsoleHelper";

const DowntimeChartCard = ({ chartParams, title = "", description = "" }) => {
  const { t } = useTranslation();
  let labels;
  let colors = ["#1A76C4", "#32D500", "#404040"];

  const [innerDetails, setInnerDetails] = useState(null);

  const [startDate, setStartDate] = useState(new Date("2022-01-01"));
  const [endDate, setEndDate] = useState(new Date());
  const [chartData, setChartData] = useState(null);
  const [error, setError] = useState(null);

  const [dataReady, setDataReady] = useState(null);

  const onRangeChanged = (range) => {
    range = range[0];
    if (null !== range.endDate && null !== range.startDate) {
      setStartDate(range.startDate);
      setEndDate(range.endDate);
      setDataReady({});
    }
  };

  const dateRangePicker = dataReady ? (
    <div>
      <DatePicker
        text={"Range"}
        startDate={startDate}
        endDate={endDate}
        onRangeChanged={onRangeChanged}
      />
    </div>
  ) : null;

  function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${month}-${day}-${year}`;
  }

  const getData = () => {
    if (!startDate || !endDate) {
      return;
    }
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Get/AverageDowntime/${formatDate(
          startDate
        )}:${formatDate(endDate)}`,
        {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        }
      )
      .then((response) => {
        setDataReady({});

        const dataTransfer = [];

        const full = 100;

        dataTransfer.push({
          label: "Scheduled Hours",
          data: response.data.percent_preventable,
          full: full,
        });
        dataTransfer.push({
          label: "Unscheduled Hours",
          data: response.data.percent_non_preventable,
          full: full,
        });

        const detailedData = (
          <div>
            <div>
              <p
                className="text-uppercase chart-card-detail drag-handle"
                style={{ display: "inline" }}
              >
                Maintenance Hours: {response.data.maintenance_hours}
              </p>
            </div>
            <div>
              <p
                className="text-uppercase chart-card-detail drag-handle"
                style={{ display: "inline" }}
              >
                Repair Hours: {response.data.repair_hours}
              </p>
            </div>
            <div>
              <p
                className="text-uppercase chart-card-detail drag-handle"
                style={{ display: "inline" }}
              >
                Scheduled Hours: {response.data.preventable_hours}
              </p>
            </div>
            <div>
              <p
                className="text-uppercase chart-card-detail drag-handle"
                style={{ display: "inline" }}
              >
                Unscheduled Hours: {response.data.non_preventable_hours}
              </p>
            </div>
          </div>
        );

        setChartData(dataTransfer);
        setInnerDetails(detailedData);
      })
      .catch((error) => {
        ConsoleHelper(error);
        setError(error);
      });
  };

  useEffect(() => {
    getData();
  }, [startDate, endDate]);

  useEffect(() => {
    if (dataReady && chartData) {
      // eslint-disable-next-line
      labels = chartParams.map((chartParam) => chartParam.label);
    }
  }, [dataReady]);

  return (
    <ChartCard
      title={title.length ? title : t("downTime.fleet_downtime_title")}
      filter={dateRangePicker}
      innerDetails={innerDetails}
      tooltipName={"downtime_fleet"}
    >
      {dataReady ? (
        error ? (
          <FullWidthSkeleton height="350px" error />
        ) : (
          <div className="p-px-2">
            <SolidGaugeChart
              data={chartData}
              innerRadius={35}
              labels={labels}
              colors={colors}
              size={"325px"}
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
