import React, { useState } from "react";
import { useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Galleria } from "primereact/galleria";
import { faMinus, faArrowsAltH, faPen } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import CurrentDate from "../ShareComponents/helpers/CurrentDate";
import AssetDetailsTable from "./AssetDetailsTable";
import UpdateAssetDetail from "./UpdateAssetDetail";
import FullWidthSkeleton from "../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../styles/AssetDetailsPanel/AssetDetailsCard.scss";
import AddCustomField from "./AddCustomField";

const AssetDetailsCard = ({ vin, asset, assetImgs = [], isOperator, isSupervisor, setForceUpdate }) => {
  const history = useHistory();
  const { t } = useTranslation();
  const [updateDetail, setUpdateDetail] = useState(false);
  const [addCustomField, setAddCustomField] = useState(false);
  const responsiveOptions = [
    {
      breakpoint: "1500px",
      numVisible: 3,
    },
    {
      breakpoint: "1400px",
      numVisible: 2,
    },
    {
      breakpoint: "560px",
      numVisible: 1,
    },
  ];

  const placeholder = `${process.env.PUBLIC_URL}/assets/images/weather/default.png`;

  const onQuickAccess = (url) => {
    history.push({
      pathname: url,
      state: {
        vehicle: asset,
      },
    });
  };

  const itemTemplate = (item) => {
    return (
      <img
        src={item.itemImageSrc}
        onError={(e) => e.target.src = placeholder}
        alt={item.alt}
        style={{ maxWidth: "100%", maxHeight: "420px", display: "block" }}
      />
    );
  };

  const thumbnailTemplate = (item) => {
    return (
      <img
        src={item.thumbnailImageSrc}
        onError={(e) => e.target.src = placeholder}
        alt={item.alt}
        style={{ maxHeight: "50px", display: "block" }}
      />
    );
  };

  return (
    <div className="asset-details-left">
      <div className="asset-details-left-title">
        <h1 className="text-white font-weight-bold text-uppercase">
          {t("assetDetailPanel.page_title")}
        </h1>
        <h4 className="text-white">{CurrentDate()}</h4>
      </div>
      {asset ? (
        <div className="custom-asset-detail-view asset-details-card p-p-5">
          <div className="asset-details-card-header p-mb-4">
            <h2 className="font-weight-bold">{t("assetDetailPanel.asset_summary")}</h2>
            <h4>{t("general.header_vin", { vin: asset.VIN })}</h4>
          </div>
          <React.Fragment>
            <AssetDetailsTable asset={asset} vin={vin} />
            {!isOperator && !isSupervisor && (
              <div className="p-mt-2 p-d-flex p-flex-column asset-details-card-btn">
                <h3 className="font-weight-bold">{t("general.quick_actions")}</h3>
                <Button
                  className="p-d-flex p-jc-center p-mt-2 update-detail-btn"
                  onClick={() => setAddCustomField(true)}
                >
                  <FontAwesomeIcon icon={faPen} color="#ffffff" />
                  <span className="p-px-3 font-weight-bold">
                    {t("assetDetailPanel.add_custom_field")}
                  </span>
                </Button>

                <Button
                  className="p-d-flex p-jc-center p-mt-2 update-detail-btn"
                  onClick={() => setUpdateDetail(true)}
                >
                  <FontAwesomeIcon icon={faPen} color="#ffffff" />
                  <span className="p-px-3 font-weight-bold">
                    {t("assetDetailPanel.update_asset_detail")}
                  </span>
                </Button>
                {!asset.has_transfer && (
                  <Button
                    className="p-d-flex p-jc-center p-mt-3 transfer-btn"
                    onClick={() => onQuickAccess("/transfers/asset-transfer")}
                  >
                    <FontAwesomeIcon icon={faArrowsAltH} color="#ffffff" />
                    <span className="p-px-3 font-weight-bold">
                      {t("assetDetailPanel.transfer_asset")}
                    </span>
                  </Button>
                )}
                {!asset.has_disposal && asset.status.toLowerCase() !== "disposed-of" && (
                  <Button
                    className="p-d-flex p-jc-center p-mt-3 dispose-btn"
                    onClick={() => onQuickAccess("/asset-removal")}
                  >
                    <FontAwesomeIcon icon={faMinus} color="#000000" />
                    <span className="p-px-3 font-weight-bold">
                      {t("assetDetailPanel.dispose_asset")}
                    </span>
                  </Button>
                )}
              </div>
            )}
            {assetImgs.length !== 0 && (
              <div className="asset-images p-mt-5">
                <hr />
                <div className="p-mt-3">
                  <Galleria
                    value={assetImgs}
                    numVisible={4}
                    circular
                    showItemNavigators
                    item={itemTemplate}
                    thumbnail={thumbnailTemplate}
                    responsiveOptions={responsiveOptions}
                  />
                </div>
              </div>
            )}
          </React.Fragment>
        </div>
      ) : (
        <div className="custom-asset-detail-view asset-details-card p-p-5">
          <FullWidthSkeleton height="66vh">{""}</FullWidthSkeleton>
        </div>
      )}
      {asset && (
        <UpdateAssetDetail
          vehicle={asset}
          dialogStatus={updateDetail}
          setDialogStatus={setUpdateDetail}
          setForceUpdate={setForceUpdate}
        />
      )}
      {asset && (
        <AddCustomField
          vehicle={asset}
          dialogStatus={addCustomField}
          setDialogStatus={setAddCustomField}
          setForceUpdate={setForceUpdate}
        />
      )}
    </div>
  );
};

export default AssetDetailsCard;
