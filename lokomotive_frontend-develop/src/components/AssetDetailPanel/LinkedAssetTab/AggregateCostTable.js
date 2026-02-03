import React from "react";
import { useTranslation } from "react-i18next";
import { capitalize } from "../../../helpers/helperFunctions";
import Table from "../../ShareComponents/Table/Table";
import "../../../styles/ShareComponents/Table/table2.scss";

const AggregateCostTable = ({ costData, width, isMobileTable }) => {
  const { t } = useTranslation();

  let tableData = [];

  const formatCostData = (costData, role = "child") => {
    return {
      VIN: costData[`${role}_VIN`],
      role,
      total_cost: costData[`${role === "parent" ? role + "_" : ""}total_cost`],
      fuel_cost: costData.fuel_cost?.total_cost.toFixed(2),
      license_cost: costData.license_cost?.total_cost.toFixed(2),
      insurance_cost: costData.insurance_cost?.total_cost.toFixed(2),
      acquisition_cost: costData.acquisition_cost?.total_cost.toFixed(2),
      rental_cost: costData.rental_cost?.total_cost.toFixed(2),
      labor_cost: costData.labor_cost?.total_cost.toFixed(2),
      parts_cost: costData.parts_cost?.total_cost.toFixed(2),
      delivery_cost: costData.delivery_cost?.total_cost.toFixed(2),
    };
  };

  if (costData) {
    const parentCost = formatCostData(costData, "parent");
    const childrenCost = costData.children?.map((child) => formatCostData(child));
    tableData = [parentCost, ...childrenCost];
  }

  const tableHeaders = [
    t("general.vin"),
    t("general.role"),
    t("costsTab.fuel_submit_label"),
    t("costsTab.license_submit_label"),
    t("costsTab.insurance_submit_label"),
    t("costsTab.acquisition_submit_label"),
    t("costsTab.rental_submit_label"),
    t("laborCost.labor_title"),
    t("partsCost.parts_title"),
    t("costsTab.delivery_cost"),
  ];

  const tableValue = tableData.map((item) => {
    return {
      id: item.VIN,
      dataPoint: item,
      cells: [
        item.VIN,
        capitalize(item.role),
        item.fuel_cost,
        item.license_cost,
        item.insurance_cost,
        item.acquisition_cost,
        item.rental_cost,
        item.labor_cost,
        item.parts_cost,
        item.delivery_cost,
      ],
    };
  });

  return (
    <div className={`darkTable2 darkTable2${isMobileTable ? "-mobile" : ""}`}>
      <Table
        dataReady
        tableHeaders={tableHeaders}
        tableData={tableValue}
        globalSearch={false}
        disableMobileDetail
      />
    </div>
  );
};

export default AggregateCostTable;
