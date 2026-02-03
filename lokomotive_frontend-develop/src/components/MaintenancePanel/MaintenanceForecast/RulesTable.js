import React from "react";
import { useTranslation } from "react-i18next";
import Table from "../../ShareComponents/Table/Table";
import VINLink from "../../ShareComponents/helpers/VINLink";
import GeneralBadge from "../../ShareComponents/GeneralBadge";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/ShareComponents/TabStyles/subTab2.scss";

const RulesTable = ({
  rulesList,
  dataReady,
  setSelectedRule,
  maintenanceTypes,
}) => {
  const { t } = useTranslation();

  const getInspectionTypeName = (id) => {
    return maintenanceTypes.filter((element) => element.id === id)[0].inspection_name;
  };

  //Preparing table data
  let rulesTableHeaders = [
    { header: t("general.vin"), colFilter: { field: "VIN" } },
    {
      header: t("maintenanceForecastPanel.inspection_type"),
      colFilter: { field: "inspection_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("maintenanceForecastPanel.hours_cycle"),
      colFilter: { field: "hour_cycle" },
    },
    {
      header: t("maintenanceForecastPanel.mileage_cycle"),
      colFilter: { field: "mileage_cycle" },
    },
    {
      header: t("maintenanceForecastPanel.time_cycle"),
      colFilter: { field: "time_cycle" },
    },
  ];

  let rulesTableData = rulesList.map((item) => {
      const newItem = Object.assign({}, item);
      newItem.inspection_type = getInspectionTypeName(item.inspection_type);
      return newItem;
    })
    .map((item) => {
      return {
        id: item.id,
        dataPoint: item,
        cells: [
          <VINLink vin={item.VIN} />,
          item.inspection_type,
          ...(item.hour_cycle === -1.0 ? 
                [<GeneralBadge data={t("general.not_applicable")} tooltipContent={t("maintenanceForecastPanel.tooltip_hours_na")} />] 
                : [item.hour_cycle]
              ),
          ...(item.mileage_cycle === -1.0 ? 
                [<GeneralBadge data={t("general.not_applicable")} tooltipContent={t("maintenanceForecastPanel.tooltip_mileage_na")} />] 
                : [item.mileage_cycle]
              ),
          ...(item.time_cycle === -1.0 ? 
                [<GeneralBadge data={t("general.not_applicable")} tooltipContent={t("maintenanceForecastPanel.tooltip_mileage_na")} />] 
                : [item.time_cycle]
              ),
        ],
      };
    });

  return (
    <div className="p-mx-3 p-mt-3 darkTable">
      <Table
        dataReady={dataReady}
        tableHeaders={rulesTableHeaders}
        tableData={rulesTableData}
        hasSelection
        onSelectionChange={(request) => setSelectedRule(request)}
        globalSearch={false}
      />
    </div>
  );
};

export default RulesTable;