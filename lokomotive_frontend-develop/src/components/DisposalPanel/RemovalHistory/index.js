import React, { useEffect, useState } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { TabView, TabPanel } from "primereact/tabview";
import { faRecycle } from "@fortawesome/free-solid-svg-icons";
import { getAuthHeader } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import CommonRemovalPanel from "./CommonRemovalPanel";
import { capitalize } from "../../../helpers/helperFunctions";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import { useHistory } from "react-router-dom";
import { persistSetTab } from "../../../helpers/helperFunctions";
import { persistGetTab } from "../../../helpers/helperFunctions";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";

const RemovalHistoryPanel = () => {
  const { t } = useTranslation();
  const [removals, setRemovalData] = useState([]);
  const [dataReady, setDataReady] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const history = useHistory();

  useEffect(() => {
    persistGetTab(setActiveIndex);
  }, []);

  useEffect(() => {
    if (!dataReady) {
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetDisposal/List`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          let data = response.data;

          data.forEach((disposal, index) => {
            data[index].disposal_type = capitalize(disposal.disposal_type);
            if (!data[index].vendor) {
              if (
                data[index].primary_vendor_email &&
                !["", "NA"].includes(data[index].primary_vendor_email)
              ) {
                data[index].vendor_name = data[index].primary_vendor_email;
              }
            }
          });
          setDataReady(true);
          setRemovalData(data);
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

  let incompleteRemovals = [];
  let completeRemovals = [];
  const incompleteStatus = [
    "waiting for vendor",
    "awaiting approval",
    "approved",
    "in transit - to vendor",
    "at vendor",
    "in progress",
  ];
  const completeStatus = ["complete", "cancelled", "denied"];

  if (dataReady && removals?.length > 0) {
    incompleteRemovals = removals.filter((i) => {
      return incompleteStatus.includes(i.status?.toLowerCase());
    });
    completeRemovals = removals.filter((i) => {
      return completeStatus.includes(i.status?.toLowerCase());
    });
  }

  return (
    <React.Fragment>
      {isMobile && (
        <QuickAccessTabs
          tabs={["Asset Removal", "Removal History"]}
          activeTab={"Removal History"}
          urls={["/asset-removal", "/asset-removal/history"]}
        />
      )}
      <PanelHeader icon={faRecycle} text={t("removalHistory.panel_title")} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Asset Removal", "Asset Removal History"]}
          activeTab={"Asset Removal History"}
          urls={["/asset-removal", "/asset-removal/history"]}
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
        <TabPanel header={t("general.incomplete").toUpperCase()}>
          <CommonRemovalPanel
            className="p-mt-2"
            removalsData={incompleteRemovals}
            setRemovalData={setRemovalData}
            dataReady={dataReady}
            setDataReady={setDataReady}
            tab={activeIndex}
          />
        </TabPanel>
        <TabPanel header={t("general.complete").toUpperCase()}>
          <CommonRemovalPanel
            className="p-mt-2"
            removalsData={completeRemovals}
            setRemovalData={setRemovalData}
            dataReady={dataReady}
            setDataReady={setDataReady}
            tab={activeIndex}
          />
        </TabPanel>
      </TabView>
    </React.Fragment>
  );
};

export default RemovalHistoryPanel;
