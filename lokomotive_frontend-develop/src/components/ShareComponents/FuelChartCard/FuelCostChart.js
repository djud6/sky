import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import ChartCard from "../ChartCard/ChartCard";
import MultipleValueAxesCard from "./MultipleValueAxesCard";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import FullWidthSkeleton from "../CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";

const FuelCostChart = ({ chartParams = null, dataReady, height, error }) => {
  const { t } = useTranslation();
  let [selectedPeriod, setSelectedPeriod] = useState(Object.keys(chartParams)[0]);
  let [fuelCostParams, setFuelCostParams] = useState([]);
  let [selectedLocation, setSelectedLocation] = useState(!error && {
    name: Object.keys(chartParams[selectedPeriod][0])[0],
    code: Object.keys(chartParams[selectedPeriod][0])[0],
  });

  const timePeriodTitles = {
    daily: "DAILY",
    weekly: "WEEKLY",
    monthly: "MONTHLY",
  };

  const onDatePeriodChange = (item) => {
    let i = chartParams[item].findIndex((x) => Object.keys(x)[0] === selectedLocation.name);
    setSelectedPeriod(item);
    setSelectedLocation({
      name: Object.keys(chartParams[item][i])[0],
      code: Object.keys(chartParams[item][i])[0],
    });
  };

  useEffect(() => {
    if (chartParams && !error) setSelectedPeriod(Object.keys(chartParams)[0]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chartParams]);

  useEffect(() => {
    if (chartParams && !error) {
      const selectedParams = chartParams[selectedPeriod].find((item) => {
        return Object.keys(item)[0] === selectedLocation.name;
      });
  
      const parsedChartParams = selectedParams[selectedLocation.name].map((item) => {
        return {
          ...(item.date ? { date: new Date(item.date) } : { date: new Date(item.start_date) }),
          label: `Percentage Change: [bold]${item.percentage_change}%[/]`,
          fuel_cost: item.fuel_cost,
          // projected_cost:  item.fuel_cost + Math.round(item.fuel_cost*Math.random()*10)
        };
      });
  
      setFuelCostParams(parsedChartParams);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedLocation]);

  const onLocationChange = (selected) => {
    setSelectedLocation({
      name: selected,
      code: selected,
    });
  };

  const locationFilter = (
    <div className="p-d-flex p-flex-column p-flex-md-row p-ai-center p-flex-wrap">
      <h5 className="text-white font-weight-bold p-text-nowrap p-mr-2">{t("fuelCostChartCard.time_period")}:</h5>
      <div className="p-d-flex p-ai-center p-flex-wrap p-mb-2">
        {Object.keys(chartParams).map((item) => {
          return (
            <Button
              key={item}
              label={timePeriodTitles[item]}
              onClick={() => {
                onDatePeriodChange(item);
              }}
              className={`p-button-text p-text-bold ${selectedPeriod === item || "p-button-plain"}`}
            />
          );
        })}
      </div>
      <div className="chartcard-dropdown w-100 p-pr-3">
        <FormDropdown
          className="w-100"
          defaultValue={selectedLocation}
          onChange={onLocationChange}
          options={chartParams[selectedPeriod] && 
            chartParams[selectedPeriod].map((item) => ({
            name: Object.keys(item)[0],
            code: Object.keys(item)[0],
          }))}
          plain_dropdown
          placeholder="Location"
          disabled={!chartParams[selectedPeriod]}
          reset="disabled"
          dataReady={!!chartParams}
        />
      </div>
    </div>
  );

  return (
    <ChartCard
      title={t("fuelCostChartCard.title")}
      description={t("fuelCostChartCard.description")}
      filter={!error && locationFilter}
    >
      {dataReady ? 
        error ? (
          <FullWidthSkeleton height={height} error />
        ) : (
          <div className="row no-gutters text-center">
            <MultipleValueAxesCard
              chartParams={fuelCostParams}
              height={height}
            />
          </div>
        )
        :
        <FullWidthSkeleton height={height} />
      }
    </ChartCard>
  );
};

export default FuelCostChart;
