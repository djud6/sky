import React, { useState, useEffect } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import DatePicker from "../../ShareComponents/DatePicker";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import CustomInputNumber from "../../ShareComponents/CustomInputNumber";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";
import "../../../styles/ShareComponents/GeneralRadio.scss";

const UpdateMaintenance = ({
  maintenance,
  editDialogStatus,
  setEditDialogStatus,
  setSelectedMaintenance,
  setMaintenances,
  maintenanceStatus,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [pickupDate, setPickupDate] = useState(
    maintenance.available_pickup_date ? new Date(maintenance.available_pickup_date) : null
  );
  const [requestedDeliveryDate, setRequestedDeliveryDate] = useState(
    maintenance.requested_delivery_date ? new Date(maintenance.requested_delivery_date) : null
  );
  const [typesDataReady, setTypesDataReady] = useState(false);
  const [maintenanceTypes, setMaintenanceTypes] = useState([]);
  const [maintenanceType, setMaintenanceType] = useState(null);
  const [defaultMaintenanceType, setDefaultMaintenanceType] = useState(null);
  const [estimatedCost, setEstimatedCost] = useState(
    maintenance.estimatedCost ? maintenance.estimatedCost : null
  );
  const isExternalVendor =
    maintenance.vendor_email &&
    !["", "NA"].includes(maintenance.vendor_email) &&
    !maintenance.potential_vendor_ids &&
    !maintenance.assigned_vendor
      ? true
      : false;

  useEffect(() => {
    if (editDialogStatus) {
      setTypesDataReady(false);
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Inspection/List`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          setMaintenanceTypes(response.data);
          setTypesDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
  }, [editDialogStatus]);

  useEffect(() => {
    setPickupDate(
      maintenance.available_pickup_date ? new Date(maintenance.available_pickup_date) : null
    );
    setRequestedDeliveryDate(
      maintenance.requested_delivery_date ? new Date(maintenance.requested_delivery_date) : null
    );

    if (typesDataReady) {
      let tempData = maintenanceTypes.find(
        (v) => v.inspection_name === maintenance.inspection_type
      );
      let reformatMaintenance = {
        name: tempData.inspection_name,
        code: tempData.id,
      };
      setMaintenanceType(tempData);
      setDefaultMaintenanceType(reformatMaintenance);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [maintenance, typesDataReady]);

  const handleMaintenanceUpdate = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let maintenanceData = {
      maintenance_id: maintenance.maintenance_id,
      inspection_type_id: maintenanceType.id,
      ...(["waiting for vendor", "awaiting approval", "approved"].includes(
        maintenance.status.toLowerCase()
      )
        ? { available_pickup_date: pickupDate.toISOString() }
        : null),
      requested_delivery_date: requestedDeliveryDate.toISOString(),
      ...(isExternalVendor ? { estimated_cost: estimatedCost } : null),
    };

    handleUpdateSubmit(maintenanceData);
  };

  const handleUpdateSubmit = (data) => {
    loadingAlert();

    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Update`, data, getAuthHeader())
      .then((res) => {
        setEditDialogStatus(false);
        refreshData(data);
        successAlert();
      })
      .catch((error) => {
        ConsoleHelper(error);
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  const refreshData = async (data) => {
    const cancelTokenSource = axios.CancelToken.source();
    let requestURL;
    if (maintenanceStatus === "Outstanding") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/List`;
    } else if (maintenanceStatus === "Completed") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Completed/List`;
    } else if (maintenanceStatus === "search") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/VIN/${maintenance.VIN}`;
    }

    if (requestURL) {
      let response = await axios.get(requestURL, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });

      const maintenances = response.data;
      let selectedMaintenance;
      for (let i in maintenances) {
        if (maintenances[i].maintenance_id === data.maintenance_id) {
          selectedMaintenance = maintenances[i];
        }

        if (maintenances[i].in_house) {
          maintenances[i].vendor_name = "In-house Maintenance";
        } else if (!maintenances[i].in_house && !maintenances[i].vendor_name) {
          if (maintenances[i].vendor_email && !["", "NA"].includes(maintenances[i].vendor_email)) {
            maintenances[i].vendor_name = maintenances[i].vendor_email;
          }
        }
      }

      setSelectedMaintenance(selectedMaintenance);
      setMaintenances(maintenances);
      successAlert(t("maintenanceDetails.success_alert_text"));
      dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
    }
  };

  const selectMaintenanceType = (id) => {
    let selected = maintenanceTypes.find((v) => v.id === parseInt(id));
    setMaintenanceType(selected);
  };

  const onDialogStatus = (status) => {
    setEditDialogStatus(status);
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label={t("general.cancel")}
          icon="pi pi-times"
          onClick={() => onDialogStatus(false)}
          className="p-button-text"
        />
        <Button
          label={t("general.submit")}
          icon="pi pi-check"
          onClick={handleMaintenanceUpdate}
          disabled={
            (["waiting for vendor", "awaiting approval", "approved"].includes(
              maintenance.status.toLowerCase()
            ) &&
              !pickupDate) ||
            !typesDataReady ||
            !requestedDeliveryDate ||
            (isExternalVendor && estimatedCost === null)
          }
          autoFocus
        />
      </div>
    );
  };

  return (
    <Dialog
      className="custom-main-dialog"
      header={t("maintenanceDetails.edit_maintenance_header")}
      visible={editDialogStatus}
      onHide={() => onDialogStatus(false)}
      style={{ width: "50vw" }}
      breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
      footer={renderFooter}
    >
      <div className="p-field">
        <label>{t("maintenanceSchedulePanel.maintenance_type_label")}</label>
        <FormDropdown
          onChange={selectMaintenanceType}
          options={
            maintenanceTypes &&
            maintenanceTypes.map((maintenanceTypeItem) => ({
              name: maintenanceTypeItem.inspection_name,
              code: maintenanceTypeItem.id,
            }))
          }
          defaultValue={defaultMaintenanceType}
          loading={!typesDataReady}
          disabled={!typesDataReady}
          dataReady={typesDataReady}
          plain_dropdown
          leftStatus
        />
      </div>
      {isExternalVendor && (
        <div className="p-field">
          <label>{t("maintenanceSchedulePanel.estimated_cost_label")}</label>
          <CustomInputNumber
            value={estimatedCost}
            onChange={setEstimatedCost}
            className="w-100"
            mode="decimal"
            min={0}
            minFractionDigits={2}
            maxFractionDigits={2}
            max={2147483646}
            leftStatus
          />
        </div>
      )}
      {["waiting for vendor", "awaiting approval", "approved"].includes(
        maintenance.status.toLowerCase()
      ) && (
        <div className="p-field">
          <label>
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
          </label>
          <div className="p-fluid p-grid p-formgrid">
            <div className="p-col-12">
              <DatePicker
                onChange={(e) => {
                  setPickupDate(e);
                  if (requestedDeliveryDate && Date.parse(e) > Date.parse(requestedDeliveryDate)) {
                    setRequestedDeliveryDate(null);
                  }
                }}
                initialDate={pickupDate}
                minDate={new Date()}
                leftStatus
              />
            </div>
          </div>
        </div>
      )}
      <div className="p-field">
        <label>
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
        </label>
        <div className="p-fluid p-grid p-formgrid">
          <div className="p-col-12">
            <DatePicker
              onChange={setRequestedDeliveryDate}
              initialDate={requestedDeliveryDate}
              minDate={pickupDate || new Date()}
              leftStatus
            />
          </div>
        </div>
      </div>
    </Dialog>
  );
};

export default UpdateMaintenance;
