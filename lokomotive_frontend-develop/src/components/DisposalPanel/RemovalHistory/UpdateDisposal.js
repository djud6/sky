import React, { useEffect, useState } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import CustomInputNumber from "../../ShareComponents/CustomInputNumber";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import DatePicker from "../../ShareComponents/DatePicker";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import { capitalize } from "../../../helpers/helperFunctions";
import "../../../styles/dialogStyles.scss";

const UpdateDisposal = ({
  asset,
  editDialogStatus,
  setEditDialogStatus,
  setRemovalData,
  setSelectedAsset,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [preDataReady, setPreDataReady] = useState(false);
  const [interiorCond, setInteriorCond] = useState(null);
  const [interiorDets, setInteriorDets] = useState(null);
  const [exteriorCond, setExteriorCond] = useState(null);
  const [exteriorDets, setExteriorDets] = useState(null);
  const [reason, setReason] = useState(null);
  const [replaceReason, setReplaceReason] = useState(null);
  const [disposalPickupDate, setDisposalPickupDate] = useState(null);
  const [estimatedCost, setEstimatedCost] = useState(null);
  const isExternalVendor =
    asset.primary_vendor_email &&
    !["", "NA", "not applicable"].includes(asset.primary_vendor_email) &&
    !asset.potential_vendor_ids &&
    !asset.vendor
      ? true
      : false;

  const conditions = [
    { name: t("removalPanel.condition_poor"), code: "P" },
    { name: t("removalPanel.condition_avg"), code: "A" },
    { name: t("removalPanel.condition_good"), code: "G" },
    { name: t("removalPanel.condition_na"), code: "N" },
  ];
  const disposalReasons = [
    { name: t("removalPanel.being_replaced"), code: "B" },
    { name: t("removalPanel.operational_change"), code: "O" },
    { name: t("removalPanel.location_closing"), code: "L" },
    { name: t("removalPanel.no_longer_fit_for_purpose"), code: "N" },
  ];
  const replacementResaons = [
    { name: t("removalPanel.end_of_useful_life"), code: "N" },
    { name: t("removalPanel.accident"), code: "A" },
    { name: t("removalPanel.equipment_failure"), code: "E" },
    { name: t("removalPanel.condition_na"), code: "NA" },
  ];

  useEffect(() => {
    setPreDataReady(false);
    let selectedIn = conditions.find((v) => v.name.toLowerCase() === asset.interior_condition);
    setInteriorCond(selectedIn);
    let selectedEx = conditions.find((v) => v.name.toLowerCase() === asset.exterior_condition);
    setExteriorCond(selectedEx);
    let selectedReason = disposalReasons.find(
      (v) => v.name.toLowerCase() === asset.disposal_reason
    );
    setReason(selectedReason);
    let selectedReplaceReason = replacementResaons.find(
      (v) => v.name.toLowerCase() === asset.replacement_reason
    );
    setReplaceReason(selectedReplaceReason);
    setInteriorDets(asset.interior_condition_details);
    setExteriorDets(asset.exterior_condition_details);
    setDisposalPickupDate(
      asset.available_pickup_date ? new Date(asset.available_pickup_date) : null
    );
    setEstimatedCost(asset.estimated_cost);

    setPreDataReady(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [asset]);

  const handleDisposalUpdate = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let disposalData = {
      disposal_id: asset.id,
      interior_condition: interiorCond.name.toLowerCase(),
      interior_condition_details: interiorDets,
      exterior_condition: exteriorCond.name.toLowerCase(),
      exterior_condition_details: exteriorDets,
      disposal_reason: reason.name.toLowerCase(),
      ...(reason.name === t("removalPanel.being_replaced") && {
        replacement_reason: replaceReason.name.toLowerCase(),
      }),
      ...(disposalPickupDate ? {available_pickup_date: disposalPickupDate.toISOString()} : null),
      ...(isExternalVendor ? { estimated_cost: estimatedCost } : null),
    };
    handleUpdateSubmit(disposalData);
  };

  const handleUpdateSubmit = (data) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetDisposal/Update`, data, getAuthHeader())
      .then(async (res) => {
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
    const response = await axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetDisposal/List`, {
      ...getAuthHeader(),
      cancelToken: cancelTokenSource.token,
    });
    const removalData = response.data;
    let selectedRemoval;
    removalData.forEach((disposal, index) => {
      if (disposal.id === data.disposal_id) {
        selectedRemoval = disposal;
      }
      return (removalData[index].disposal_type = capitalize(disposal.disposal_type));
    });

    setRemovalData(removalData);
    setSelectedAsset(selectedRemoval);
    successAlert("msg", t("removalDetails.disposal_update_success"));
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
  };

  const selectInteriorCondition = (code) => {
    let selected = conditions.find((v) => v.code === code);
    setInteriorCond(selected);
  };

  const selectExteriorCondition = (code) => {
    let selected = conditions.find((v) => v.code === code);
    setExteriorCond(selected);
  };

  const selectReason = (code) => {
    let selected = disposalReasons.find((v) => v.code === code);
    setReason(selected);
  };

  const selectReplaceReason = (code) => {
    let selected = replacementResaons.find((v) => v.code === code);
    setReplaceReason(selected);
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
          onClick={handleDisposalUpdate}
          disabled={
            !interiorCond ||
            !interiorDets ||
            !exteriorCond ||
            !exteriorDets ||
            !reason ||
            (reason.name === t("removalPanel.being_replaced") && !replaceReason) ||
            /*!disposalPickupDate ||*/
            (isExternalVendor && estimatedCost === null)
          }
          autoFocus
        />
      </div>
    );
  };

  return (
    <div>
      <Dialog
        className="custom-main-dialog"
        header={t("removalDetails.edit_removal_header")}
        visible={editDialogStatus}
        onHide={() => setEditDialogStatus(false)}
        style={{ width: "50vw" }}
        breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
        footer={renderFooter}
      >
        {isExternalVendor && (
          <div className="p-field">
            <label>{t("removalPanel.estimated_cost_label")}</label>
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
        <div className="p-field">
          <label>{t("removalPanel.interior_condition_of_the_asset")}</label>
          <FormDropdown
            reset={"disabled"}
            onChange={selectInteriorCondition}
            options={conditions}
            defaultValue={interiorCond}
            loading={!preDataReady}
            disabled={!preDataReady}
            dataReady={preDataReady}
            plain_dropdown
            leftStatus
          />
        </div>
        <div className="p-field">
          <label>{t("removalPanel.interior_condition_details")}</label>
          <CustomTextArea
            className="w-100"
            rows={3}
            value={interiorDets}
            onChange={setInteriorDets}
            required
            leftStatus
          />
        </div>
        <div className="p-field">
          <label>{t("removalPanel.exterior_condition_of_the_asset")}</label>
          <FormDropdown
            reset={"disabled"}
            onChange={selectExteriorCondition}
            options={conditions}
            defaultValue={exteriorCond}
            loading={!preDataReady}
            disabled={!preDataReady}
            dataReady={preDataReady}
            plain_dropdown
            leftStatus
          />
        </div>
        <div className="p-field">
          <label>{t("removalPanel.exterior_condition_details")}</label>
          <CustomTextArea
            className="w-100"
            rows={3}
            value={exteriorDets}
            onChange={setExteriorDets}
            required
            leftStatus
          />
        </div>
        <div className="p-field">
          <label>{t("removalPanel.reason_for_disposal")}</label>
          <FormDropdown
            reset={"disabled"}
            onChange={selectReason}
            options={disposalReasons}
            defaultValue={reason}
            loading={!preDataReady}
            disabled={!preDataReady}
            dataReady={preDataReady}
            plain_dropdown
            leftStatus
          />
        </div>
        {reason
          ? reason.name === t("removalPanel.being_replaced") && (
              <div className="p-field">
                <label>{t("removalPanel.reason_for_replacement")}</label>
                <FormDropdown
                  reset={"disabled"}
                  onChange={selectReplaceReason}
                  options={replacementResaons}
                  defaultValue={replaceReason}
                  loading={!preDataReady}
                  disabled={!preDataReady}
                  dataReady={preDataReady}
                  plain_dropdown
                  leftStatus
                />
              </div>
            )
          : null}
        {["waiting for vendor", "awaiting approval", "approved"].includes(
          asset.status.toLowerCase()
        ) && (
          <div className="p-field">
            <label>
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
            </label>
            <DatePicker
              onChange={setDisposalPickupDate}
              initialDate={disposalPickupDate}
              minDate={new Date()}
              leftStatus
            />
          </div>
        )}
      </Dialog>
    </div>
  );
};

export default UpdateDisposal;
