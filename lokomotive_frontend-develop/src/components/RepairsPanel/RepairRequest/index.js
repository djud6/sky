import React, { useEffect, useState } from "react";
import axios from "axios";
import swal from "sweetalert";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { useLocation } from "react-router-dom";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import { faWrench } from "@fortawesome/free-solid-svg-icons";
import ChecklistItem from "../../ShareComponents/ChecklistItem";
import WarningMsg from "../../ShareComponents/WarningMsg";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import { loadingAlert, errorAlert } from "../../ShareComponents/CommonAlert";
import IncidentReportForm from "../../IncidentsPanel/ReportNewIncident/IncidentReportForm";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import IssuesTable from "./IssuesTable";
import RepairRequestForm from "./RepairRequestForm";
import "./RepairRequestPanel.css";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/RepairsPanel/repairRequest.scss";
import "../../../styles/dialogStyles.scss";
import "../../../styles/helpers/button1.scss";
import "../../../styles/helpers/button2.scss";
import "../../../styles/helpers/radiobutton.scss";
import "../../../styles/helpers/fileInput.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";

const RepairRequestPanel = () => {
  const location = useLocation();
  const { t } = useTranslation();
  const [vehicle, setVehicle] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["List Repairs", "Repair Request"]}
          activeTab={"Repair Request"}
          urls={["/repairs", "/repairs/request"]}
        />
      )}
      <PanelHeader icon={faWrench} text={t("repairRequestPanel.repair_request_title")} mobileBg />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["List Repairs", "Repair Request"]}
          activeTab={"Repair Request"}
          urls={["/repairs", "/repairs/request"]}
        />
      )}
      <div className={`VIN-cont ${isMobile ? "p-pb-4" : "p-mt-5"}`}>
        <VINSearch
          defaultValue={`${
            !vehicle && location.query
              ? location.query.vehicle.VIN
              : !vehicle && location.state
              ? location.state.vehicle.VIN
              : ""
          }`}
          onVehicleSelected={(v) => {
            setVehicle(v);
          }}
        />
      </div>
      {vehicle && !Array.isArray(vehicle) && (
        <div>
          <RepairRequestForVehicle
            vehicle={vehicle || location.query.vehicle || location.state.vehicle}
          />
        </div>
      )}
    </div>
  );
};

