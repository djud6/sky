import React from "react";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { capitalize } from "../../../helpers/helperFunctions";
import { Table } from "../../ShareComponents/Table";
import InventoryDetails from "./InventoryDetails";

const InventoryPanel = ({
  inventory,
  dataReady,
  setInventory,
  selectedInventory,
  setSelectedInventory,
}) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  if (!inventory) return null;

  let TableHeaders = [
    { header: t("inventoryPanelIndex.inventory_type"), colFilter: { field: "inventory_type" } },
    { header: t("inventoryPanelIndex.description"), colFilter: { field: "description" } },
    {
      header: t("inventoryPanelIndex.location"),
      colFilter: { field: "location", filterOptions: { filterAs: "dropdown" } },
    },
    { header: t("inventoryPanelIndex.per_unit_cost"), colFilter: { field: "per_unit_cost" } },
    {
      header: t("inventoryPanelIndex.date_of_manufacture"),
      colFilter: {
        field: "date_of_manufacture",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
  ];

  let TableData = inventory.map((item) => {
    return {
      id: item.id,
      dataPoint: item,
      cells: [
        capitalize(item.inventory_type) || [t("general.not_applicable")],
        item.description || [t("general.not_applicable")],
        item.location || [t("general.not_applicable")],
        item.per_unit_cost ? item.per_unit_cost.toFixed(2) : [t("general.not_applicable")],
        ...(moment(item.date_of_manufacture).isValid()
          ? [moment(item.date_of_manufacture).format("YYYY-MM-DD")]
          : [t("general.not_applicable")]),
      ],
    };
  });

  return (
    <React.Fragment>
      {isMobile ? (
        <React.Fragment>
          {selectedInventory ? (
            <div className="p-mb-5">
              <InventoryDetails
                inventory={selectedInventory}
                setInventory={setInventory}
                setSelectedInventory={setSelectedInventory}
              />
            </div>
          ) : (
            <div className="p-mb-5">
              <Table
                dataReady={dataReady}
                tableHeaders={TableHeaders}
                tableData={TableData}
                onSelectionChange={(item) => setSelectedInventory(item)}
                hasSelection
              />
            </div>
          )}
        </React.Fragment>
      ) : (
        <React.Fragment>
          <Table
            dataReady={dataReady}
            tableHeaders={TableHeaders}
            tableData={TableData}
            onSelectionChange={(item) => setSelectedInventory(item)}
            hasSelection
          />
          {selectedInventory && !Array.isArray(selectedInventory) && (
            <InventoryDetails
              inventory={selectedInventory}
              setInventory={setInventory}
              setSelectedInventory={setSelectedInventory}
            />
          )}
        </React.Fragment>
      )}
    </React.Fragment>
  );
};

export default InventoryPanel;
