import React, { useState } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import DatePicker from "../../ShareComponents/DatePicker";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import CustomInputNumber from "../../ShareComponents/CustomInputNumber";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";

const UpdateRepair = ({
  repair,
  editDialogStatus,
  setEditDialogStatus,
  setSelectedRepair,
  setRepairRequests,
  category,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [pickupDate, setPickupDate] = useState(
    repair.available_pickup_date ? new Date(repair.available_pickup_date) : null
  );
  const [requestedDeliveryDate, setRequestedDeliveryDate] = useState(
    repair.requested_delivery_date ? new Date(repair.requested_delivery_date) : null
  );
  const [description, setDescription] = useState(repair.description);
  const [estimatedCost, setEstimatedCost] = useState(
    repair.estimatedCost ? repair.estimatedCost : null
  );
  const isExternalVendor =
    repair.vendor_email &&
    !["", "NA"].includes(repair.vendor_email) &&
    !repair.potential_vendor_ids &&
    !repair.vendor
      ? true
      : false;

  const handleRepairUpdate = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let repairData = {
      repair_id: repair.repair_id,
      ...(["waiting for vendor", "awaiting approval", "approved"].includes(
        repair.status.toLowerCase()
      )
        ? { available_pickup_date: pickupDate.toISOString() }
        : null),
      requested_delivery_date: requestedDeliveryDate.toISOString(),
      description: description,
      ...(isExternalVendor ? { estimated_cost: estimatedCost } : null),
    };

    handleUpdateSubmit(repairData);
  };

  const handleUpdateSubmit = (data) => {
    loadingAlert();

    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Update`, data, getAuthHeader())
      .then((res) => {
        setEditDialogStatus(false);
        refreshData(data);
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
    if (category === "inProgress") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/List`;
    } else if (category === "completed") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Complete/List`;
    }

    if (requestURL) {
      let response = await axios.get(requestURL, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });

      const repairs = response.data;
      let selectedRepair;
      if (category === "inProgress") {
        for (var i in repairs) {
          if (repairs[i].repair_id === data.repair_id) {
            selectedRepair = repairs[i];
          }
          if (repairs[i].is_urgent) repairs[i].is_urgent = "Yes";
          else repairs[i].is_urgent = "No";

          if (repairs[i].in_house) {
            repairs[i].vendor_name = "In-house Repair";
          } else if (!repairs[i].in_house && !repairs[i].vendor_name) {
            if (repairs[i].vendor_email && !["", "NA"].includes(repairs[i].vendor_email)) {
              repairs[i].vendor_name = repairs[i].vendor_email;
            }
          }
        }
      } else if (category === "completed") {
        for (var y in repairs) {
          if (repairs[y].repair_id === data.repair_id) {
            selectedRepair = repairs[y];
          }
          if (repairs[y].in_house) {
            repairs[y].vendor_name = "In-house Repair";
          } else if (!repairs[y].in_house && !repairs[y].vendor_name) {
            if (repairs[y].vendor_email && !["", "NA"].includes(repairs[y].vendor_email)) {
              repairs[y].vendor_name = repairs[y].vendor_email;
            }
          }
        }
      }

      setSelectedRepair(selectedRepair);
      setRepairRequests(repairs);
      successAlert(t("repairDetails.success_alert_text"));
      dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
    }
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label={t("general.cancel")}
          icon="pi pi-times"
          onClick={() => setEditDialogStatus(false)}
          className="p-button-text"
        />
        <Button
          label={t("general.submit")}
          icon="pi pi-check"
          onClick={handleRepairUpdate}
          disabled={
            (["waiting for vendor", "awaiting approval", "approved"].includes(
              repair.status.toLowerCase()
            ) &&
              !pickupDate) ||
            !requestedDeliveryDate ||
            !description ||
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
      header={t("repairDetails.edit_repair_header")}
      visible={editDialogStatus}
      onHide={() => setEditDialogStatus(false)}
      style={{ width: "50vw" }}
      breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
      footer={renderFooter}
    >
      <div className="p-field">
        <label>{t("repairRequestPanel.repair_description_label")}</label>
        <CustomTextArea
          className="w-100"
          rows={5}
          value={description}
          onChange={setDescription}
          required
          leftStatus
        />
      </div>
      {isExternalVendor && (
        <div className="p-field">
          <label>{t("repairRequestPanel.estimated_cost_label")}</label>
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
        repair.status.toLowerCase()
      ) && (
        <div className="p-field">
          <label>
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

export default UpdateRepair;
