import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { TabView, TabPanel } from "primereact/tabview";
import { faListUl } from "@fortawesome/free-solid-svg-icons";
import * as Constants from "../../../constants";
import { getAuthHeader, getRolePermissions } from "../../../helpers/Authorization";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import CommonTransferPanel from "./CommonTransferPanel";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import { useHistory } from "react-router-dom";
import { persistSetTab } from "../../../helpers/helperFunctions";
import { persistGetTab } from "../../../helpers/helperFunctions";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";

const ListTransfersPanel = () => {
  const { t } = useTranslation();
  const history = useHistory();
  const [dataReady, setDataReady] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const [transfers, setTransfers] = useState([]);
  const [selectedTransfer, setSelectedTransfer] = useState(null);
  const [isSupervisor, setIsSupervisor] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    persistGetTab(setActiveIndex);

    const rolePermissions = getRolePermissions();
    if (rolePermissions.role.toLowerCase() === "supervisor") setIsSupervisor(true);
    else setIsSupervisor(false);
  }, []);

  useEffect(() => {
    if (!dataReady) {
      const cancelTokenSource = axios.CancelToken.source();
      setSelectedTransfer(null);

      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Transfer/List`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          const transfer_list = response.data.map((data) => {
            data.status = data.status.charAt(0).toUpperCase() + data.status.slice(1);
            return data;
          });
          setTransfers(transfer_list);
          setDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
  }, [dataReady]);

  let inProgressTransfers = [];
  let completedTransfers = [];

  if (transfers) {
    inProgressTransfers = transfers.filter((transfer) => {
      return !["delivered", "denied", "cancelled"].includes(transfer.status.toLowerCase());
    });
    completedTransfers = transfers.filter((transfer) => {
      return ["delivered", "denied", "cancelled"].includes(transfer.status.toLowerCase());
    });
  }

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={isSupervisor ? ["Map", "Transfers"] : ["Map", "Transfers", "Request"]}
          activeTab={"Transfers"}
          urls={
            isSupervisor
              ? ["/transfers", "/transfers/list"]
              : ["/transfers", "/transfers/list", "/transfers/asset-transfer"]
          }
        />
      )}
      <PanelHeader icon={faListUl} text={t("navigationItems.list_transfers")} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={
            isSupervisor
              ? ["Transfer Map", "List Transfers"]
              : ["Transfer Map", "List Transfers", "Transfer Asset"]
          }
          activeTab={"List Transfers"}
          urls={
            isSupervisor
              ? ["/transfers", "/transfers/list"]
              : ["/transfers", "/transfers/list", "/transfers/asset-transfer"]
          }
        />
      )}
      <TabView
        className={`darkSubTab darkTable ${isMobile ? "" : "p-mt-5"}`}
        activeIndex={activeIndex}
        onTabChange={(e) => {
          persistSetTab(e, history);
          setActiveIndex(e.index);
        }}
      >
        <TabPanel header={t("general.in_progress").toUpperCase()}>
          <CommonTransferPanel
            transfers={inProgressTransfers}
            setTransfers={setTransfers}
            selectedTransfer={selectedTransfer}
            setSelectedTransfer={setSelectedTransfer}
            dataReady={dataReady}
            tab={activeIndex}
          />
        </TabPanel>
        <TabPanel header={t("general.completed").toUpperCase()}>
          <CommonTransferPanel
            transfers={completedTransfers}
            setTransfers={setTransfers}
            selectedTransfer={selectedTransfer}
            setSelectedTransfer={setSelectedTransfer}
            dataReady={dataReady}
            tab={activeIndex}
          />
        </TabPanel>
      </TabView>
    </div>
  );
};

export default ListTransfersPanel;
