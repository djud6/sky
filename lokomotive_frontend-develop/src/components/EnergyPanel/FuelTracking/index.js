import React from "react";
import { useSelector } from "react-redux";
import { useRequestedData } from "../../../hooks/dataDetcher";
import { faBolt } from "@fortawesome/free-solid-svg-icons";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import FuelTrackingSkeleton from "../../ShareComponents/CustomSkeleton/FuelTrackingSkeleton";
import FuelUsageVolume from "../../ShareComponents/FuelChartCard/FuelUsageVolume";
import FuelCostChart from "../../ShareComponents/FuelChartCard/FuelCostChart";
import { isMobileDevice } from "../../../helpers/helperFunctions";
import ConsoleHelper from "../../../helpers/ConsoleHelper";

const FuelTrackingPanel = () => {
  const isMobile = isMobileDevice();
  const { listLocations } = useSelector((state) => state.apiCallData);
  const locations = listLocations.map((loc) => ({ name: loc.location_name, code: loc.location_id }));
  const urlArray = [
    "api/v1/Chart/Get/Fuel/Cost/daily",
    "api/v1/Chart/Get/Fuel/Cost/weekly",
    "api/v1/Chart/Get/Fuel/Cost/monthly",
  ];

  const [
    dataReady,
    dataArray1,
    errors,
  ] = useRequestedData("api/v1/Chart/Get/Fuel/Volume");

  const [
    dataReady1,
    dataArray2,
    dataArray3,
    dataArray4,
    errors1,
  ] = useRequestedData(urlArray);

  let fuelVolumeParams = {};
  let fuelCostChartParams;

  if (dataReady) {
    if (errors) {
      ConsoleHelper("errors:", errors);
    }

    dataArray1 && dataArray1.forEach((location) => {
      fuelVolumeParams[Object.keys(location)[0]] = location[Object.keys(location)[0]];
    });

    fuelCostChartParams = {
      daily: dataArray2,
      weekly: dataArray3,
      monthly: dataArray4
    };
  }

  return (
    <div>
      {isMobile &&
        <QuickAccessTabs
          tabs={["Fuel Tracking", "Transaction", "Order History", "Fuel Cards"]}
          activeTab={"Fuel Tracking"}
          urls={["/energy", "/energy/fuel-transaction", "/energy/energy-orders", "/energy/fuel-cards"]}
        />
      }
      <PanelHeader text="Fuel Tracking" icon={faBolt} />
      {!isMobile &&
        <QuickAccessTabs
          tabs={["Fuel Tracking", "Transaction", "Order History", "Fuel Cards"]}
          activeTab={"Fuel Tracking"}
          urls={["/energy", "/energy/fuel-transaction", "/energy/energy-orders", "/energy/fuel-cards"]}
        />
      }
      {dataReady && dataReady1 && locations.length !== 0 && fuelVolumeParams ? (
        <div className="row">
          <div className="p-col-12 p-d-flex p-flex-wrap">
            <div className="p-col-12 p-sm-12 p-md-12 p-lg-12 p-xl-3">
              <FuelUsageVolume
                locations={locations}
                chartParams={fuelVolumeParams}
                dataReady={dataReady}
                error={errors}
                height={isMobile ? "320px" : "550px"}
              />
            </div>
            <div className="p-col-12 p-sm-12 p-md-12 p-lg-12 p-xl-9">
              <FuelCostChart
                chartParams={fuelCostChartParams}
                dataReady={dataReady1}
                height={isMobile ? "380px" : "550px"}
                error={errors1}
              />
            </div>
          </div>
        </div>
      ) : (
        <FuelTrackingSkeleton />
      )}
    </div>
  );
};

export default FuelTrackingPanel;