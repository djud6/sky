import React, { useState } from "react";
import { useTranslation } from "react-i18next";
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
import "../../styles/helpers/button4.scss";
import "../../styles/AssetDetailsPanel/AssetDetailsMoreMobile.scss";

const AssetDetailsMoreMobile = ({
  asset,
  detailsSection,
  setMoreDetails,
  setDetailsSection,
  setForceUpdate,
}) => {
  const { t } = useTranslation();
  const [mobileDetails, setMobileDetails] = useState(false);

  const BackBtn = () => (
    <div className="no-style-btn p-mt-5 p-mx-2">
      <Button
        label={t("general.back")}
        className="p-button-link"
        icon="pi pi-chevron-left"
        onClick={() => {
          setMoreDetails(false);
          setDetailsSection(null);
          window.history.replaceState(null, "", window.location.pathname);
        }}
      />
    </div>
  );

  return (
    <div className="asset-details-more-mobile">
      {detailsSection === t("assetDetailPanel.asset_log") && (
        <div className="asset-log p-mb-5">
          <BackBtn />
          <AssetLogTab vin={asset.VIN} asset={asset} />
        </div>
      )}
      {detailsSection === t("navigationItems.issues") && (
        <div className="history-tables p-mb-5">
          {!mobileDetails && <BackBtn />}
          <IssuesTab
            vin={asset.VIN}
            mobileDetails={mobileDetails}
            setMobileDetails={setMobileDetails}
          />
        </div>
      )}
      {detailsSection === t("navigationItems.repairs") && (
        <div className="history-tables p-mb-5">
          {!mobileDetails && <BackBtn />}
          <RepairsTab
            vin={asset.VIN}
            mobileDetails={mobileDetails}
            setMobileDetails={setMobileDetails}
          />
        </div>
      )}
      {detailsSection === t("navigationItems.maintenance") && (
        <div className="history-tables p-mb-5">
          {!mobileDetails && <BackBtn />}
          <MaintenanceTab
            vin={asset.VIN}
            mobileDetails={mobileDetails}
            setMobileDetails={setMobileDetails}
          />
        </div>
      )}
      {detailsSection === t("navigationItems.incidents") && (
        <div className="history-tables p-mb-5">
          {!mobileDetails && <BackBtn />}
          <IncidentsTab
            vin={asset.VIN}
            mobileDetails={mobileDetails}
            setMobileDetails={setMobileDetails}
          />
        </div>
      )}
      {detailsSection === t("navigationItems.transfers") && (
        <div className="history-tables p-mb-5">
          {!mobileDetails && <BackBtn />}
          <TransfersTab
            vin={asset.VIN}
            mobileDetails={mobileDetails}
            setMobileDetails={setMobileDetails}
          />
        </div>
      )}
      {detailsSection === t("assetDetailPanel.asset_downtime") && (
        <div className="downtime-tab p-mb-5">
          <BackBtn />
          <DowntimeTab vin={asset.VIN} />
        </div>
      )}
      {detailsSection === t("general.documents") && (
        <div className="history-tables p-mb-5">
          <BackBtn />
          <DocumentTab vin={asset.VIN} />
        </div>
      )}
      {detailsSection === t("general.costs") && (
        <div className="p-mb-5">
          <BackBtn />
          <CostsTab vin={asset.VIN} />
        </div>
      )}
      {detailsSection === t("motherChildAsset.linked_asset_tab_title") && (
        <div className="p-mb-5">
          <BackBtn />
          <LinkedAssetTab asset={asset} setForceUpdate={setForceUpdate} />
        </div>
      )}
    </div>
  );
};

export default AssetDetailsMoreMobile;
