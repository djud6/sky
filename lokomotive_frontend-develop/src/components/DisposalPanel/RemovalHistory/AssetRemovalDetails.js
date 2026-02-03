import React, { useState } from "react";
import axios from "axios";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import { capitalize } from "../../../helpers/helperFunctions";
import UpdateDisposal from "./UpdateDisposal";
import DisposalStatusUpdate from "./DisposalStatusUpdate";
import DetailsView from "../../ShareComponents/DetailView/DetailsView";
import LoadingAnimation from "../../ShareComponents/LoadingAnimation";
import DetailsViewMobile from "../../ShareComponents/DetailView/DetailsViewMobile";
import { generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import "../../../styles/helpers/button4.scss";

const AssetRemovalDetails = ({
  asset,
  setDataReady,
  setSelectedAsset,
  setMobileDetails,
  setRemovalData,
  disableButtons,
  disableMobileVersion,
  detailsReady,
}) => {
  const { t } = useTranslation();
  const [completeDialog, setCompleteDialog] = useState(false);
  const [editDialogStatus, setEditDialogStatus] = useState(false);
  const [refurbishDeets, setRefurbishDeets] = useState(null);
  const [dataPending, setdataPending] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const progressSteps = [
    t("requestProgress.waiting_for_vendor"),
    t("requestProgress.awaiting_approval"),
    t("requestProgress.approved"),
    t("requestProgress.in_transit_to_vendor"),
    t("requestProgress.at_vendor"),
    t("requestProgress.in_progress"),
    t("requestProgress.complete"),
  ];
  const progressContents = [
    t("requestProgress.waiting_for_vendor_content"),
    t("requestProgress.awaiting_approval_content"),
    t("requestProgress.approved_content"),
    t("requestProgress.in_transit_to_vendor_content_" + Boolean(asset.vendor_transport_to_vendor)),
    t("requestProgress.at_vendor_content"),
    t("requestProgress.in_progress_content"),
    t("requestProgress.complete_content"),
  ];

  const onBack = () => {
    setMobileDetails(false);
    setSelectedAsset(null);
  };

  const getRefurbishDetails = () => {
    if (!refurbishDeets) {
      setdataPending(true);
      axios
        .get(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Get/Details/WorkOrder/${asset.refurbish_work_order}`,
          getAuthHeader()
        )
        .then((res) => {
          setRefurbishDeets(res.data);
          setdataPending(false);
        })
        .catch((error) => {
          generalErrorAlert(error.customErrorMsg);
          setdataPending(false);
          ConsoleHelper(error);
        });
    }
  };

  let detailViewTitles = [
    t("general.id"),
    t("general.status"),
    t("general.asset_type"),
    t("fleetPanel.manufacturer_label"),
    t("general.model_number"),
    t("removalDetails.disposal_reason"),
    t("removalDetails.refurbish_required"),
    t("removalDetails.interior_condition"),
    t("removalDetails.exterior_condition"),
    t("general.estimated_cost"),
    ...(!["complete", "cancelled", "denied"].includes(asset.status?.toLowerCase())
      ? [
          <React.Fragment>
            {asset.vendor_transport_to_vendor
              ? t("general.available_pickup_date")
              : t("general.client_dropoff_date")}
            <Tooltip
              label="transport_to_vendor"
              description={t(
                asset.vendor_transport_to_vendor
                  ? "general.transport_to_vendor_pickup"
                  : "general.transport_to_vendor_dropoff",
                { request_type: "disposal" }
              )}
            />
          </React.Fragment>,
        ]
      : []),
    t("general.created_by"),
    t("general.modified_by"),
    t("general.date_created"),
    t("general.date_updated"),
  ];

  let detailViewValues = [
    asset.custom_id,
    capitalize(asset.status),
    asset.asset_type,
    asset.manufacturer || t("general.not_applicable"),
    asset.model_number || t("general.not_applicable"),
    capitalize(asset.disposal_reason),
    asset.refurbished ? t("general.yes") : t("general.no"),
    capitalize(asset.interior_condition),
    capitalize(asset.exterior_condition),
    asset.estimated_cost !== null ? asset.estimated_cost.toFixed(2) : t("general.not_applicable"),
    ...(!["complete", "cancelled", "denied"].includes(asset.status?.toLowerCase())
      ? moment(asset.available_pickup_date).isValid()
        ? [moment(asset.available_pickup_date).format("YYYY-MM-DD")]
        : [t("general.not_applicable")]
      : []),
    asset.created_by || t("general.not_applicable"),
    asset.modified_by || t("general.not_applicable"),
    moment(asset.date_created).format("YYYY-MM-DD") || t("general.not_applicable"),
    moment(asset.date_modified).format("YYYY-MM-DD") || t("general.not_applicable"),
  ];

  const refurbishDetails = (
    <React.Fragment>
      {asset.refurbish_work_order && (
        <div
          className={`add-descr-section p-d-flex p-flex-column ${isMobile ? "main-details" : ""}`}
        >
          {isMobile && <hr />}
          <div className="p-d-flex p-jc-between">
            <span className="title">{t("removalDetails.refurbish_id")}</span>
            <span className="value clickable-id" onClick={() => getRefurbishDetails()}>
              {asset.refurbish_work_order}
            </span>
          </div>
          {refurbishDeets ? (
            <div className="p-mt-2 p-d-flex p-flex-column">
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.status")}:`}</span>
                <span className="sub-value">{capitalize(refurbishDeets.status)}</span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">
                  {`${t("repairRequestPanel.urgent_repair_button")}:`}
                </span>
                <span className="sub-value">
                  {refurbishDeets.is_urgent ? t("general.yes") : t("general.no")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.available_pickup_date")}:`}</span>
                <span className="sub-value">
                  {moment(refurbishDeets.available_pickup_date).format("YYYY-MM-DD")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.requested_delivery_date")}:`}</span>
                <span className="sub-value">
                  {moment(refurbishDeets.requested_delivery_date).format("YYYY-MM-DD")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.date_created")}:`}</span>
                <span className="sub-value">
                  {moment(refurbishDeets.date_created).format("YYYY-MM-DD")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.created_by")}:`}</span>
                <span className="sub-value">{refurbishDeets.created_by}</span>
              </div>
              <div className="p-d-flex p-flex-column">
                <span className="sub-title">
                  {`${t("repairRequestPanel.repair_description_label")}:`}
                </span>
                <span className="sub-value">
                  {refurbishDeets.description || t("general.not_applicable")}
                </span>
              </div>
            </div>
          ) : dataPending ? (
            <div className="p-mt-2">
              <LoadingAnimation height={"150px"} />
            </div>
          ) : null}
          {!isMobile && <hr />}
        </div>
      )}
    </React.Fragment>
  );

  return (
    <React.Fragment>
      {isMobile && !disableMobileVersion ? (
        <div className="p-mb-5">
          <div className="no-style-btn p-my-3">
            <Button
              label={t("general.back")}
              className="p-button-link"
              icon="pi pi-chevron-left"
              onClick={() => onBack()}
            />
          </div>
          <DetailsViewMobile
            header={t("general.header_vin", { vin: asset.VIN })}
            titles={detailViewTitles}
            values={detailViewValues}
            description={[
              t("removalDetails.ex_interior_details_title"),
              t("removalDetails.interior_details") +
                ": " +
                (asset.interior_condition_details || t("general.not_applicable")),
              t("removalDetails.exterior_details") +
                ": " +
                (asset.exterior_condition_details || t("general.not_applicable")),
            ]}
            files={asset.files}
            editBtn={
              asset.status?.toLowerCase() !== "complete"
                ? t("removalDetails.edit_removal_header")
                : ""
            }
            onEdit={() => setEditDialogStatus(true)}
            actionBtn1={
              !["complete", "denied", "cancelled"].includes(asset.status?.toLowerCase())
                ? [t("general.mark_as_complete"), "pi-check-circle", "detail-action-color-1"]
                : ""
            }
            onActionBtn1={() => setCompleteDialog(true)}
            disabledBtn1={
              asset.vendor &&
              ["waiting for vendor", "in transit - to vendor", "at vendor"].includes(
                asset.status?.toLowerCase()
              )
            }
            progressSteps={progressSteps}
            progressContents={progressContents}
            progressActive={asset.status}
            additionalDescr={refurbishDetails}
          />
        </div>
      ) : (
        <DetailsView
          headers={[t("removalDetails.page_title"), t("general.header_vin", { vin: asset.VIN })]}
          titles={detailViewTitles}
          values={detailViewValues}
          description={[
            t("removalDetails.ex_interior_details_title"),
            t("removalDetails.interior_details") +
              ": " +
              (asset.interior_condition_details || t("general.not_applicable")),
            t("removalDetails.exterior_details") +
              ": " +
              (asset.exterior_condition_details || t("general.not_applicable")),
          ]}
          files={asset.files}
          onHideDialog={setSelectedAsset}
          editBtn={
            asset.status?.toLowerCase() !== "complete" && !disableButtons
              ? t("removalDetails.edit_removal_header")
              : ""
          }
          onEdit={() => setEditDialogStatus(true)}
          actionBtn1={
            !["complete", "denied", "cancelled"].includes(asset.status?.toLowerCase())
              ? [t("general.update_status"), "pi-check-circle", "detail-action-color-1"]
              : ""
          }
          onActionBtn1={() => setCompleteDialog(true)}
          disabledBtn1={
            asset.vendor &&
            ["waiting for vendor", "in transit - to vendor", "at vendor"].includes(
              asset.status?.toLowerCase()
            )
          }
          detailsReady={detailsReady}
          progressSteps={progressSteps}
          progressContents={progressContents}
          progressActive={asset.status}
          additionalDescr={refurbishDetails}
        />
      )}

      {/* Update disposal Dialog */}
      <UpdateDisposal
        asset={asset}
        editDialogStatus={editDialogStatus}
        setEditDialogStatus={setEditDialogStatus}
        setRemovalData={setRemovalData}
        setSelectedAsset={setSelectedAsset}
      />

      {/* Complete disposal Dialog */}
      <DisposalStatusUpdate
        disposal={asset}
        completeDialog={completeDialog}
        setCompleteDialog={setCompleteDialog}
        setRemovalData={setRemovalData}
        setSelectedAsset={setSelectedAsset}
        setDataReady={setDataReady}
      />
    </React.Fragment>
  );
};

export default AssetRemovalDetails;