const RepairRequestForVehicle = ({ vehicle }) => {
  const { t } = useTranslation();
  const [issues, setIssues] = useState([]);
  const [dataReady, setDataReady] = useState(false);
  const [selectedIssues, setSelectedIssues] = useState([]);
  const [validRepair, setValidRepair] = useState(false);
  const [forceUpdateTable, setForceUpdateTable] = useState(Date.now);
  const [submitSuccessForceUpdate, setSubmitSuccessForceUpdate] = useState(Date.now);
  const [isAccident, setIsAccident] = useState("");
  const [accidentReported, setAccidentReported] = useState("");
  const [submitIncidentSuccess, setSubmitIncidentSuccess] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const resetForm = () => {
    setForceUpdateTable(Date.now);
    setSelectedIssues([]);
    setIsAccident("");
    setAccidentReported("");
    setValidRepair(false);
    setSubmitIncidentSuccess(false);
  };

  useEffect(() => {
    setIssues([]);
    setDataReady(false);
    setSelectedIssues([]);
    setIsAccident("");
    setAccidentReported("");
    setValidRepair(false);
    setSubmitIncidentSuccess(false);
    if (vehicle) {
      axios
        .get(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Issues/Get/Unresolved/${vehicle.VIN}`,
          getAuthHeader()
        )
        .then((response) => {
          let initIssues = response.data.filter((issue) => {
            return !issue.repair_id;
          });
          let incidentsIssues = initIssues.map((issue) => {
            return issue.accident_id
              ? { ...issue, incident_reported: t("general.yes") }
              : { ...issue, incident_reported: t("general.no") };
          });
          setIssues(incidentsIssues);
          setDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicle, submitSuccessForceUpdate]);

  // Reset questions each time a different issue is selected
  useEffect(() => {
    setIsAccident("");
    setAccidentReported("");
    setValidRepair(false);
    setSubmitIncidentSuccess(false);
  }, [selectedIssues]);

  /* 
    If user declares something is not caused by accident, but more than one selected issue
    is flagged as an accident, user will be prompted to report the incident or cancel the request.
  */
  const unreportedAccident = () => {
    return swal({
      title: t("repairRequestPanel.unreported_accident_alert_title"),
      text: t("repairRequestPanel.unreported_accident_alert_text"),
      icon: "warning",
      buttons: {
        cancel: t("repairRequestPanel.unreported_accident_alert_cancel"),
      },
    }).then(() => {
      setAccidentReported("");
    });
  };

  /* 
    If user declares something is caused by accident, but more than one selected issue
    is flagged as a non-accident, user will be prompted to reselect issues or cancel the request.
  */
  const reportedAccidents = () => {
    return swal({
      title: t("repairRequestPanel.reported_accident_alert_title"),
      text: t("repairRequestPanel.reported_accident_alert_text"),
      icon: "warning",
      buttons: {
        return: t("repairRequestPanel.reported_accident_alert_return"),
      },
    }).then(() => {
      resetForm();
    });
  };

  /* 
    If user declares something is caused by accident, they haven't filled out the form but they actually do
    user will be prompted to reselect issues or cancel the request.
  */
  const accidentsReportedBefore = () => {
    return swal({
      title: t("repairRequestPanel.accident_reported_before_alert_title"),
      text: t("repairRequestPanel.accident_reported_before_alert_text"),
      icon: "warning",
      buttons: {
        return: t("repairRequestPanel.accident_reported_before_alert_return"),
        cancel: t("repairRequestPanel.accident_reported_before_alert_cancel"),
      },
    }).then((value) => {
      switch (value) {
        case "return":
          break;
        case "cancel":
          setAccidentReported(true);
          setValidRepair(true);
          break;
        default:
          setAccidentReported(true);
          setValidRepair(true);
          break;
      }
    });
  };

  const sendIncidentReport = (incidentReport) => {
    loadingAlert();
    const headers = getAuthHeader();
    headers.headers["Content-Type"] = "application/json";
    const requestConfig = {
      method: "post",
      url: `${Constants.ENDPOINT_PREFIX}/api/v1/Accident/Add`,
      ...headers,
      data: incidentReport,
    };
    axios(requestConfig)
      .then((response) => {
        return response.data;
      })
      .catch((error) => {
        errorAlert(error.customErrorMsg, sendIncidentReport);
      })
      .then((data) => {
        let accidentID = data.accident_id;
        selectedIssues.forEach((issue) => {
          axios
            .post(
              `${Constants.ENDPOINT_PREFIX}/api/v1/Issues/ID/${issue.issue_id}/Set/Accident/ID/${accidentID}`,
              null,
              getAuthHeader()
            )
            .catch((error) => {
              ConsoleHelper(error);
              errorAlert(error.customErrorMsg, sendIncidentReport);
            });
          issues.forEach((o, i) => {
            if (o.issue_id === issue.issue_id) {
              issues[i] = { ...issues[i], accident_id: accidentID };
              issues[i].incident_reported = t("general.yes");
            }
          });
        });
      })
      .then(() => {
        IncidentReportedSuccess();
      })
      .catch((error) => {
        ConsoleHelper(error);
        errorAlert(error.customErrorMsg, sendIncidentReport);
      });
  };

  const successAlert = () => {
    return swal({
      title: t("repairRequestPanel.submit_incident_report_successSwAl_title"),
      text: t("repairRequestPanel.submit_incident_report_successSwAl_text", {
        vehicle_vin: vehicle.VIN,
      }),
      icon: "success",
      buttons: { repair: t("repairRequestPanel.submit_incident_report_successSwAl_repair") },
    });
  };

  let accidentIssues = selectedIssues.filter((issue) => issue.accident_id);
  let nonAccidentIssues = selectedIssues.filter((issue) => !issue.accident_id);
  let validCombination =
    accidentIssues.length === 0 || nonAccidentIssues.length === 0 ? true : false;

  const IncidentReportedSuccess = () => {
    setSubmitIncidentSuccess(true);
    setValidRepair(true);
    successAlert();
  };

  useEffect(() => {
    if (validCombination) {
      if (isAccident && accidentReported === false && submitIncidentSuccess) {
        setValidRepair(true);
      } else if (isAccident === false && accidentIssues.length === 0) {
        setValidRepair(true);
      } else if (isAccident && accidentReported && nonAccidentIssues.length === 0) {
        setValidRepair(true);
      } else {
        setValidRepair(false);
      }
    }
  }, [
    isAccident,
    accidentReported,
    accidentIssues,
    nonAccidentIssues,
    validCombination,
    submitIncidentSuccess,
  ]);

  if (issues.length === 0 && dataReady)
    return (
      <div className={`${isMobile ? "p-mx-3 p-mt-3" : "p-mx-1"}`}>
        <WarningMsg message={t("repairRequestPanel.no_issues_label")} />
      </div>
    );

  if (!vehicle) return null;
  return (
    <div className="p-mt-2 p-mb-5">
      <IssuesTable
        forceUpdateTable={forceUpdateTable}
        vehicle={vehicle}
        issues={issues}
        dataReady={dataReady}
        getSelectedRowsFromTable={(dataFromChild) => setSelectedIssues(dataFromChild)}
      />
      {selectedIssues.length !== 0 && (
        <div className="repair-request-form p-mx-2">
          <div className="row">
            <div className="col">
              <div className="d-flex flex-column p-mt-5">
                <div className="report-form-container p-mb-3">
                  <h4 className="repair-form-title p-mb-3">
                    {t("repairRequestPanel.submit_repair_request_for_label", {
                      vehicle_vin: vehicle.VIN,
                    })}
                  </h4>
                  <ChecklistItem
                    value={isAccident}
                    onChange={(bool) => {
                      setIsAccident(bool);
                      if (bool === false) {
                        setAccidentReported("");
                        if (accidentIssues.length > 0) {
                          reportedAccidents();
                        }
                      }
                    }}
                    name={"accidentRadio"}
                    labels={[t("repairRequestPanel.accident_radio_btn_label")]}
                    status={isAccident !== "" ? true : false}
                  />
                  {validRepair === false ? (
                    <React.Fragment>
                      {isAccident && (
                        <ChecklistItem
                          value={accidentReported}
                          onChange={(bool) => {
                            setAccidentReported(bool);
                            if (bool === true && nonAccidentIssues.length > 0) {
                              unreportedAccident();
                            }
                            if (bool === false && nonAccidentIssues.length === 0) {
                              accidentsReportedBefore();
                            }
                          }}
                          name={"reportRadio"}
                          labels={[t("repairRequestPanel.report_radio_btn_label")]}
                          status={accidentReported !== "" ? true : false}
                        />
                      )}
                      {isAccident && accidentReported === false && (
                        <div>
                          <IncidentReportForm
                            vehicle={vehicle}
                            title={`${t("reportIncidentPanel.report_incident_for_vehicle_vin")} ${
                              vehicle.VIN
                            }`}
                            sendIncidentReport={sendIncidentReport}
                          />
                        </div>
                      )}
                    </React.Fragment>
                  ) : (
                    <RepairRequestForm
                      issues={selectedIssues}
                      vehicle={vehicle}
                      resetForm={resetForm}
                      setSubmitSuccessForceUpdate={setSubmitSuccessForceUpdate}
                    />
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RepairRequestPanel;
