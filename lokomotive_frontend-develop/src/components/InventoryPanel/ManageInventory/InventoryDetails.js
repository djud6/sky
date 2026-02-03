import React, { useState } from "react";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import { capitalize } from "../../../helpers/helperFunctions";
import DetailsView from "../../ShareComponents/DetailView/DetailsView";
import DetailsViewMobile from "../../ShareComponents/DetailView/DetailsViewMobile";
import InventoryUpdate from "./InventoryUpdate";

const InventoryDetails = ({ inventory, setInventory, setSelectedInventory }) => {
  const { t } = useTranslation();
  const [updateDialog, setUpdateDialog] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const onBack = () => {
    setSelectedInventory(null);
  };

  let detailViewTitles = [
    t("inventoryDetails.inventory_type"),
    t("inventoryDetails.description"),
    t("inventoryDetails.location"),
    t("inventoryDetails.equipment_type"),
    t("inventoryDetails.serial"),
    t("inventoryDetails.per_unit_cost"),
    t("inventoryDetails.date_of_manufacture"),
    t("general.created_by"),
    t("general.modified_by"),
    t("general.date_created"),
    t("general.date_updated"),
  ];

  let detailViewValues = [
    capitalize(inventory.inventory_type) || [t("general.not_applicable")],
    inventory.description || [t("general.not_applicable")],
    inventory.location || [t("general.not_applicable")],
    inventory.equipment_type || [t("general.not_applicable")],
    inventory.serial || [t("general.not_applicable")],
    inventory.per_unit_cost ? inventory.per_unit_cost.toFixed(2) : [t("general.not_applicable")],
    ...(moment(inventory.date_of_manufacture).isValid()
      ? [moment(inventory.date_of_manufacture).format("YYYY-MM-DD")]
      : [t("general.not_applicable")]),
    inventory.created_by,
    inventory.modified_by,
    moment(inventory.date_created).format("YYYY-MM-DD"),
    moment(inventory.date_modified).format("YYYY-MM-DD"),
  ];

  return (
    <React.Fragment>
      {isMobile ? (
        /* Mobile Details View */
        <div className="p-mx-2">
          <div className="no-style-btn p-my-3">
            <Button
              label={t("general.back")}
              className="p-button-link"
              icon="pi pi-chevron-left"
              onClick={() => onBack()}
            />
          </div>
          <DetailsViewMobile
            titles={detailViewTitles}
            values={detailViewValues}
            onHideDialog={setSelectedInventory}
            editBtn={t("inventoryPanelIndex.update_inventory")}
            onEdit={() => {
              setUpdateDialog(true);
            }}
          />
        </div>
      ) : (
        /* Desktop Details View */
        <DetailsView
          headers={[t("inventoryDetails.inventory_details")]}
          titles={detailViewTitles}
          values={detailViewValues}
          onHideDialog={setSelectedInventory}
          editBtn={t("inventoryPanelIndex.update_inventory")}
          onEdit={() => {
            setUpdateDialog(true);
          }}
        />
      )}
      <InventoryUpdate
        updateDialog={updateDialog}
        setUpdateDialog={setUpdateDialog}
        inventory={inventory}
        setSelectedInventory={setSelectedInventory}
        setInventory={setInventory}
      />
    </React.Fragment>
  );
};

export default InventoryDetails;
