import React, { useEffect, useState } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import { TabView, TabPanel } from "primereact/tabview";
import { Button } from "primereact/button";
import { faTruckMoving } from "@fortawesome/free-solid-svg-icons";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import InventoryPanel from "./InventoryPanel";
import InventoryAdd from "./InventoryAdd";
import "../../../styles/InventoryPanel/ManageInventory/mainInventory.scss";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";
import "../../../styles/helpers/button2.scss";
import ConsoleHelper from "../../../helpers/ConsoleHelper";

const ManageInventory = () => {
  const [dataReady, setDataReady] = useState(false);
  const [inventory, setInventory] = useState([]);
  const [addDialog, setAddDialog] = useState(false);
  const [selectedInventory, setSelectedInventory] = useState(null);

  useEffect(() => {
    setSelectedInventory(null);

    const cancelTokenSource = axios.CancelToken.source();

    if (!dataReady) {
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Inventory/List`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((res) => {
          const data = res.data;
          setInventory(data);
          setDataReady(true);
        })
        .catch((err) => {
          setDataReady(true);
          ConsoleHelper(err);
        });
    }
  }, [dataReady]);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const { t } = useTranslation();
  return (
    <div className="inventory_content">
      <PanelHeader
        icon={faTruckMoving}
        text={t("inventoryPanelIndex.inventory")}
        mobileBg={isMobile}
      />

      <div className="p-d-flex p-jc-end btns-container mt-4">
        <div className={`btn-2 p-mr-3`}>
          <Button
            icon="pi pi-upload"
            label={t("inventoryPanelIndex.add_inventory")}
            tooltip={t("inventoryPanelIndex.add_inventory_tooltip")}
            tooltipOptions={{ position: "top" }}
            onClick={() => {
              setAddDialog(true);
            }}
            disabled={selectedInventory}
          />
        </div>
      </div>
      <TabView className="darkSubTab darkTable inventoryTable p-mt-4">
        <TabPanel>
          <InventoryPanel
            inventory={inventory}
            dataReady={dataReady}
            setDataReady={setDataReady}
            setInventory={setInventory}
            selectedInventory={selectedInventory}
            setSelectedInventory={setSelectedInventory}
          />
        </TabPanel>
      </TabView>
      <InventoryAdd setDataReady={setDataReady} addDialog={addDialog} setAddDialog={setAddDialog} />
    </div>
  );
};

export default ManageInventory;
