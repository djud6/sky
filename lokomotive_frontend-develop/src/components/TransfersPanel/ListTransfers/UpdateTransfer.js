import React, { useState, useEffect } from "react";
import axios from "axios";
import { useDispatch, useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import * as Constants from "../../../constants";
import { capitalize } from "../../../helpers/helperFunctions";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import CustomInputNumber from "../../ShareComponents/CustomInputNumber";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";

const UpdateTransfer = ({
  transfer,
  editDialogStatus,
  setEditDialogStatus,
  setSelectedTransfer,
  setTransfers,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { listLocations } = useSelector((state) => state.apiCallData);
  const [defaultLocation, setDefaultLocation] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [justification, setJustification] = useState(transfer.justification);
  const [locDataReady, setLocDataReady] = useState(false);
  const [estimatedCost, setEstimatedCost] = useState(null);

  useEffect(() => {
    if (editDialogStatus) {
      setLocDataReady(false);
      setJustification(transfer.justification);
      let tempLocation = listLocations.find(
        (v) => v.location_name === transfer.destination_location
      );
      let reformatLocation = {
        name: tempLocation.location_name,
        code: tempLocation.location_id,
      };
      setDefaultLocation(reformatLocation);
      setSelectedLocation(tempLocation);
      setEstimatedCost(transfer.estimated_cost);
      setLocDataReady(true);
    }
    // eslint-disable-next-line
  }, [editDialogStatus]);

  const handleTransferUpdate = () => {
    let transferData = {
      transfer_id: transfer.asset_transfer_id,
      destination_location_id: selectedLocation.location_id,
      justification: justification,
      ...(transfer.approving_user && !["", "NA"].includes(transfer.approving_user)
        ? { estimated_cost: estimatedCost }
        : null),
    };

    handleUpdateSubmit(transferData);
  };

  const handleUpdateSubmit = (data) => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Transfer/Update`, data, getAuthHeader())
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
    const response = await axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Transfer/List`, {
      ...getAuthHeader(),
      cancelToken: cancelTokenSource.token,
    });

    const listTransfers = response.data.map((data) => {
      data.status = capitalize(data.status);
      return data;
    });
    const selectedTrans = listTransfers.filter((t) => t.asset_transfer_id === data.transfer_id);

    setSelectedTransfer(selectedTrans[0]);
    setTransfers(listTransfers);
    successAlert("msg", t("assetTransferPanel.update_success_text"));
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
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
          onClick={handleTransferUpdate}
          disabled={
            !justification ||
            !justification.trim() ||
            !locDataReady ||
            (transfer.approving_user &&
              !["", "NA"].includes(transfer.approving_user) &&
              estimatedCost === null)
          }
          autoFocus
        />
      </div>
    );
  };

  const selectLocation = (id) => {
    let selected = listLocations.find((v) => v.location_id === parseInt(id));
    setSelectedLocation(selected);
  };

  return (
    <Dialog
      className="custom-main-dialog"
      header={t("assetTransferPanel.edit_transfer_header")}
      visible={editDialogStatus}
      onHide={() => setEditDialogStatus(false)}
      style={{ width: "50vw" }}
      breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
      footer={renderFooter}
    >
      <div className="p-field">
        <label>{t("assetTransferPanel.transfer_location")}</label>
        <FormDropdown
          onChange={selectLocation}
          options={
            listLocations &&
            listLocations.map((location) => ({
              name: location.location_name,
              code: location.location_id,
            }))
          }
          defaultValue={defaultLocation}
          loading={!locDataReady}
          disabled={!locDataReady}
          dataReady={locDataReady}
          plain_dropdown
          leftStatus
          reset={"disabled"}
        />
      </div>
      {transfer.approving_user && !["", "NA"].includes(transfer.approving_user) && (
        <div className="p-field">
          <label>{t("assetTransferPanel.estimated_cost_label")}</label>
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
        <label>{t("assetTransferPanel.transfer_justification")}</label>
        <CustomTextArea
          className="w-100"
          rows={5}
          value={justification}
          required
          onChange={setJustification}
          leftStatus
        />
      </div>
    </Dialog>
  );
};

export default UpdateTransfer;
