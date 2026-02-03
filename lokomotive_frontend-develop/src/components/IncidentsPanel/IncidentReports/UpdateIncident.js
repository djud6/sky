import React, { useState } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { useTranslation } from "react-i18next";
import { Dialog } from "primereact/dialog";
import { Button } from "primereact/button";
import { getAuthHeader } from "../../../helpers/Authorization";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import GeneralRadio from "../../ShareComponents/GeneralRadio";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";

const UpdateIncident = ({
  incident,
  editDialogStatus,
  setEditDialogStatus,
  setSelectedIncident,
  setIncidents,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [equipmentFailure, setEquipmentFailure] = useState(incident.is_equipment_failure);
  const [isOperational, setIsOperational] = useState(incident.is_operational);
  const [isPreventable, setIsPreventable] = useState(incident.is_preventable);
  const [summary, setSummary] = useState(incident.accident_summary || "");

  const handleIncidentUpdate = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    const incidentReport = {
      accident_id: incident.accident_id,
      is_equipment_failure: equipmentFailure,
      evaluation_required: equipmentFailure,
      is_operational: isOperational,
      is_preventable: isPreventable,
      accident_summary: summary,
    };
    handleUpdateSubmit(incidentReport);
  };

  const handleUpdateSubmit = (data) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Accident/Update`, data, getAuthHeader())
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
    const response = await axios.post(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Accident/List/Date`,
      { start_date: "1900-01-01", end_date: "2099-12-31" },
      { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
    );

    const incidents = response.data;
    const selectedIncidents = incidents.filter(
      (incident) => incident.accident_id === data.accident_id
    );
    setSelectedIncident(selectedIncidents[0]);
    setIncidents(incidents);
    successAlert(t("incidentsDetails.update_success_text"));
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
          onClick={handleIncidentUpdate}
          disabled={!summary}
          autoFocus
        />
      </div>
    );
  };

  return (
    <Dialog
      className="custom-main-dialog"
      header={t("incidentsDetails.edit_incident_header")}
      visible={editDialogStatus}
      onHide={() => setEditDialogStatus(false)}
      style={{ width: "50vw" }}
      breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
      footer={renderFooter}
    >
      <div className="p-field">
        <GeneralRadio
          value={equipmentFailure}
          onChange={setEquipmentFailure}
          name={"equipmentFailureRadio"}
          labels={[t("reportIncidentPanel.equipment_failure_radio_labels")]}
        />
      </div>
      <div className="p-field">
        <GeneralRadio
          value={isOperational}
          onChange={setIsOperational}
          name={"isOpRadio"}
          labels={[t("reportIncidentPanel.incident_report_operational_labels")]}
        />
      </div>
      <div className="p-field">
        <GeneralRadio
          value={isPreventable}
          onChange={setIsPreventable}
          name={"isPreventableRadio"}
          labels={[
            t("reportIncidentPanel.incident_report_equipment_required_labels"),
            t("reportIncidentPanel.preventable"),
            t("reportIncidentPanel.non_preventable"),
          ]}
        />
      </div>
      <div className="p-field">
        <label>{t("reportIncidentPanel.incident_summary")}</label>
        <CustomTextArea rows={5} value={summary} onChange={setSummary} required leftStatus />
      </div>
    </Dialog>
  );
};

export default UpdateIncident;
