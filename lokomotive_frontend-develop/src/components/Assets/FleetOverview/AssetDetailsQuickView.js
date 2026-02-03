import React, { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import { getRolePermissions } from "../../../helpers/Authorization";
import { faMinus } from "@fortawesome/free-solid-svg-icons";
import { faOilCan } from "@fortawesome/free-solid-svg-icons";
import { faWrench } from "@fortawesome/free-solid-svg-icons";
import { faCarCrash } from "@fortawesome/free-solid-svg-icons";
import { faArrowsAltH } from "@fortawesome/free-solid-svg-icons";
import { faExclamationTriangle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import AssetDetailsTable from "../../AssetDetailPanel/AssetDetailsTable";
import "../../../styles/AssetDetailsPanel/AssetDetailsCard.scss";

const AssetDetailsQuickView = ({ asset, setSelectedAsset }) => {
  const { t } = useTranslation();
  const history = useHistory();
  const [isSupervisor, setIsSupervisor] = useState(false);
  const [currentDetailBtnsCount, setCurrentDetailBtnsCount] = useState(6);

  useEffect(() => {
    const rolePermissions = getRolePermissions();
    if (rolePermissions.role.toLowerCase() === "supervisor") {
      setIsSupervisor(true);
      setCurrentDetailBtnsCount(4);
    } else {
      setIsSupervisor(false);
      setCurrentDetailBtnsCount(6);
    }
  }, []);

  const onQuickAccess = (url) => {
    history.push({
      pathname: url,
      state: {
        vehicle: asset,
      },
    });
  };

  const onViewMoreDetails = () => {
    history.push(`/asset-details/${asset.VIN}`);
  };

  const detailsViewHeader = () => {
    return (
      <div>
        <h2>{t("assetDetailPanel.asset_summary")}</h2>
        <h4>{t("general.header_vin", { vin: asset.VIN })}</h4>
      </div>
    );
  };

  const detailsViewFooter = () => {
    return (
      <Button
        label={t("general.view_more_details")}
        className="p-button-link"
        onClick={onViewMoreDetails}
      />
    );
  };

  const btnWidth = 100 / (currentDetailBtnsCount / 2) - 1;

  return (
    <Dialog
      className="custom-asset-detail-view"
      header={detailsViewHeader}
      visible
      position={"right"}
      modal
      style={{ width: "540px" }}
      footer={detailsViewFooter}
      onHide={() => setSelectedAsset(null)}
      draggable={false}
      resizable={false}
    >
      <AssetDetailsTable asset={asset} />

      <div className="p-mt-2 p-d-flex p-flex-column">
        <h3>{t("general.quick_actions")}</h3>
        <div
          id="asset-details-btns"
          className="p-mt-2 p-d-flex p-flex-wrap p-jc-between asset-details-btns"
        >
          <Button
            style={{ width: `${btnWidth}%` }}
            onClick={() => onQuickAccess("/maintenance/schedule")}
          >
            <FontAwesomeIcon icon={faOilCan} color="#C4C4C4" />
            <span className="p-px-3">{t("navigationItems.maintenance")}</span>
          </Button>
          <Button style={{ width: `${btnWidth}%` }} onClick={() => onQuickAccess("/incidents/new")}>
            <FontAwesomeIcon icon={faCarCrash} color="#C4C4C4" />
            <span className="p-px-3">{t("navigationItems.incidents")}</span>
          </Button>
          <Button
            style={{ width: `${btnWidth}%` }}
            onClick={() => onQuickAccess("/repairs/request")}
          >
            <FontAwesomeIcon icon={faWrench} color="#C4C4C4" />
            <span className="p-px-3">{t("navigationItems.repairs")}</span>
          </Button>

          <Button style={{ width: `${btnWidth}%` }} onClick={() => onQuickAccess("/issues/new")}>
            <FontAwesomeIcon icon={faExclamationTriangle} color="#C4C4C4" />
            <span className="p-px-3">{t("navigationItems.issues")}</span>
          </Button>
          {!isSupervisor && (
            <React.Fragment>
              <Button
                style={{ width: `${btnWidth}%` }}
                onClick={() => onQuickAccess("/transfers/asset-transfer")}
              >
                <FontAwesomeIcon icon={faArrowsAltH} color="#C4C4C4" />
                <span className="p-px-3">{t("navigationItems.transfers")}</span>
              </Button>
              <Button
                style={{ width: `${btnWidth}%` }}
                onClick={() => onQuickAccess("/asset-removal")}
              >
                <FontAwesomeIcon icon={faMinus} color="#C4C4C4" />
                <span className="p-px-3">{t("navigationItems.asset_removal")}</span>
              </Button>
            </React.Fragment>
          )}
        </div>
      </div>
    </Dialog>
  );
};

export default AssetDetailsQuickView;
