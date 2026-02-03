import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { faBus } from "@fortawesome/free-solid-svg-icons";
import { getAuthHeader } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import { Button } from "primereact/button";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import ChartCard from "../../ShareComponents/ChartCard/ChartCard";
import MapChart from "../../ShareComponents/ChartCard/MapChart";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import AssetOrderForm from "./AssetOrderForm";
import AssetOrderFormMobile from "./AssetOrderFormMobile";
import AssetRequestMobile from "./AssetRequestMobile";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button3.scss";
import "../../../styles/Assets/assetRequest.scss";

const AssetRequest = () => {
  const { t } = useTranslation();
  const mapRef = useRef(null);
  const history = useHistory();
  const [mapChartParams, setMapChartParams] = useState(null);
  const [mobileForm, setMobileForm] = useState(false);
  const [divHeight, setDivHeight] = useState(0);
  const isBigScreen = useMediaQuery({ query: "(min-width: 630px)" });
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (isBigScreen) setDivHeight(mapRef.current.clientHeight);
    // eslint-disable-next-line
  }, [window.innerHeight]);

  useEffect(() => {
    const controller = new AbortController();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Chart/Get/Location/Count/Operators/Assets`, {
        ...getAuthHeader(),
        signal: controller.signal,
      })
      .then((response) => {
        setMapChartParams(response.data);
      })
      .catch((error) => {
        ConsoleHelper(error);
      });
    return () => controller.abort();
  }, []);

  return (
    <div className="asset-manage-page">
      {isBigScreen ? (
        <React.Fragment>
          <PanelHeader icon={faBus} text={t("assetRequestPanel.asset_request")} />
          {!isMobile && (
            <QuickAccessTabs
              tabs={["Fleet Overview", "Asset Request", "Current Orders"]}
              activeTab={"Asset Request"}
              urls={["/assets-overview", "/assets/asset-request", "/assets/current-order"]}
            />
          )}
          <div className="p-grid nested-grid asset-manage-content p-mt-5">
            <div className="p-sm-12 p-md-12 p-lg-12 p-xl-6">
              <div className="asset-order">
                <AssetOrderForm />
              </div>
            </div>
            <div className="p-sm-12 p-md-12 p-lg-12 p-xl-6">
              <div className="live-asset-map" ref={mapRef}>
                <ChartCard title={t("assetRequestPanel.asset_map_title")}>
                  {mapChartParams ? (
                    <MapChart datasets={mapChartParams} height={`${divHeight - 85}px`} />
                  ) : (
                    <FullWidthSkeleton height={`${divHeight - 85}px`} />
                  )}
                </ChartCard>
              </div>
            </div>
          </div>
        </React.Fragment>
      ) : mobileForm ? (
        <AssetOrderFormMobile setMobileForm={setMobileForm} />
      ) : (
        <React.Fragment>
          <QuickAccessTabs
            tabs={["Fleet", "Request", "Orders"]}
            activeTab={"Request"}
            urls={["/assets-overview", "/assets/asset-request", "/assets/current-order"]}
          />
          <PanelHeader icon={faBus} text={t("assetRequestPanel.asset_request")} />
          <div className="p-grid nested-grid asset-manage-content p-mt-2 p-mx-2">
            <div className="p-col-12 p-pt-3">
              <AssetRequestMobile setMobileForm={setMobileForm} />
            </div>
            <div className="p-col-12">
              <div className="live-asset-map" style={{ height: "340px" }}>
                <ChartCard title={t("assetRequestPanel.asset_map_title")}>
                  {mapChartParams ? (
                    <MapChart datasets={mapChartParams} height={`260px`} />
                  ) : (
                    <FullWidthSkeleton height={`260px`} />
                  )}
                </ChartCard>
              </div>
            </div>
            <div className="w-100 p-mt-3 p-mb-5 p-d-flex p-jc-center btn-3">
              <Button
                label={t("assetDetailPanel.fleet_overview_cap")}
                icon="pi pi-arrow-right"
                iconPos="right"
                onClick={() => history.push("/assets")}
              />
            </div>
          </div>
        </React.Fragment>
      )}
    </div>
  );
};

export default AssetRequest;
