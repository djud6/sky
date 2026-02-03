import React, { useState } from "react";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import UpdateMaintenance from "./UpdateMaintenance";
import MaintenanceStatusUpdate from "./MaintenanceStatusUpdate";
import UploadMaintenanceFiles from "./UploadMaintenanceFiles";
import { capitalize } from "../../../helpers/helperFunctions";
import DetailsView from "../../ShareComponents/DetailView/DetailsView";
import DetailsViewMobile from "../../ShareComponents/DetailView/DetailsViewMobile";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import "../../../styles/helpers/button4.scss";

const MaintenanceDetails = ({
  maintenance,
  setSelectedMaintenance,
  setMobileDetails,
  setMoreDetails,
  setDetailsSection,
  setMaintenances,
  setDataReady,
  maintenanceType,
  disableButtons,
  disableMobileVersion,
  detailsReady,
}) => {
  const { t } = useTranslation();
  const [editDialogStatus, setEditDialogStatus] = useState(false);
  const [updateDialogStatus, setUpdateDialogStatus] = useState(false);
  const [uploadDialogStatus, setUploadDialogStatus] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const onBack = () => {
    setMobileDetails(false);
    setSelectedMaintenance(null);
  };

  let detailViewTitles = [
    t("general.id"),
    t("general.inspection_type"),
    t("general.status"),
    ...(["complete", "in transit - to client", "delivered"].includes(
      maintenance.status?.toLowerCase()
    )
      ? [t("general.date_completed")]
      : []),
    t("general.asset_type"),
    t("general.location"),
    ...(maintenance.mileage !== -1.0 ? [t("general.mileage")] : []),
    ...(maintenance.hours !== -1.0 ? [t("general.hours")] : []),
    t("general.vendor"),
    t("general.estimated_cost"),
    ...(!["delivered", "cancelled", "denied"].includes(maintenance.status?.toLowerCase())
      ? [
          <React.Fragment>
            {maintenance.vendor_transport_to_vendor
              ? t("general.available_pickup_date")
              : t("general.client_dropoff_date")}
            <Tooltip
              label="transport_to_vendor"
              description={t(
                maintenance.vendor_transport_to_vendor
                  ? "general.transport_to_vendor_pickup"
                  : "general.transport_to_vendor_dropoff",
                { request_type: "maintenance" }
              )}
            />
          </React.Fragment>,
          <React.Fragment>
            {maintenance.vendor_transport_to_client
              ? t("maintenanceSchedulePanel.requested_date_label")
              : t("maintenanceSchedulePanel.pickup_date_label")}
            <Tooltip
              label="transport_to_client"
              description={t(
                maintenance.vendor_transport_to_client
                  ? "general.transport_to_client_delivery"
                  : "general.transport_to_client_pickup",
                { request_type: "maintenance" }
              )}
            />
          </React.Fragment>,
          t("general.estimated_delivery_date"),
          t("general.vendor_contacted_date"),
        ]
      : []),
    t("general.created_by"),
    t("general.modified_by"),
    t("general.date_created"),
    t("general.date_updated"),
  ];

  let detailViewValues = [
    maintenance.work_order,
    maintenance.inspection_type,
    capitalize(maintenance.status),
    ...(["complete", "in transit - to client", "delivered"].includes(
      maintenance.status?.toLowerCase()
    )
      ? [moment(maintenance.date_completed).format("YYYY-MM-DD")]
      : []),
    maintenance.asset_type,
    maintenance.current_location,
    ...(maintenance.mileage !== -1.0 ? [maintenance.mileage.toLocaleString()] : []),
    ...(maintenance.hours !== -1.0 ? [maintenance.hours.toLocaleString()] : []),
    maintenance.vendor_name || t("general.not_applicable"),
    maintenance.estimated_cost !== null
      ? maintenance.estimated_cost.toFixed(2)
      : t("general.not_applicable"),
    ...(!["delivered", "cancelled", "denied"].includes(maintenance.status?.toLowerCase())
      ? [
          moment(maintenance.available_pickup_date).isValid()
            ? moment(maintenance.available_pickup_date).format("YYYY-MM-DD")
            : t("general.not_applicable"),
          moment(maintenance.requested_delivery_date).isValid()
            ? moment(maintenance.requested_delivery_date).format("YYYY-MM-DD")
            : t("general.not_applicable"),
          moment(maintenance.estimated_delivery_date).isValid()
            ? moment(maintenance.estimated_delivery_date).format("YYYY-MM-DD")
            : t("general.not_applicable"),
          moment(maintenance.vendor_contacted_date).isValid()
            ? moment(maintenance.vendor_contacted_date).format("YYYY-MM-DD")
            : t("general.not_applicable"),
        ]
      : []),
    maintenance.created_by || t("general.not_applicable"),
    maintenance.modified_by || t("general.not_applicable"),
    moment(maintenance.date_created).isValid()
      ? moment(maintenance.date_created).format("YYYY-MM-DD")
      : t("general.not_applicable"),
    moment(maintenance.date_updated).isValid()
      ? moment(maintenance.date_updated).format("YYYY-MM-DD")
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
            header={t("general.header_vin", { vin: maintenance.VIN })}
            titles={detailViewTitles}
            values={detailViewValues}
            files={maintenance.files}
            editBtn={
              !["complete", "in transit - to client", "delivered","cancelled","denied"].includes(
                maintenance.status?.toLowerCase()
              ) && !disableButtons
                ? t("maintenanceDetails.edit_maintenance_header")
                : ""
            }
            onEdit={() => setEditDialogStatus(true)}
            actionBtn1={
              !["delivered", "denied", "cancelled"].includes(maintenance.status?.toLowerCase()) &&
              !disableButtons
                ? [t("general.update_status"), "pi-check-circle", "detail-action-color-1"]
                : ""
            }
            onActionBtn1={() => setUpdateDialogStatus(true)}
            disabledBtn1={
              maintenance.assigned_vendor &&
              !maintenance.in_house &&
              ["waiting for vendor", "in transit - to vendor", "at vendor", "complete"].includes(
                maintenance.status?.toLowerCase()
              )
            }
            actionBtn2={
              !["delivered", "denied", "cancelled"].includes(maintenance.status?.toLowerCase()) &&
              !disableButtons &&
              maintenance.status !== "awaiting approval" && [
                t("documentTab.upload_document"),
                "pi-cloud-upload",
                "detail-action-color-2",
              ]
            }
            onActionBtn2={() => setUploadDialogStatus(true)}
            enableMore={!disableButtons && setMoreDetails}
            detailsSection={[t("requestProgress.tab_title"), t("general.parts_and_cost")]}
            setMoreDetails={setMoreDetails}
            setDetailsSection={setDetailsSection}
          />
        </div>
      ) : (
        /* Desktop Details View */
        <DetailsView
          headers={[
            t("maintenanceDetails.maintenance_request_details"),
            t("general.header_vin", { vin: maintenance.VIN }),
          ]}
          titles={detailViewTitles}
          values={detailViewValues}
          files={maintenance.files}
          onHideDialog={setSelectedMaintenance}
          editBtn={
            !["complete", "in transit - to client", "delivered","cancelled","denied"].includes(
              maintenance.status?.toLowerCase()
            ) && !disableButtons
              ? t("maintenanceDetails.edit_maintenance_header")
              : ""
          }
          onEdit={() => setEditDialogStatus(true)}
          actionBtn1={
            !["delivered", "denied", "cancelled"].includes(maintenance.status?.toLowerCase()) &&
            !disableButtons
              ? [t("general.update_status"), "pi-check-circle", "detail-action-color-1"]
              : ""
          }
          onActionBtn1={() => setUpdateDialogStatus(true)}
          disabledBtn1={
            maintenance.assigned_vendor &&
            !maintenance.in_house &&
            ["waiting for vendor", "in transit - to vendor", "at vendor", "complete"].includes(
              maintenance.status?.toLowerCase()
            )
          }
          actionBtn2={
            !["delivered", "denied", "cancelled"].includes(maintenance.status?.toLowerCase()) &&
            !disableButtons &&
            maintenance.status !== "awaiting approval" && [
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
      <UpdateMaintenance
        maintenance={maintenance}
        editDialogStatus={editDialogStatus}
        setEditDialogStatus={setEditDialogStatus}
        setSelectedMaintenance={setSelectedMaintenance}
        setMaintenances={setMaintenances}
        maintenanceStatus={maintenanceType}
      />
      <MaintenanceStatusUpdate
        maintenance={maintenance}
        updateDialogStatus={updateDialogStatus}
        setUpdateDialogStatus={setUpdateDialogStatus}
        setSelectedMaintenance={setSelectedMaintenance}
        setMaintenances={setMaintenances}
        setDataReady={setDataReady}
        maintenanceStatus={maintenanceType}
      />
      <UploadMaintenanceFiles
        maintenance={maintenance}
        uploadDialogStatus={uploadDialogStatus}
        setUploadDialogStatus={setUploadDialogStatus}
        setSelectedMaintenance={setSelectedMaintenance}
        setMaintenances={setMaintenances}
        maintenanceStatus={maintenanceType}
      />
    </React.Fragment>
  );
};

export default MaintenanceDetails;
