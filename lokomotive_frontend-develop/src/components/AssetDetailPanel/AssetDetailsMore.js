import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useHistory } from "react-router-dom";
import { Button } from "primereact/button";
import AssetLogTab from "./AssetLogTab";
import IssuesTab from "./IssuesTab";
import RepairsTab from "./RepairsTab";
import MaintenanceTab from "./MaintenanceTab";
import IncidentsTab from "./IncidentsTab";
import TransfersTab from "./TransfersTab";
import DowntimeTab from "./DowntimeTab";
import DocumentTab from "./DocumentTab";
import CostsTab from "./CostsTab";
import LinkedAssetTab from "./LinkedAssetTab";
import FullWidthSkeleton from "../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../styles/ShareComponents/Table/table.scss";
import "../../styles/helpers/button3.scss";
import "../../styles/AssetDetailsPanel/AssetDetailsMore.scss";

const AssetDetailsMore = ({ asset, isOperator, setForceUpdate }) => {
  const history = useHistory();
  const { t } = useTranslation();
  const [activeSection, setActiveSection] = useState(null);

  const OptionButton = ({ label, section }) => {
    return (
      <div className="p-mt-4">
        <Button
          className="p-d-flex p-jc-between p-button-link"
          onClick={() => setActiveSection(section)}
        >
          <span>{label}</span>
          <i className="pi pi-angle-right" style={{ fontSize: "2em" }}>
            {""}
          </i>
        </Button>
        <hr />
      </div>
    );
  };

  const handleRouting = (url) => {
    history.push(url);
  };

  const handleNewAssetOrder = () => {
    history.push({
      pathname: `/assets/asset-request`,
      state: { vehicle: asset },
    });
  };

  return (
    <div className="asset-details-more">
      <div className="asset-details-more-btn p-d-flex p-jc-end">
        <div className="btn-3 p-mb-4 p-d-flex p-ai-end">
          <Button
            label={t("assetDetailPanel.fleet_overview_cap")}
            icon="pi pi-arrow-right"
            iconPos="right"
            onClick={() => handleRouting("/assets")}
          />
        </div>
      </div>
      {asset ? (
        <div className="asset-details-more-body">
          <div className="header p-d-flex p-flex-column">
            <div className="p-d-flex p-jc-between">
              <h3>{t("general.header_vin", { vin: asset.VIN })}</h3>
              {!isOperator && (
                <div className="order-asset-btn">
                  <Button
                    icon="pi pi-plus-circle"
                    label={t("assetDetailPanel.order_same_asset")}
                    className="p-mx-3"
                    onClick={() => handleNewAssetOrder()}
                  />
                </div>
              )}
            </div>
            <h5 className="p-mt-2 p-mb-4">{asset.asset_type}</h5>
            <hr />
          </div>
          <div className="body">
            {!activeSection ? (
              <div className="options p-pt-2">
                {!isOperator && (
                  <OptionButton label={t("assetDetailPanel.asset_log")} section={"assetLog"} />
                )}
                <OptionButton label={t("navigationItems.issues")} section={"issues"} />
                {!isOperator && (
                  <OptionButton label={t("navigationItems.repairs")} section={"repairs"} />
                )}
                {!isOperator && (
                  <OptionButton label={t("navigationItems.maintenance")} section={"maintenance"} />
                )}
                {!isOperator && (
                  <OptionButton label={t("navigationItems.incidents")} section={"incidents"} />
                )}
                {!isOperator && (
                  <OptionButton label={t("navigationItems.transfers")} section={"transfers"} />
                )}
                {!isOperator && (
                  <OptionButton label={t("assetDetailPanel.asset_downtime")} section={"downtime"} />
                )}
                {!isOperator && (
                  <OptionButton label={t("general.documents")} section={"documents"} />
                )}
                {!isOperator && <OptionButton label={t("general.costs")} section={"costs"} />}
                {!isOperator && (
                  <OptionButton
                    label={t("motherChildAsset.linked_asset_tab_title")}
                    section={"linkedAsset"}
                  />
                )}
              </div>
            ) : (
              <div className="section-body">
                <div className="back-btn">
                  <Button
                    className="p-button-link p-button-lg"
                    label="Back"
                    icon="pi pi-angle-left"
                    onClick={() => {
                      setActiveSection(null);
                      window.history.replaceState(null, "", window.location.pathname);
                    }}
                  />
                </div>
                {activeSection === "assetLog" && <AssetLogTab vin={asset.VIN} asset={asset} />}
                {activeSection === "issues" && <IssuesTab vin={asset.VIN} />}
                {activeSection === "repairs" && <RepairsTab vin={asset.VIN} />}
                {activeSection === "maintenance" && <MaintenanceTab vin={asset.VIN} />}
                {activeSection === "incidents" && <IncidentsTab vin={asset.VIN} />}
                {activeSection === "transfers" && <TransfersTab vin={asset.VIN} />}
                {activeSection === "downtime" && <DowntimeTab vin={asset.VIN} />}
                {activeSection === "documents" && <DocumentTab vin={asset.VIN} />}
                {activeSection === "costs" && <CostsTab vin={asset.VIN} />}
                {activeSection === "linkedAsset" && (
                  <LinkedAssetTab asset={asset} setForceUpdate={setForceUpdate} />
                )}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="asset-details-more-body">
          <FullWidthSkeleton height="66vh">{""}</FullWidthSkeleton>
        </div>
      )}
    </div>
  );
};

export default AssetDetailsMore;
