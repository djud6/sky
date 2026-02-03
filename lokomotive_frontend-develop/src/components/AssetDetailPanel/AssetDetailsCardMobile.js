import React, { useState, useEffect } from "react";
import { useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Galleria } from "primereact/galleria";
import UpdateAssetDetail from "./UpdateAssetDetail";
import FullWidthSkeleton from "../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import DetailsViewMobile from "../ShareComponents/DetailView/DetailsViewMobile";
import "../../styles/helpers/button4.scss";
import "../../styles/AssetDetailsPanel/AssetDetails.scss";
import placeholder from "../../images/background/placeholder.png";

const AssetDetailsCardMobile = ({
  isSupervisor,
  isOperator,
  asset,
  assetImgs,
  setMoreDetails,
  setDetailsSection,
  setForceUpdate,
}) => {
  const history = useHistory();
  const { t } = useTranslation();
  const [tableTitles, setTableTitles] = useState([]);
  const [tableValues, setTableValues] = useState([]);
  const [updateDetail, setUpdateDetail] = useState(false);

  const onQuickAccess = (url) => {
    history.push({
      pathname: url,
      state: {
        vehicle: asset,
      },
    });
  };

  useEffect(() => {
    if (asset) {
      setTableTitles([
        t("assetDetailPanel.status_label"),
        t("assetDetailPanel.asset_type_label"),
        t("assetDetailPanel.business_unit_label"),
        t("assetDetailPanel.location_label"),
        t("assetDetailPanel.manufacturer_label"),
        t("assetDetailPanel.company_label"),
        t("assetDetailPanel.year_of_manufacture"),
        t("assetDetailPanel.fuel_type_label"),
        t("assetDetailPanel.license_plate_label"),
        t("assetDetailPanel.parent_asset_label"),
        t("assetDetailPanel.child_assets_label"),
        ...(asset.hours_or_mileage.toLowerCase() === "mileage" ||
        asset.hours_or_mileage.toLowerCase() === "both"
          ? [t("assetDetailPanel.mileage_label"), t("assetDetailPanel.daily_average_mileage")]
          : []),
        ...(asset.hours_or_mileage.toLowerCase() === "hours" ||
        asset.hours_or_mileage.toLowerCase() === "both"
          ? [t("assetDetailPanel.hours_label"), t("assetDetailPanel.daily_average_hours")]
          : []),
        t("assetDetailPanel.total_cost"),
      ]);
      setTableValues([
        asset.status,
        asset.asset_type,
        asset.businessUnit,
        asset.current_location,
        asset.manufacturer || t("general.not_applicable"),
        asset.company || t("general.not_applicable"),
        asset.date_of_manufacture || t("general.not_applicable"),
        asset.fuel_type || t("general.not_applicable"),
        asset.license_plate || t("general.not_applicable"),
        asset.parent || t("general.not_applicable"),
        asset.children.length !== 0
          ? [
              asset.children.length > 1 &&
                asset.children.map((child) => {
                  return child + ", ";
                }),
            ]
          : [t("general.not_applicable")],
        ...(asset.hours_or_mileage.toLowerCase() === "mileage" ||
        asset.hours_or_mileage.toLowerCase() === "both"
          ? [asset.mileage, asset.daily_average_mileage.toFixed(2)]
          : []),
        ...(asset.hours_or_mileage.toLowerCase() === "hours" ||
        asset.hours_or_mileage.toLowerCase() === "both"
          ? [asset.hours, asset.daily_average_hours.toFixed(2)]
          : []),

        "$ "+ asset.total_cost.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        })  || t("general.not_applicable"),

      ]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [asset]);

  const itemTemplate = (item) => {
    return (
      <img
        src={item.itemImageSrc}
        onError={(e) => e.target.src = placeholder}
        alt={item.alt}
        style={{ maxWidth: "100%", maxHeight: "320px", display: "block" }}
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

  const AssetImages = (
    <React.Fragment>
      {assetImgs.length !== 0 && (
        <div className="asset-images p-mt-5">
          <hr />
          <div className="p-mt-3">
            <Galleria
              value={assetImgs}
              numVisible={3}
              circular
              showItemNavigators
              item={itemTemplate}
              thumbnail={thumbnailTemplate}
            />
          </div>
        </div>
      )}
    </React.Fragment>
  );

  return (
    <div className="p-mb-5">
      {asset ? (
        <React.Fragment>
          <div className="details-card-title">{t("assetDetailPanel.page_title")}</div>
          <DetailsViewMobile
            header={t("general.header_vin", { vin: asset.VIN })}
            titles={tableTitles}
            values={tableValues}
            additionalDescr={AssetImages}
            editBtn={!isSupervisor && t("assetDetailPanel.update_asset_detail")}
            onEdit={() => setUpdateDetail(true)}
            actionBtn1={
              !isOperator && !isSupervisor && !asset.has_transfer
                ? [
                    t("assetDetailPanel.transfer_asset"),
                    "pi-external-link",
                    "detail-action-color-1",
                  ]
                : ""
            }
            onActionBtn1={() => onQuickAccess("/transfers/asset-transfer")}
            actionBtn2={
              !isOperator &&
              !isSupervisor &&
              !asset.has_disposal &&
              asset.status.toLowerCase() !== "disposed-of"
                ? [t("assetDetailPanel.dispose_asset"), "pi-external-link", "detail-action-color-2"]
                : ""
            }
            onActionBtn2={() => onQuickAccess("/asset-removal")}
            enableMore
            detailsSection={
              !isOperator
                ? [
                    t("assetDetailPanel.asset_log"),
                    t("navigationItems.issues"),
                    t("navigationItems.repairs"),
                    t("navigationItems.maintenance"),
                    t("navigationItems.incidents"),
                    t("navigationItems.transfers"),
                    t("assetDetailPanel.asset_downtime"),
                    t("general.documents"),
                    t("general.costs"),
                    t("motherChildAsset.linked_asset_tab_title"),
                  ]
                : [t("navigationItems.issues")]
            }
            setMoreDetails={setMoreDetails}
            setDetailsSection={setDetailsSection}
          />
        </React.Fragment>
      ) : (
        <FullWidthSkeleton height="550px" />
      )}
      {asset && (
        <UpdateAssetDetail
          vehicle={asset}
          dialogStatus={updateDetail}
          setDialogStatus={setUpdateDetail}
          setForceUpdate={setForceUpdate}
        />
      )}
    </div>
  );
};

export default AssetDetailsCardMobile;
