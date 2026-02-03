import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import ChartCard from "../ChartCard/ChartCard";
import PictorialSliceCard from "./PictorialSliceCard";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import FullWidthSkeleton from "../CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";

const FuelUsageVolume = ({ locations, chartParams, dataReady, error, height }) => {
  const { t } = useTranslation();
  const [selectedFuelType, setSelectedFuelType] = useState(!error && {
    name:
      Object.keys(chartParams)[0].charAt(0).toUpperCase() + Object.keys(chartParams)[0].slice(1),
    code: Object.keys(chartParams)[0],
  });
  const [selectedLocation, setSelectedLocation] = useState(locations[0]);
  const [totalUsage, setTotalUsage] = useState(0);
  const fuelTypes = [];
  Object.keys(chartParams).forEach((fuelType) => {
    fuelTypes.push({ name: fuelType.charAt(0).toUpperCase() + fuelType.slice(1), code: fuelType });
  });

  useEffect(() => {
    if (!error) {
      let locationParams;
      let seletedLocData;
      let tempTotal = 0;
      locationParams = chartParams[selectedFuelType.code];
      seletedLocData = locationParams.find((loc) => Object.keys(loc)[0] === selectedLocation.name);
      seletedLocData[selectedLocation.name].forEach((value) => {
        if (value[1]["liters:"]) {
          tempTotal = tempTotal + value[1]["liters:"];
        }
      });
      setTotalUsage(tempTotal);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedFuelType, selectedLocation]);

  const selectFuelType = (id) => {
    let selected = fuelTypes.find((type) => type.code === id);
    setSelectedFuelType(selected);
  };

  const selectLocation = (id) => {
    let selected = locations.find((location) => location.code === parseInt(id));
    setSelectedLocation(selected);
  };

  const Filter = (
    <div className="chartcard-dropdown mr-4 p-d-flex p-flex-wrap p-jc-end">
      <div>
        <FormDropdown
          defaultValue={selectedFuelType}
          onChange={selectFuelType}
          options={fuelTypes}
          plain_dropdown
          placeholder="Fuel"
          reset="disabled"
          dataReady
        />
      </div>
      <div className="p-ml-3">
        <FormDropdown
          defaultValue={selectedLocation}
          onChange={selectLocation}
          options={locations}
          plain_dropdown
          placeholder="Location"
          reset="disabled"
          dataReady
        />
      </div>
    </div>
  );

  return (
    <ChartCard
      title={t("fuelUsageVolumeChartCard.title")}
      description={t("fuelUsageVolumeChartCard.description")}
    >
      {dataReady ? 
        error ? (
          <FullWidthSkeleton height={height} error />
        ) : (
          <React.Fragment>
            {Filter}
            <div>
              <PictorialSliceCard usage={totalUsage} height={height} />
            </div>
          </React.Fragment>
        )
        :
        <FullWidthSkeleton height={height} />
      }
    </ChartCard>
  );
};

export default FuelUsageVolume;
