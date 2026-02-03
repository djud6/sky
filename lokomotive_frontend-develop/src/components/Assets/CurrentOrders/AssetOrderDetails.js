import React, { useState } from "react";
import axios from "axios";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import UpdateAssetOrder from "./UpdateAssetOrder";
import OrderStatusUpdate from "./OrderStatusUpdate";
import DetailsView from "../../ShareComponents/DetailView/DetailsView";
import LoadingAnimation from "../../ShareComponents/LoadingAnimation";
import DetailsViewMobile from "../../ShareComponents/DetailView/DetailsViewMobile";
import { generalErrorAlert } from "../../ShareComponents/CommonAlert";
import { capitalize } from "../../../helpers/helperFunctions";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import "../../../styles/helpers/button4.scss";

const AssetOrderDetails = ({
  order,
  setSelectedOrder,
  setMobileDetails,
  setRequests,
  requestType,
  setDataReady,
}) => {
  const { t } = useTranslation();
  const [editDialogStatus, setEditDialogStatus] = useState(false);
  const [completedialogStatus, setCompletedialogStatus] = useState(false);
  const [tradeinDeets, setTradeinDeets] = useState(null);
  const [dataPending, setdataPending] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const progressSteps = [
    t("requestProgress.waiting_for_vendor"),
    t("requestProgress.awaiting_approval"),
    t("requestProgress.approved"),
    t("requestProgress.ordered"),
    t("requestProgress.built"),
    t("requestProgress.in_transit_to_client"),
    t("requestProgress.delivered"),
  ];
  const progressContents = [
    t("requestProgress.waiting_for_vendor_content"),
    t("requestProgress.awaiting_approval_content"),
    t("requestProgress.approved_content"),
    t("requestProgress.ordered_content"),
    t("requestProgress.built_content"),
    t("requestProgress.in_transit_to_client_content_" + Boolean(order.vendor_transport_to_client)),
    t("requestProgress.delivered_content"),
  ];

  const onBack = () => {
    setMobileDetails(false);
    setSelectedOrder(null);
  };

  const onOrderStatusUpdate = () => {
    setCompletedialogStatus(true);
  };

  const getTradeinDetails = () => {
    if (!tradeinDeets) {
      setdataPending(true);
      axios
        .get(
          `${Constants.ENDPOINT_PREFIX}/api/v1/AssetDisposal/Get/Details/ID/${order.disposal}`,
          getAuthHeader()
        )
        .then((res) => {
          setTradeinDeets(res.data);
          setdataPending(false);
        })
        .catch((error) => {
          generalErrorAlert(error.customErrorMsg);
          setdataPending(false);
          ConsoleHelper(error);
        });
    }
  };

  const detailViewTitles = [
    t("general.id"),
    t("general.status"),
    t("general.asset_type"),
    t("assetOrderDetails.business_unit_label"),
    t("assetOrderDetails.manufacturer_label"),
    t("assetOrderDetails.equipment_type_label"),
    t("general.estimated_cost"),
    ...(!["delivered", "cancelled", "denied"].includes(order.status?.toLowerCase())
      ? [
          <React.Fragment>
            {order.vendor_transport_to_client
              ? t("assetRequest.delivery_date_label")
              : t("assetRequest.pickup_date_label")}
            <Tooltip
              label="transport_to_client"
              description={t(
                order.vendor_transport_to_client
                  ? "general.transport_to_client_delivery"
                  : "general.transport_to_client_pickup",
                { request_type: "asset request" }
              )}
            />
          </React.Fragment>,
        ]
      : []),
    t("assetOrderDetails.justification_label"),
    t("general.vendor_email"),
    t("general.created_by"),
    t("general.modified_by"),
    t("general.date_created"),
    t("general.date_updated"),
  ];

  const detailViewValues = [
    order.custom_id,
    capitalize(order.status),
    order.asset_type,
    order.business_unit,
    order.manufacturer,
    order.model_number,
    order.estimated_cost !== null ? order.estimated_cost.toFixed(2) : t("general.not_applicable"),
    ...(!["delivered", "cancelled", "denied"].includes(order.status?.toLowerCase())
      ? moment(order.date_required).isValid()
        ? [moment(order.date_required).format("YYYY-MM-DD")]
        : [t("general.not_applicable")]
      : []),
    order.justification,
    order.vendor_email,
    order.created_by,
    order.modified_by || t("general.not_applicable"),
    moment(order.date_created).isValid()
      ? moment(order.date_created).format("YYYY-MM-DD")
      : t("general.not_applicable"),
    moment(order.date_updated).isValid()
      ? moment(order.date_updated).format("YYYY-MM-DD")
      : t("general.not_applicable"),
  ];

  const tradeinDetails = (
    <React.Fragment>
      {order.disposal_custom_id && (
        <div
          className={`p-d-flex p-flex-column ${isMobile ? "main-details" : "add-descr-section"}`}
        >
          {isMobile && <hr />}
          <div className="p-d-flex p-jc-between">
            <span>{t("assetOrderDetails.linked_tradein")}</span>
            <span className="value clickable-id" onClick={() => getTradeinDetails()}>
              {order.disposal_custom_id}
            </span>
          </div>
          {tradeinDeets ? (
            <div className="p-mt-2 p-d-flex p-flex-column">
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.status")}:`}</span>
                <span className="sub-value">{capitalize(tradeinDeets.status)}</span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("removalDetails.disposal_reason")}:`}</span>
                <span className="sub-value">{capitalize(tradeinDeets.disposal_reason)}</span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("removalDetails.refurbish_required")}:`}</span>
                <span className="sub-value">
                  {tradeinDeets.refurbished ? t("general.yes") : t("general.no")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("removalDetails.interior_condition")}:`}</span>
                <span className="sub-value">{capitalize(tradeinDeets.interior_condition)}</span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("removalDetails.exterior_condition")}:`}</span>
                <span className="sub-value">{capitalize(tradeinDeets.exterior_condition)}</span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.date_created")}:`}</span>
                <span className="sub-value">
                  {moment(tradeinDeets.date_created).format("YYYY-MM-DD")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.created_by")}:`}</span>
                <span className="sub-value">{tradeinDeets.created_by}</span>
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
            header={t("assetOrderDetails.header")}
            titles={detailViewTitles}
            values={detailViewValues}
            description={[
              t("assetOrderDetails.nonstandard_description_title"),
              order.nonstandard_description || t("general.not_applicable"),
            ]}
            editBtn={
              !["in transit - to client", "delivered", "cancelled", "denied"].includes(
                order.status?.toLowerCase()
              )
                ? t("assetRequest.edit_asset_request_header")
                : ""
            }
            onEdit={() => setEditDialogStatus(true)}
            actionBtn1={
              !["delivered", "cancelled", "denied"].includes(order.status?.toLowerCase())
                ? [t("general.update_status"), "pi-check-circle", "detail-action-color-1"]
                : ""
            }
            onActionBtn1={onOrderStatusUpdate}
            disabledBtn1={
              order.vendor &&
              ["waiting for vendor", "ordered", "built"].includes(order.status?.toLowerCase())
            }
            progressSteps={progressSteps}
            progressContents={progressContents}
            progressActive={order.status}
            additionalDescr={tradeinDetails}
          />
        </div>
      ) : (
        <DetailsView
          headers={[t("assetOrderDetails.header")]}
          titles={detailViewTitles}
          values={detailViewValues}
          description={[
            t("assetOrderDetails.nonstandard_description_title"),
            order.nonstandard_description || t("general.not_applicable"),
          ]}
          onHideDialog={setSelectedOrder}
          editBtn={
            !["in transit - to client", "delivered", "cancelled", "denied"].includes(
              order.status?.toLowerCase()
            )
              ? t("assetRequest.edit_asset_request_header")
              : ""
          }
          onEdit={() => setEditDialogStatus(true)}
          actionBtn1={
            !["delivered", "cancelled", "denied"].includes(order.status?.toLowerCase())
              ? [t("general.update_status"), "pi-check-circle", "detail-action-color-1"]
              : ""
          }
          onActionBtn1={onOrderStatusUpdate}
          disabledBtn1={
            order.vendor &&
            ["waiting for vendor", "ordered", "built"].includes(order.status?.toLowerCase())
          }
          progressSteps={progressSteps}
          progressContents={progressContents}
          progressActive={order.status}
          additionalDescr={tradeinDetails}
        />
      )}
      <UpdateAssetOrder
        request={order}
        editDialogStatus={editDialogStatus}
        setEditDialogStatus={setEditDialogStatus}
        setSelectedOrder={setSelectedOrder}
        setRequests={setRequests}
        requestType={requestType}
      />
      <OrderStatusUpdate
        request={order}
        dialogOpen={completedialogStatus}
        setDialogOpen={setCompletedialogStatus}
        setDataReady={setDataReady}
      />
    </React.Fragment>
  );
};

export default AssetOrderDetails;
