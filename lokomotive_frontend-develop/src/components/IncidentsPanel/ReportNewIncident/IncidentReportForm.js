import React, { useEffect, useState } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import { useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Checkbox } from "primereact/checkbox";
import * as Constants from "../../../constants";
import { getAuthHeader, getRolePermissions } from "../../../helpers/Authorization";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import ChecklistItem from "../../ShareComponents/ChecklistItem";
import CardWidget from "../../ShareComponents/CardWidget";
import GeneralRadio from "../../ShareComponents/GeneralRadio";
import WarningMsg from "../../ShareComponents/WarningMsg";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import FileUploadInput from "../../ShareComponents/FileUploadInput";
import { isMobileDevice } from "../../../helpers/helperFunctions";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button1.scss";
import "../../../styles/tooltipStyles.scss";
import "../../../styles/helpers/fileInput.scss";
import "../../../styles/IncidentsPanel/reportNewIncident.scss";

const IncidentReportForm = ({ vehicle, title, sendIncidentReport }) => {
  const dispatch = useDispatch();
  const history = useHistory();
  const [incidentReportSubmitted, setIncidentReportSubmitted] = useState("");
  const [isWrittenOff, setIsWrittenOff] = useState("");
  const [disposalSubmitted, setDisposalSubmitted] = useState("");
  const [equipmentFailure, setEquipmentFailure] = useState("");
  const [isOperational, setIsOperational] = useState("");
  const [isPreventable, setIsPreventable] = useState("");
  const [summary, setSummary] = useState("");
  const [photos, setPhotos] = useState([]);
  const [photoNames, setPhotoNames] = useState([]);
  const [fileLoading, setFileLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [disableButton, setDisableButton] = useState(true);
  const [disposalReport, setDisposalReport] = useState([]);
  const [disposalReportChecked, setDisposalReportChecked] = useState(false);
  const [disposalDataReady, setDisposalDataReady] = useState(false);
  const [isOperator, setIsOperator] = useState(false);
  const [isSupervisor, setIsSupervisor] = useState(false);
  const { t } = useTranslation();
  const isMobile = isMobileDevice();

  useEffect(() => {
    const rolePermissions = getRolePermissions();
    if (rolePermissions.role.toLowerCase() === "operator") {
      setIsOperator(true);
    }

    if (rolePermissions.role.toLowerCase() === "supervisor") {
      setIsSupervisor(true);
    }
  }, []);

  // If vehicle changes, reset form
  useEffect(() => {
    setIncidentReportSubmitted("");
    setIsWrittenOff("");
    setDisposalSubmitted("");
    setEquipmentFailure("");
    setIsOperational("");
    setIsPreventable("");
    setSummary("");
    setPhotos([]);
    setPhotoNames([]);
    setSubmitted(false);
    setDisposalDataReady(false);
  }, [vehicle]);

  useEffect(() => {
    if (disposalSubmitted !== "" && disposalSubmitted) {
      setDisposalDataReady(false);
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetDisposal/Get/Writeoff/NoAccident`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          const disposalRequest = response.data.filter((disposal) => {
            return disposal.VIN === vehicle.VIN;
          });
          setDisposalReport(disposalRequest);
          setDisposalDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [disposalSubmitted]);

  useEffect(() => {
    if (isPreventable !== "" && summary !== "" && isOperational !== "") {
      setDisableButton(false);
    } else {
      setDisableButton(true);
    }
  }, [isPreventable, summary, isOperational]);

  const handleSubmit = (event) => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    event.preventDefault();
    let incidentReport = new FormData();
    incidentReport.append(
      "data",
      JSON.stringify({
        VIN: vehicle.VIN,
        accident_report_completed: incidentReportSubmitted,
        accident_summary: summary,
        is_equipment_failure: equipmentFailure,
        notification_ack: false,
        evaluation_required: equipmentFailure,
        is_preventable: isPreventable,
        is_operational: isOperational,
        ...(isWrittenOff && { disposal: disposalReport[0].id }),
      })
    );
    for (let i = 0; i < photos.length; i++) {
      incidentReport.append("files", photos[i]);
    }
    sendIncidentReport(incidentReport);
  };

  const handleTransferToDisposal = (e) => {
    e.preventDefault();
    history.push({
      pathname: "/asset-removal",
      state: {
        vehicle: vehicle,
      },
    });
  };

  if (!vehicle || submitted) return null;
  return (
    <div className="report-new-incident-form p-d-flex p-jc-center">
      <form onSubmit={handleSubmit} className={`w-100 ${isMobile ? "" : "p-mt-5"}`}>
        <div className="w-100">
          <h3 className="p-mb-3 text-white">{title}</h3>
          <ChecklistItem
            value={incidentReportSubmitted}
            onChange={setIncidentReportSubmitted}
            name={"incidentReportRadio"}
            labels={[t("reportIncidentPanel.incident_report_radio_labels")]}
            status={incidentReportSubmitted !== "" ? true : false}
          />
          {incidentReportSubmitted === false && (
            <WarningMsg message={t("reportIncidentPanel.incident_report_not_submit")} />
          )}
          {incidentReportSubmitted && (
            <ChecklistItem
              value={isWrittenOff}
              onChange={setIsWrittenOff}
              name={"isWrittenOffRadio"}
              labels={[t("reportIncidentPanel.is_written_off_labels")]}
              status={isWrittenOff !== "" ? true : false}
            />
          )}
          {incidentReportSubmitted && isWrittenOff && (
            <CardWidget status={disposalSubmitted !== "" ? true : false}>
              <GeneralRadio
                value={disposalSubmitted}
                onChange={setDisposalSubmitted}
                name={"disposalSubmittedRadio"}
                labels={[t("reportIncidentPanel.is_disposal_submitted")]}
                fontStyle="h5"
              />
              {disposalSubmitted !== "" ? (
                disposalSubmitted ? (
                  <div className="shadow-none p-mt-3 p-p-2 bg-light rounded">
                    {disposalDataReady ? (
                      disposalReport.length !== 0 ? (
                        <div className="p-d-flex p-flex-column p-p-2">
                          <div className="p-field-checkbox">
                            <Checkbox
                              inputId="checkdisposal"
                              checked={disposalReportChecked}
                              onChange={(e) => setDisposalReportChecked(e.checked)}
                            />
                            <label className="p-ml-2 p-mr-0 p-my-0 " htmlFor="checkdisposal">
                              {t("reportIncidentPanel.link_disposal")}
                            </label>
                          </div>
                          <h5>{t("reportIncidentPanel.disposal_found")}</h5>
                          <span>{`${t("general.vin")}: ${disposalReport[0].VIN}`}</span>
                          <span>
                            {`${t("general.created_by")}: ${disposalReport[0].created_by}`}
                          </span>
                          <span>
                            {`${t("general.date_created")}: ${disposalReport[0].date_created}`}
                          </span>
                        </div>
                      ) : (
                        <div className="p-d-flex p-flex-wrap p-ai-center disposal-warning-msg">
                          <div className="p-d-flex p-ai-center">
                            <i className="pi pi-exclamation-circle p-mr-3" />
                            <div>{t("reportIncidentPanel.no_disposal_found")}</div>
                          </div>
                          {!isOperator && !isSupervisor && (
                            <Button
                              label={t("reportIncidentPanel.disposal_btn")}
                              className="p-button-text"
                              onClick={handleTransferToDisposal}
                            />
                          )}
                        </div>
                      )
                    ) : (
                      <React.Fragment>
                        <div className="spinner-grow" role="status" style={{ color: "#8D249899" }}>
                          <span className="sr-only">{""}</span>
                        </div>
                        <div className="spinner-grow" role="status" style={{ color: "#8D249899" }}>
                          <span className="sr-only">{""}</span>
                        </div>
                        <div className="spinner-grow" role="status" style={{ color: "#8D249899" }}>
                          <span className="sr-only">{""}</span>
                        </div>
                      </React.Fragment>
                    )}
                  </div>
                ) : (
                  <div className="shadow-none p-mt-3 p-p-2 bg-light rounded p-d-flex p-flex-wrap">
                    <div className="p-d-flex p-flex-wrap p-ai-center disposal-warning-msg">
                      <div className="p-d-flex p-ai-center">
                        <i className="pi pi-exclamation-circle p-mr-3" />
                        <div>{t("reportIncidentPanel.require_submit_disposal_msg")}</div>
                      </div>
                      {!isOperator && !isSupervisor && (
                        <Button
                          label={t("reportIncidentPanel.disposal_btn")}
                          className="p-button-text"
                          onClick={handleTransferToDisposal}
                        />
                      )}
                    </div>
                  </div>
                )
              ) : null}
            </CardWidget>
          )}
          {incidentReportSubmitted &&
            ((isWrittenOff !== "" && !isWrittenOff) ||
              (isWrittenOff && disposalSubmitted && disposalReportChecked)) && (
              <ChecklistItem
                value={equipmentFailure}
                onChange={setEquipmentFailure}
                name={"equipmentFailureRadio"}
                labels={[t("reportIncidentPanel.equipment_failure_radio_labels")]}
                status={equipmentFailure !== "" ? true : false}
              />
            )}
          {incidentReportSubmitted && isWrittenOff !== "" && !isWrittenOff && equipmentFailure && (
            <WarningMsg message={t("reportIncidentPanel.equipment_failure_warning")} />
          )}
          {incidentReportSubmitted &&
            ((isWrittenOff !== "" && !isWrittenOff) ||
              (isWrittenOff && disposalSubmitted && disposalReportChecked)) &&
            equipmentFailure !== "" && (
              <>
                <ChecklistItem
                  value={isOperational}
                  onChange={setIsOperational}
                  name={"operationalRadio"}
                  labels={[t("reportIncidentPanel.incident_report_operational_labels")]}
                  status={isOperational !== "" ? true : false}
                />
                <ChecklistItem
                  value={isPreventable}
                  onChange={setIsPreventable}
                  name={"preventableRadio"}
                  labels={[
                    t("reportIncidentPanel.incident_report_equipment_required_labels"),
                    t("reportIncidentPanel.preventable"),
                    t("reportIncidentPanel.non_preventable"),
                  ]}
                  status={isPreventable !== "" ? true : false}
                />
                <CardWidget status={summary ? true : false}>
                  <label className="h5">{t("reportIncidentPanel.incident_summary")}</label>
                  <CustomTextArea
                    rows={7}
                    value={summary}
                    placeholder={t("reportIncidentPanel.enter_incident_summary")}
                    onChange={setSummary}
                    required
                    autoResize
                  />
                </CardWidget>
                <CardWidget status={photos.length !== 0 ? true : false}>
                  <label className="h5 form-tooltip">
                    {t("reportIssuePanel.upload_images")}
                    <Tooltip
                      label={"upload-tooltip"}
                      description={t("reportIssuePanel.upload-tooltip")}
                    />
                  </label>
                  <div className="custom-file input-files-container">
                    <FileUploadInput
                      images={photos}
                      setImages={setPhotos}
                      imageNames={photoNames}
                      setImageNames={setPhotoNames}
                      fileLoading={fileLoading}
                      setFileLoading={setFileLoading}
                      fileTypes=".pdf,.doc,.docx,image/*,.heic"
                      maxNumberOfFiles={20}
                    />
                  </div>
                </CardWidget>
                <div className="btn-1 p-my-5 p-pb-5 p-d-flex p-jc-center">
                  <Button
                    type="submit"
                    disabled={disableButton || fileLoading}
                    label={t("reportIncidentPanel.submit_incident")}
                  />
                </div>
              </>
            )}
        </div>
      </form>
    </div>
  );
};

export default IncidentReportForm;
