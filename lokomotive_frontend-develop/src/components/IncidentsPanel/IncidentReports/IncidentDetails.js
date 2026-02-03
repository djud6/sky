import React, { useState } from "react";
import moment from "moment";
import axios from "axios";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import UpdateIncident from "./UpdateIncident";
import DetailsView from "../../ShareComponents/DetailView/DetailsView";
import DetailsViewMobile from "../../ShareComponents/DetailView/DetailsViewMobile";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button4.scss";

const IncidentDetails = ({
  incident,
  setSelectedIncident,
  setMobileDetails,
  setIncidents,
  disableButtons,
  disableMobileVersion,
  detailsReady
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [editDialogStatus, setEditDialogStatus] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const onBack = () => {
    setMobileDetails(false);
    setSelectedIncident(null);
  };

  const onResolveIncident = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    loadingAlert();
    axios
      .post(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Accident/Set/Resolved/${incident.accident_id}`,
        "true",
        getAuthHeader()
      )
      .then((res) => {
        refreshData();
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  const refreshData = async () => {
    const cancelTokenSource = axios.CancelToken.source();
    const response = await axios.post(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Accident/List/Date`,
      { start_date: "1900-01-01", end_date: "2099-12-31" },
      { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
    );

    const incidents = response.data;
    const selectedIncidents = incidents.filter((i) => i.accident_id === incident.accident_id);
    setSelectedIncident(selectedIncidents[0]);
    setIncidents(incidents);
    successAlert(t("incidentsDetails.update_success_text"));
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
  };

  let detailViewTitles = [
    t("general.id"),
    t("general.status"),
    t("general.asset_type"),
    t("incidentsDetails.business_unit_label"),
    t("general.location"),
    t("incidentsDetails.incident_type_label"),
    t("incidentsDetails.equipment_failure"),
    t("incidentsDetails.asset_state"),
    t("incidentsDetails.returned_to_service_label"),
    t("general.created_by"),
    t("general.date_created"),
    t("general.modified_by"),
    t("general.date_updated"),
  ];
  let detailViewValues = [
    incident.custom_id,
    incident.is_resolved ? t("general.resolved") : t("general.unresolved"),
    incident.asset_type,
    incident.business_unit,
    incident.current_location || t("general.not_applicable"),
    incident.is_preventable
      ? t("incidentsDetails.preventable")
      : t("incidentsDetails.not_preventable"),
    incident.is_equipment_failure
      ? t("general.yes")
      : t("general.no"),
    incident.is_operational
      ? t("general.operational")
      : t("general.inoperational"),
    moment(incident.date_returned_to_service).isValid() ?
    moment(incident.date_returned_to_service).format("YYYY-MM-DD") : t("general.not_applicable"),
    incident.created_by || t("general.not_applicable"),
    moment(incident.date_created).format("YYYY-MM-DD") || t("general.not_applicable"),
    incident.modified_by || t("general.not_applicable"),
    moment(incident.date_modified).format("YYYY-MM-DD") || t("general.not_applicable"),
  ];

  return (
    <React.Fragment>
      {isMobile && !disableMobileVersion ? (
        <div className="p-my-3">
          <div className="no-style-btn p-my-3">
            <Button
              label={t("general.back")}
              className="p-button-link"
              icon="pi pi-chevron-left"
              onClick={() => onBack()}
            />
          </div>
          <DetailsViewMobile
            header={t("general.header_vin", { vin: incident.VIN })}
            titles={detailViewTitles}
            values={detailViewValues}
            description={[
              t("incidentsDetails.accident_summary"),
              incident.accident_summary || t("general.not_applicable"),
            ]}
            files={incident.files}
            editBtn={!incident.is_resolved && !disableButtons ? t("incidentsDetails.edit_incident_header") : ""}
            onEdit={() => setEditDialogStatus(true)}
            actionBtn1={
              !incident.is_resolved && !disableButtons
                ? [t("general.mark_as_resolved"), "pi-check-circle", "detail-action-color-1"]
                : ""
            }
            onActionBtn1={onResolveIncident}
          />
        </div>
      ) : (
        <DetailsView
          headers={[
            t("incidentsDetails.incident_details"),
            t("general.header_vin", { vin: incident.VIN }),
          ]}
          titles={detailViewTitles}
          values={detailViewValues}
          description={[
            t("incidentsDetails.accident_summary"),
            incident.accident_summary || t("general.not_applicable"),
          ]}
          files={incident.files}
          onHideDialog={setSelectedIncident}
          editBtn={!incident.is_resolved && !disableButtons ? t("incidentsDetails.edit_incident_header") : ""}
          onEdit={() => setEditDialogStatus(true)}
          actionBtn1={
            !incident.is_resolved && !disableButtons
              ? [t("general.mark_as_resolved"), "pi-check-circle", "detail-action-color-1"]
              : ""
          }
          onActionBtn1={onResolveIncident}
          detailsReady={detailsReady}
        />
      )}
      <UpdateIncident
        incident={incident}
        editDialogStatus={editDialogStatus}
        setEditDialogStatus={setEditDialogStatus}
        setSelectedIncident={setSelectedIncident}
        setIncidents={setIncidents}
      />
    </React.Fragment>
  );
};

export default IncidentDetails;
