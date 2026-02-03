import React, { useState } from "react";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import TransferStatusUpdate from "./TransferStatusUpdate";
import DetailsView from "../../ShareComponents/DetailView/DetailsView";
import DetailsViewMobile from "../../ShareComponents/DetailView/DetailsViewMobile";
import UpdateTransfer from "./UpdateTransfer";
import { capitalize } from "../../../helpers/helperFunctions";
import "../../../styles/helpers/button4.scss";

const TransferDetails = ({ transfer, setTransfers, setSelectedTransfer, setMobileDetails }) => {
  const { t } = useTranslation();
  const [editDialogStatus, setEditDialogStatus] = useState(false);
  const [updateDialogStatus, setUpdateDialogStatus] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const progressSteps = [
    t("requestProgress.awaiting_approval"),
    t("requestProgress.awaiting_transfer"),
    t("requestProgress.in_transit"),
    t("requestProgress.delivered"),
  ];
  const progressContents = [
    t("requestProgress.awaiting_approval_content"),
    t("requestProgress.awaiting_transfer_content"),
    t("requestProgress.in_transit_content"),
    t("requestProgress.delivered_content"),
  ];

  const onBack = () => {
    setMobileDetails(false);
    setSelectedTransfer(null);
  };

  const detailViewTitles = [
    t("general.id"),
    t("general.status"),
    t("general.business_unit"),
    t("general.current_location"),
    t("general.destination_location"),
    t("general.estimated_cost"),
    t("general.created_by"),
    t("general.modified_by"),
    t("general.date_created"),
    t("general.date_updated"),
  ];
  const detailViewValues = [
    transfer.custom_id,
    capitalize(transfer.status),
    transfer.business_unit,
    transfer.current_location,
    transfer.destination_location,
    transfer.estimated_cost !== null
      ? transfer.estimated_cost.toFixed(2)
      : t("general.not_applicable"),
    transfer.created_by || t("general.not_applicable"),
    transfer.modified_by || t("general.not_applicable"),
    moment(transfer.date_created).format("YYYY-MM-DD") || t("general.not_applicable"),
    moment(transfer.date_modified).format("YYYY-MM-DD") || t("general.not_applicable"),
  ];

  const InTransitDetails = (
    <div className={`p-d-flex p-flex-column ${isMobile ? "main-details" : ""}`}>
      {isMobile && <hr className="solid" />}
      <span className="title text-white">{`${t("general.additional_details")}:`}</span>
      <div className="p-d-flex">
        <span className="detail-title">
          {`${t("removalPanel.interior_condition_of_the_asset")}:`}
        </span>
        <span className="sub-value">&nbsp;&nbsp;{capitalize(transfer.interior_condition)}</span>
      </div>
      <div className="p-d-flex">
        <span className="detail-title">{`${t("removalPanel.interior_condition_details")}:`}</span>
        {transfer.interior_condition_details ? (
          <span className="sub-value">&nbsp;&nbsp;{transfer.interior_condition_details}</span>
        ) : (
          <span className="sub-value">&nbsp;&nbsp;{t("general.not_applicable")}</span>
        )}
      </div>
      <div className="p-d-flex">
        <span className="detail-title">
          {`${t("removalPanel.exterior_condition_of_the_asset")}:`}
        </span>
        <span className="sub-value">&nbsp;&nbsp;{capitalize(transfer.exterior_condition)}</span>
      </div>
      <div className="p-d-flex">
        <span className="detail-title">{`${t("removalPanel.exterior_condition_details")}:`}</span>
        {transfer.exterior_condition_details ? (
          <span className="sub-value">&nbsp;&nbsp;{transfer.exterior_condition_details}</span>
        ) : (
          <span className="sub-value">&nbsp;&nbsp;{t("general.not_applicable")}</span>
        )}
      </div>
      {!isMobile && <hr className="solid" />}
    </div>
  );

  return (
    <div>
      {isMobile ? (
        <div>
          <div className="no-style-btn p-my-3">
            <Button
              label={t("general.back")}
              className="p-button-link"
              icon="pi pi-chevron-left"
              onClick={() => onBack()}
            />
          </div>
          <DetailsViewMobile
            header={t("assetTransferPanel.transfer_details")}
            titles={detailViewTitles}
            values={detailViewValues}
            description={[
              t("assetTransferPanel.transfer_justification"),
              transfer.justification || t("general.not_applicable"),
            ]}
            additionalDescr={
              transfer.status.toLowerCase() === "in transit" ||
              transfer.status.toLowerCase() === "delivered"
                ? InTransitDetails
                : ""
            }
            files={transfer.files}
            editBtn={
              !["delivered", "denied", "cancelled"].includes(transfer.status.toLowerCase())
                ? t("assetTransferPanel.edit_transfer_header")
                : ""
            }
            onEdit={() => setEditDialogStatus(true)}
            actionBtn1={
              !["delivered", "denied", "cancelled"].includes(transfer.status.toLowerCase())
                ? [t("general.update_status"), "pi-check-circle", "detail-action-color-1"]
                : ""
            }
            onActionBtn1={() => setUpdateDialogStatus(true)}
            progressSteps={progressSteps}
            progressContents={progressContents}
            progressActive={transfer.status}
          />
        </div>
      ) : (
        <DetailsView
          headers={[
            t("assetTransferPanel.transfer_details"),
            t("general.header_vin", { vin: transfer.VIN }),
          ]}
          titles={detailViewTitles}
          values={detailViewValues}
          description={[
            t("assetTransferPanel.transfer_justification"),
            transfer.justification || t("general.not_applicable"),
          ]}
          additionalDescr={
            transfer.status.toLowerCase() === "in transit" ||
            transfer.status.toLowerCase() === "delivered"
              ? InTransitDetails
              : ""
          }
          files={transfer.files}
          editBtn={
            !["delivered", "denied", "cancelled"].includes(transfer.status.toLowerCase())
              ? t("assetTransferPanel.edit_transfer_header")
              : ""
          }
          onEdit={() => setEditDialogStatus(true)}
          actionBtn1={
            !["delivered", "denied", "cancelled"].includes(transfer.status.toLowerCase())
              ? [t("general.update_status"), "pi-check-circle", "detail-action-color-1"]
              : ""
          }
          onActionBtn1={() => setUpdateDialogStatus(true)}
          onHideDialog={setSelectedTransfer}
          progressSteps={progressSteps}
          progressContents={progressContents}
          progressActive={transfer.status}
        />
      )}
      <TransferStatusUpdate
        transfer={transfer}
        updateDialogStatus={updateDialogStatus}
        setUpdateDialogStatus={setUpdateDialogStatus}
        setSelectedTransfer={setSelectedTransfer}
        setTransfers={setTransfers}
      />
      <UpdateTransfer
        transfer={transfer}
        editDialogStatus={editDialogStatus}
        setEditDialogStatus={setEditDialogStatus}
        setSelectedTransfer={setSelectedTransfer}
        setTransfers={setTransfers}
      />
    </div>
  );
};

export default TransferDetails;
