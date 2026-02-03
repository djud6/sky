import React from "react";
import moment from "moment";
import { useTranslation } from "react-i18next";
import Table from "../../ShareComponents/Table/Table";
import DateBadge from "../../ShareComponents/helpers/DateBadge";
import "../../../styles/ShareComponents/Table/table.scss";

const MaintenanceTable = ({ maintenanceList, dataReady, setSelectedMaintenance }) => {
  const { t } = useTranslation();

  //Preparing table data
  let maintenanceTableHeaders = [
    t("maintenanceLookupPanel.vin_label"),
    t("general.asset_type"),
    t("maintenanceLookupPanel.location_label"),
    t("general.mileage"),
    t("general.hours"),
    t("general.manufacturer"),
    t("general.status"),
    t("general.due_date")
  ];

  let maintenanceTableData = maintenanceList.map((item) => {
    return {
      id: item.VIN,
      dataPoint: item,
      cells: [
        item.VIN,
        item.asset_type || t("general.not_applicable"),
        item.current_location || t("general.not_applicable"),
        item.hours_or_mileage.toLowerCase() === "mileage" ||
        item.hours_or_mileage.toLowerCase() === "both"
          ? item.mileage
          : t("general.not_applicable"),
        item.hours_or_mileage.toLowerCase() === "hours" ||
        item.hours_or_mileage.toLowerCase() === "both"
          ? item.hours
          : t("general.not_applicable"),
        item.manufacturer || t("general.not_applicable"),
        item.status || t("general.not_applicable"),
        <DateBadge
          currentDate={moment(item.maintenance_due_date).format("YYYY-MM-DD")}
          dateRange={2}
          disableGreen
        />
      ],
    };
  });

  return (
    <div className="darkTable">
      <Table
        dataReady={dataReady}
        tableHeaders={maintenanceTableHeaders}
        tableData={maintenanceTableData}
        hasSelection
        multipleSelection
        onSelectionChange={(request) => setSelectedMaintenance(request)}
      />
    </div>
  );
};

export default MaintenanceTable;