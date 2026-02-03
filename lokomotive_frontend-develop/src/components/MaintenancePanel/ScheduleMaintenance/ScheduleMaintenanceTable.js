import React from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import Table from "../../ShareComponents/Table/Table";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import VINLink from "../../ShareComponents/helpers/VINLink";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/MaintenancePanel/scheduleMaintenance.scss";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";

const ScheduleMaintenanceTable = ({
  selectedVehicles,
  maintenanceTypes,
  maintenanceType,
  setSelectedVehicles,
  resetAll,
  setVehicle,
}) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  //Preparing table data
  let maintenanceTableHeaders = [
    t("maintenanceSchedulePanel.vin_label"),
    t("maintenanceSchedulePanel.maintenance_type_label"),
    t("maintenanceSchedulePanel.location_label"),
  ];

  let maintenanceTableData = selectedVehicles.map((vehicle) => {
    return {
      id: vehicle.VIN,
      dataPoint: vehicle,
      cells: [
        <div key={vehicle.VIN} className="p-d-flex p-ai-center p-flex-wrap vin-cell">
          <div className = "button-box">
           <Button
            icon="pi pi-times-circle"
            className="p-button-rounded p-button-danger p-button-text p-mr-2"
            onClick={() => {
              let filtered = selectedVehicles.filter((item) => item.VIN !== vehicle.VIN);
              filtered.length === 0 ? resetAll() : setSelectedVehicles(filtered);
            }}

            tooltip="click to remove this asset from schedule maintenance"
            tooltipOptions={{position: 'bottom'}}
               />
            </div>
          <VINLink vin={vehicle.VIN} />

        </div>,
        maintenanceType
          ? maintenanceTypes.filter((element) => element.id === maintenanceType)[0].inspection_name
          : t("general.not_applicable"),
        vehicle.current_location,
      ],
    };
  });

  return (
    <React.Fragment>
      <div className={`${isMobile ? "p-pb-4" : "p-mt-5"}`}>
        <VINSearch
          labelText={t("maintenanceSchedulePanel.add_new_asset")}
          onVehicleSelected={(v) => {
            if (!Array.isArray(v) && v != null) {
              if (!selectedVehicles.some((el) => el.VIN === v.VIN)) {
                setSelectedVehicles([...selectedVehicles, v]);
              }
            }
            setVehicle(v);
          }}
          key={JSON.stringify(selectedVehicles)}
        />
      </div>
      <div className={`p-mx-3 darkTable ${isMobile ? "p-mt-5" : ""}`}>
        <Table
          dataReady
          tableHeaders={maintenanceTableHeaders}
          tableData={maintenanceTableData}
          rows={isMobile ? 2 : 5}
          globalSearch={false}
        />
      </div>
    </React.Fragment>
  );
};

export default ScheduleMaintenanceTable;
