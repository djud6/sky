import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { faTable } from "@fortawesome/free-solid-svg-icons";
import { getAuthHeader, getRolePermissions } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import AssetsTable from "./AssetsTable";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/ShareComponents/Table/table.scss";

const FleetOverviewPanel = () => {
  const [assets, setAssets] = useState([]);
  const [dataReady, setDataReady] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [forceUpdate, setForceUpdate] = useState(Date.now());
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const [isSupervisor, setIsSupervisor] = useState(false);
  const { t } = useTranslation();

  useEffect(() => {
    const rolePermissions = getRolePermissions();
    if (rolePermissions.role.toLowerCase() === "supervisor") setIsSupervisor(true);
    else setIsSupervisor(false);
  }, []);

  const getAssetData = async () => {
    const cancelTokenSource = axios.CancelToken.source();
    await axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/All`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        setAssets(response.data);
        setDataReady(true);
      })
      .catch((error) => {
        ConsoleHelper(error);
      });

    if (selectedAsset) {
      const getSelected = assets.filter((asset) => asset.VIN === selectedAsset.VIN);
      setSelectedAsset(getSelected[0]);
    }
  };

  useEffect(() => {
    if (!dataReady) {
      const cancelTokenSource = axios.CancelToken.source();
      getAssetData();
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataReady]);

  useEffect(() => {
    if (dataReady) {
      const cancelTokenSource = axios.CancelToken.source();
      getAssetData();
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [forceUpdate]);

  return (
    <div>
      {isMobile && !isSupervisor && (
        <QuickAccessTabs
          tabs={["Fleet", "Request", "Orders"]}
          activeTab={"Fleet"}
          urls={["/assets-overview", "/assets/asset-request", "/assets/current-order"]}
        />
      )}
      <PanelHeader icon={faTable} text={t("navigationItems.fleet_overview")} />
      {!isMobile && !isSupervisor && (
        <QuickAccessTabs
          tabs={["Fleet Overview", "Asset Request", "Current Orders"]}
          activeTab={"Fleet Overview"}
          urls={["/assets-overview", "/assets/asset-request", "/assets/current-order"]}
        />
      )}

      <AssetsTable
        assets={assets}
        selectedAsset={selectedAsset}
        setSelectedAsset={setSelectedAsset}
        dataReady={dataReady}
        forceUpdate={forceUpdate}
        setForceUpdate={setForceUpdate}
      />

    </div>
  );
};

export default FleetOverviewPanel;
