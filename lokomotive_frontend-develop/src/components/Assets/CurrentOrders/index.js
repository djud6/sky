import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { faHistory } from "@fortawesome/free-solid-svg-icons";
import { getAuthHeader } from "../../../helpers/Authorization";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import { TabView, TabPanel } from "primereact/tabview";
import CommonAssetOrdersPanel from "./CommonAssetOrdersPanel";
import { useHistory } from "react-router-dom";
import { persistSetTab } from "../../../helpers/helperFunctions";
import { persistGetTab } from "../../../helpers/helperFunctions";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";

const AssetCurrentOrdersPanel = () => {
  const { t } = useTranslation();
  const [dataReady, setDataReady] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const [inProgressRequests, setInProgressRequests] = useState([]);
  const [deliveredRequests, setDeliveredRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const history = useHistory();

  useEffect(() => {
    persistGetTab(setActiveIndex);
  }, []);

  useEffect(() => {
    if (!dataReady) {
      const authHeader = getAuthHeader();
      const controller = new AbortController();

      setSelectedRequest(null);

      let inProgress = axios.get(
        `${Constants.ENDPOINT_PREFIX}/api/v1/AssetRequest/InProgress/List`,
        {
          ...authHeader,
          signal: controller.signal,
        }
      );
      let delivered = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetRequest/Delivered/List`, {
        ...authHeader,
        signal: controller.signal,
      });

      axios.all([inProgress, delivered]).then(
        axios.spread((...responses) => {
          const inProgressAPIResponse = !!responses[0] ? responses[0].data : [];
          for (let i in inProgressAPIResponse) {
            if (!inProgressAPIResponse[i].vendor) {
              if (
                inProgressAPIResponse[i].vendor_email &&
                !["", "NA"].includes(inProgressAPIResponse[i].vendor_email)
              ) {
                inProgressAPIResponse[i].vendor_name = inProgressAPIResponse[i].vendor_email;
              }
            }
          }
          setInProgressRequests(inProgressAPIResponse);
          const deliveredAPIResponse = !!responses[1] ? responses[1].data : [];
          for (let i in deliveredAPIResponse) {
            if (!deliveredAPIResponse[i].vendor) {
              if (
                deliveredAPIResponse[i].vendor_email &&
                !["", "NA"].includes(deliveredAPIResponse[i].vendor_email)
              ) {
                deliveredAPIResponse[i].vendor_name = deliveredAPIResponse[i].vendor_email;
              }
            }
          }
          setDeliveredRequests(deliveredAPIResponse);

          setDataReady(true);
        })
      );
      return () => controller.abort();
    }
  }, [dataReady]);

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["Fleet", "Request", "Orders"]}
          activeTab={"Orders"}
          urls={["/assets-overview", "/assets/asset-request", "/assets/current-order"]}
        />
      )}
      <PanelHeader icon={faHistory} text="Current Asset Orders" />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Fleet Overview", "Asset Request", "Current Orders"]}
          activeTab={"Current Orders"}
          urls={["/assets-overview", "/assets/asset-request", "/assets/current-order"]}
        />
      )}

      <TabView
        className={`darkTable darkSubTab ${isMobile ? "" : "p-mt-5"}`}
        activeIndex={activeIndex}
        onTabChange={(e) => {
          persistSetTab(e.index, history);
          setActiveIndex(e.index);
        }}
      >
        <TabPanel header={t("assetRequestPanel.tabTitles_in_progress").toUpperCase()}>
          <CommonAssetOrdersPanel
            assetOrders={inProgressRequests}
            selectedAssetOrder={selectedRequest}
            setSelectedAssetOrder={setSelectedRequest}
            dataReady={dataReady}
            setRequests={setInProgressRequests}
            requestType={"InProgress"}
            tab={activeIndex}
            setDataReady={setDataReady}
          />
        </TabPanel>
        <TabPanel header={t("assetRequestPanel.tabTitles_delivered").toUpperCase()}>
          <CommonAssetOrdersPanel
            assetOrders={deliveredRequests}
            selectedAssetOrder={selectedRequest}
            setSelectedAssetOrder={setSelectedRequest}
            dataReady={dataReady}
            setRequests={setDeliveredRequests}
            requestType={"Delivered"}
            tab={activeIndex}
            setDataReady={setDataReady}
          />
        </TabPanel>
      </TabView>
    </div>
  );
};

export default AssetCurrentOrdersPanel;
