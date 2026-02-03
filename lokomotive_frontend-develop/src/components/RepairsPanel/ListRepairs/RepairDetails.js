import React, { useState } from "react";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import UpdateRepair from "./UpdateRepair";
import RepairStatusUpdate from "./RepairStatusUpdate";
import UploadRepairFiles from "./UploadRepairFiles";
import { capitalize } from "../../../helpers/helperFunctions";
import DetailsView from "../../ShareComponents/DetailView/DetailsView";
import DetailsViewMobile from "../../ShareComponents/DetailView/DetailsViewMobile";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import "../../../styles/helpers/button4.scss";

const RepairDetails = ({
  repair,
  setSelectedRepair,
  setMobileDetails,
  setMoreDetails,
  setDetailsSection,
  setRepairRequests,
  setDataReady,
  category,
  disableButtons,
  disableMobileVersion,
  detailsReady,
}) => {
  const { t } = useTranslation();
  const [editDialogStatus, setEditDialogStatus] = useState(false);
  const [completeDialogStatus, setCompleteDialogStatus] = useState(false);
  const [uploadDialogStatus, setUploadDialogStatus] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const onBack = () => {
    setMobileDetails(false);
    setSelectedRepair(null);
  };

  let detailViewTitles = [
    t("general.id"),
    t("general.status"),
    ...(["complete", "in transit - to client"].includes(repair.status?.toLowerCase())
      ? [t("general.date_completed")]
      : []),
    t("general.asset_type"),
    t("general.division"),
    t("general.location"),
    ...(repair.mileage !== -1.0 ? [t("general.mileage")] : []),
    ...(repair.hours !== -1.0 ? [t("general.hours")] : []),
    t("general.vendor"),
    t("general.estimated_cost"),
    ...(!["delivered", "cancelled", "denied"].includes(repair.status?.toLowerCase())
      ? [
          <React.Fragment>
            {repair.vendor_transport_to_vendor
              ? t("general.available_pickup_date")
              : t("general.client_dropoff_date")}
            <Tooltip
              label="transport_to_vendor"
              description={t(
                repair.vendor_transport_to_vendor
                  ? "general.transport_to_vendor_pickup"
                  : "general.transport_to_vendor_dropoff",
                { request_type: "repair" }
              )}
            />
          </React.Fragment>,
          <React.Fragment>
            {repair.vendor_transport_to_client
              ? t("repairRequestPanel.requested_delivery_date_label")
              : t("repairRequestPanel.requested_pickup_date_label")}
            <Tooltip
              label="transport_to_client"
              description={t(
                repair.vendor_transport_to_client
                  ? "general.transport_to_client_delivery"
                  : "general.transport_to_client_pickup",
                { request_type: "repair" }
              )}
            />
          </React.Fragment>,
          t("general.estimated_delivery_date"),
        ]
      : []),
    t("general.created_by"),
    t("general.modified_by"),
    t("general.date_created"),
    t("general.date_updated"),
  ];

  let detailViewValues = [
    repair.work_order,
    capitalize(repair.status),
    ...(["complete", "in transit - to client"].includes(repair.status?.toLowerCase())
      ? [moment(repair.date_completed).format("YYYY-MM-DD")]
      : []),
    repair.asset_type,
    repair.business_unit,
    repair.current_location,
    ...(repair.mileage !== -1.0 ? [repair.mileage] : []),
    ...(repair.hours !== -1.0 ? [repair.hours] : []),
    repair.vendor_name || t("general.not_applicable"),
    repair.estimated_cost !== null ? repair.estimated_cost.toFixed(2) : t("general.not_applicable"),
    ...(!["delivered", "cancelled", "denied"].includes(repair.status?.toLowerCase())
      ? [
          moment(repair.available_pickup_date).isValid()
            ? moment(repair.available_pickup_date).format("YYYY-MM-DD")
            : t("general.not_applicable"),
          moment(repair.requested_delivery_date).isValid()
            ? moment(repair.requested_delivery_date).format("YYYY-MM-DD")
            : t("general.not_applicable"),
          moment(repair.estimated_delivery_date).isValid()
            ? moment(repair.estimated_delivery_date).format("YYYY-MM-DD")
            : t("general.not_applicable"),
        ]
      : []),
    repair.created_by || t("general.not_applicable"),
    repair.modified_by || t("general.not_applicable"),
    moment(repair.date_created).isValid()
      ? moment(repair.date_created).format("YYYY-MM-DD")
      : t("general.not_applicable"),
    moment(repair.date_modified).isValid()
      ? moment(repair.date_modified).format("YYYY-MM-DD")
      : t("general.not_applicable"),
  ];

  return (
    <React.Fragment>
      {isMobile && !disableMobileVersion ? (
        /* Mobile Details View */
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
            header={t("general.header_vin", { vin: repair.VIN })}
            titles={detailViewTitles}
            values={detailViewValues}
            files={repair.files}
            description={[
              `${t("repairRequestPanel.repair_description_label")}:`,
              repair.description || t("general.not_applicable"),
            ]}
            editBtn={
              !["complete", "in transit - to client", "delivered"].includes(
                repair.status?.toLowerCase()
              ) && !disableButtons
                ? t("repairDetails.edit_repair_header")
                : ""
            }
            onEdit={() => setEditDialogStatus(true)}
            actionBtn1={
              !["in transit - to client", "delivered", "denied", "cancelled"].includes(
                repair.status?.toLowerCase()
              ) && !disableButtons
                ? [t("general.update_status"), "pi-check-circle", "detail-action-color-1"]
                : repair.status === "in transit - to client" && !disableButtons
                ? [t("general.mark_as_delivered"), "pi-check-circle", "detail-action-color-1"]
                : ""
            }
            onActionBtn1={() => setCompleteDialogStatus(true)}
            disabledBtn1={
              repair.vendor &&
              !repair.in_house &&
              ["waiting for vendor", "in transit - to vendor", "at vendor", "complete"].includes(
                repair.status?.toLowerCase()
              )
            }
            actionBtn2={
              !disableButtons &&
              repair.status !== "awaiting approval" && [
                t("documentTab.upload_document"),
                "pi-cloud-upload",
                "detail-action-color-2",
              ]
            }
            onActionBtn2={() => setUploadDialogStatus(true)}
            enableMore={!disableButtons && setMoreDetails}
            detailsSection={[
              t("requestProgress.tab_title"),
              t("general.issue"),
              t("general.warranty"),
              t("general.parts_and_cost"),
            ]}
            setMoreDetails={setMoreDetails}
            setDetailsSection={setDetailsSection}
          />
        </div>
      ) : (
        /* Desktop Details View */
        <DetailsView
          headers={[
            t("repairDetails.repair_details"),
            t("general.header_vin", { vin: repair.VIN }),
          ]}
          titles={detailViewTitles}
          values={detailViewValues}
          files={repair.files}
          description={[
            `${t("repairRequestPanel.repair_description_label")}:`,
            repair.description || t("general.not_applicable"),
          ]}
          onHideDialog={setSelectedRepair}
          editBtn={
            !["complete", "in transit - to client", "delivered"].includes(
              repair.status?.toLowerCase()
            ) && !disableButtons
              ? t("repairDetails.edit_repair_header")
              : ""
          }
          onEdit={() => setEditDialogStatus(true)}
          actionBtn1={
            !["in transit - to client", "delivered", "denied", "cancelled"].includes(
              repair.status?.toLowerCase()
            ) && !disableButtons
              ? [t("general.update_status"), "pi-check-circle", "detail-action-color-1"]
              : repair.status === "in transit - to client" && !disableButtons
              ? [t("general.mark_as_delivered"), "pi-check-circle", "detail-action-color-1"]
              : ""
          }
          onActionBtn1={() => setCompleteDialogStatus(true)}
          disabledBtn1={
            repair.vendor &&
            !repair.in_house &&
            ["waiting for vendor", "in transit - to vendor", "at vendor", "complete"].includes(
              repair.status?.toLowerCase()
            )
          }
          actionBtn2={
            !disableButtons &&
            repair.status !== "awaiting approval" && [
              t("documentTab.upload_document"),
              "pi-cloud-upload",
              "detail-action-color-2",
            ]
          }
          onActionBtn2={() => setUploadDialogStatus(true)}
          enableMore={!disableButtons}
          setMoreDetails={() => setMoreDetails(true)}
          detailsReady={detailsReady}
        />
      )}
      <UpdateRepair
        repair={repair}
        editDialogStatus={editDialogStatus}
        setEditDialogStatus={setEditDialogStatus}
        setSelectedRepair={setSelectedRepair}
        setRepairRequests={setRepairRequests}
        category={category}
      />
      <RepairStatusUpdate
        repair={repair}
        completeDialogStatus={completeDialogStatus}
        setCompleteDialogStatus={setCompleteDialogStatus}
        setSelectedRepair={setSelectedRepair}
        setRepairRequests={setRepairRequests}
        setDataReady={setDataReady}
        category={category}
      />
      <UploadRepairFiles
        repair={repair}
        uploadDialogStatus={uploadDialogStatus}
        setUploadDialogStatus={setUploadDialogStatus}
        setSelectedRepair={setSelectedRepair}
        setRepairRequests={setRepairRequests}
        category={category}
      />
    </React.Fragment>
  );
};

export default RepairDetails;
