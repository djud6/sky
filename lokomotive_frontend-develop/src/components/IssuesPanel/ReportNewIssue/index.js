import React, { useEffect, useState } from "react";
import axios from "axios";
import swal from "sweetalert";
import moment from "moment";
import { useDispatch, useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { useHistory, useLocation } from "react-router-dom";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import {
  getAuthHeader,
  hasModulePermission,
  getRolePermissions,
} from "../../../helpers/Authorization";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { faExclamationTriangle } from "@fortawesome/free-solid-svg-icons";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import ChecklistItem from "../../ShareComponents/ChecklistItem";
import CardWidget from "../../ShareComponents/CardWidget";
import ShowMore from "../../ShareComponents/ShowMore";
import { Table } from "../../ShareComponents/Table";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import FileUploadInput from "../../ShareComponents/FileUploadInput";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import CustomInputText from "../../ShareComponents/CustomInputText";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import {
  loadingAlert,
  successAlert,
  errorAlert,
  generalErrorAlert,
} from "../../ShareComponents/CommonAlert";
import IncidentReportForm from "../../IncidentsPanel/ReportNewIncident/IncidentReportForm";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/IssuesPanel/reportNewIssues.scss";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/helpers/button1.scss";
import "../../../styles/helpers/fileInput.scss";

const ReportIssuePanel = () => {
  const { t } = useTranslation();
  const [isOperator, setIsOperator] = useState(false);
  const [vehicle, setVehicle] = useState(null);
  const [forceUpdate, setForceUpdate] = useState(Date.now());
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  let location = useLocation();
  if (!vehicle && location.query) {
    setVehicle(location.query.vehicle);
  }

  useEffect(() => {
    const rolePermissions = getRolePermissions();
    if (rolePermissions.role.toLowerCase() === "operator") setIsOperator(true);
  }, []);

  return (
    <div>
      {isMobile && !isOperator && (
        <QuickAccessTabs
          tabs={["Reports", "Search", "New Issue"]}
          activeTab={"New Issue"}
          urls={["/issues", "/issues/search", "/issues/new"]}
        />
      )}
      {isMobile && isOperator && (
        <QuickAccessTabs
          tabs={["Search Issues", "New Issue"]}
          activeTab={"New Issue"}
          urls={["/issues/search", "/issues/new"]}
        />
      )}
      <PanelHeader icon={faExclamationTriangle} text={t("reportIssuePanel.report_issues")} />
      {!isMobile && !isOperator && (
        <QuickAccessTabs
          tabs={["Issue Reports", "Search Issues", "Report New Issue"]}
          activeTab={"Report New Issue"}
          urls={["/issues", "/issues/search", "/issues/new"]}
        />
      )}
      {!isMobile && isOperator && (
        <QuickAccessTabs
          tabs={["Search Issues", "Report New Issue"]}
          activeTab={"Report New Issue"}
          urls={["/issues/search", "/issues/new"]}
        />
      )}
      <div className={`${isMobile ? "" : "p-mt-5"}`}>
        <VINSearch
          key={forceUpdate}
          defaultValue={`${!vehicle && location.state ? location.state.vehicle.VIN : ""}`}
          onVehicleSelected={(v) => {
            setVehicle(v);
          }}
        />
      </div>
      {vehicle && !Array.isArray(vehicle) && (
        <div>
          <IssueReportForVehicle
            vehicle={vehicle}
            issueTitle={t("reportIssuePanel.report_issue_for_vehicle_vin", {
              vehicleVIN: vehicle.VIN,
            })}
            setVehicle={setVehicle}
            setForceUpdate={setForceUpdate}
          />
        </div>
      )}
    </div>
  );
};

const IssueReportForVehicle = ({ vehicle, issueTitle, setVehicle, setForceUpdate }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const history = useHistory();
  const [isAccident, setIsAccident] = useState("");
  const [relatedAccidents, setRelatedAccidents] = useState([]);
  const [reportAccidentStatus, setReportAccidentStatus] = useState(false);
  const [selectedAccident, setSelectedAccident] = useState(null);
  const [dataReady, setDataReady] = useState(false);
  const [description, setDescription] = useState("");
  const [iCategory, setiCategory] = useState(null);
  const [title, setTitle] = useState("");
  const [photos, setPhotos] = useState([]);
  const [fileLoading, setFileLoading] = useState(false);
  const [photoNames, setPhotoNames] = useState([]);
  const [criticalIssue, setCriticalIssue] = useState(null);
  const [incidentReportSubmitted, setIncidentReportSubmitted] = useState("");
  const { listIssueCategories } = useSelector((state) => state.apiCallData);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  // If vehicle changes, reset form
  useEffect(() => {
    setIsAccident("");
    setRelatedAccidents([]);
    setDataReady(false);
    setiCategory(null);
    setDescription("");
    setTitle("");
    setPhotos([]);
    setPhotoNames([]);
    setIncidentReportSubmitted("");
    setSelectedAccident(null);
  }, [vehicle]);

  useEffect(() => {
    if (isAccident && incidentReportSubmitted) {
      const cancelTokenSource = axios.CancelToken.source();
      setRelatedAccidents([]);
      setSelectedAccident(null);
      setDataReady(false);
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Accident/VIN/${vehicle.VIN}`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          setRelatedAccidents(response.data);
          setDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAccident, incidentReportSubmitted]);

  useEffect(() => {
    if (!incidentReportSubmitted) {
      setSelectedAccident(null);
    }
  }, [incidentReportSubmitted]);

  const resetForm = () => {
    setVehicle(null);
    setForceUpdate(Date.now());
  };

  if (!relatedAccidents) return null;

  const incidentType = {
    all: t("general.all"),
    preventable: t("general.preventable"),
    nonpreventable: t("general.non_preventable"),
  };

  const incidentItemTemplate = (value) => {
    return value ? incidentType.preventable : incidentType.nonpreventable;
  };

  let relatedAccidentHeaders = [];
  let relatedAccidentData = [];

  if (relatedAccidents) {
    relatedAccidents.filter((i) => {
      return !i.is_resolved;
    });

    relatedAccidentHeaders = [
      { header: t("general.id"), colFilter: { field: "custom_id" } },
      { header: t("incidentsDetails.accident_summary"), colFilter: { field: "accident_summary" } },
      {
        header: t("incidentsDetails.incident_type_label"),
        colFilter: {
          field: "is_preventable",
          filterOptions: {
            filterAs: "dropdown",
            valueTemplate: incidentItemTemplate,
            itemTemplate: incidentItemTemplate,
          },
        },
      },
      {
        header: t("incidentsDetails.date_reported_label"),
        colFilter: {
          field: "date_created",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },
      {
        header: t("general.created_by"),
        colFilter: { field: "created_by", filterOptions: { filterAs: "dropdown" } },
      },
    ];

    relatedAccidentData = relatedAccidents.map((incident) => {
      return {
        id: incident.accident_id,
        dataPoint: incident,
        cells: [
          incident.custom_id,
          <ShowMore text={incident.accident_summary || "N/A"} excerpt={20} />,
          incident.is_preventable ? incidentType.preventable : incidentType.nonpreventable,
          moment(incident.date_created).format("YYYY-MM-DD"),
          incident.created_by,
        ],
      };
    });
  }

  const handleSubmit = (event) => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    event.preventDefault();
    let issueReport = new FormData();
    issueReport.append(
      "data",
      JSON.stringify({
        VIN: vehicle.VIN,
        issue_title: title,
        issue_details: description,
        issue_type: criticalIssue ? t("general.critical") : t("general.non_critical"),
        category: iCategory.id,
      })
    );
    for (let i = 0; i < photos.length; i++) {
      issueReport.append("files", photos[i]);
    }
    sendIssueReport(issueReport);
  };

  const sendIssueReport = (issueReport) => {
    loadingAlert(t("swal.loading_report"));
    const headers = getAuthHeader();
    headers.headers["Content-Type"] = "application/json";
    const requestConfig = {
      method: "post",
      url: `${Constants.ENDPOINT_PREFIX}/api/v1/Issues/Add`,
      ...headers,
      data: issueReport,
    };
    axios(requestConfig)
      .then((response) => {
        sendIssueSuccessAlert();
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
        return response.data;
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      })
      .then((data) => {
        if (selectedAccident) {
          axios
            .post(
              `${Constants.ENDPOINT_PREFIX}/api/v1/Issues/ID/${data.issue_id}/Set/Accident/ID/${selectedAccident.accident_id}`,
              null,
              getAuthHeader()
            )
            .catch((error) => {
              ConsoleHelper(error);
              generalErrorAlert(error.customErrorMsg);
              dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
            });
        }
      });
  };

  const sendIncidentReport = (incidentReport) => {
    loadingAlert(t("swal.loading_report"));
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
        successAlert(t("general.report_incident"));
        setIncidentReportSubmitted(true);
        setReportAccidentStatus(true);
        return response.data;
      })
      .catch((error) => {
        errorAlert(error.customErrorMsg, sendIncidentReport(incidentReport));
        ConsoleHelper(error);
      })
      .then((data) => {
        setSelectedAccident(data);
      });
  };

  const sendIssueSuccessAlert = () => {
    return swal({
      title: t("general.success"),
      text: t("general.your_issue_report_has_been_submitted"),
      icon: "success",
      buttons: { return: t("general.return"), new: t("general.new_report") },
    }).then((value) => {
      switch (value) {
        case "return":
          hasModulePermission("issues_list")
            ? history.push("/issues")
            : history.push("/issues/search");
          break;
        default:
          resetForm();
      }
    });
  };

  const selectIssueCategory = (id) => {
    let selected = listIssueCategories.find((i) => i.id === parseInt(id));
    setiCategory(selected);
  };

  if (!vehicle) return null;

  let isBtnDisabled = true;
  if (criticalIssue !== null) isBtnDisabled = false;

  return (
    <div className="p-mx-3 p-mt-5">
      <div className="report-issues-form-container">
        <form onSubmit={handleSubmit}>
          <h3 className="p-mb-4 report-issue-title">{issueTitle}</h3>
          <ChecklistItem
            value={isAccident}
            onChange={setIsAccident}
            name={"isAccidentRadio"}
            labels={[t("reportIssuePanel.was_issue_a_result_from_accident")]}
            status={isAccident !== "" ? true : false}
          />
          {isAccident && (
            <ChecklistItem
              value={incidentReportSubmitted}
              onChange={setIncidentReportSubmitted}
              name={"incidentReportRadio"}
              labels={[t("reportIssuePanel.was_incident_report_submitted")]}
              status={incidentReportSubmitted !== "" ? true : false}
            />
          )}
          {isAccident === true && incidentReportSubmitted === true && !reportAccidentStatus && (
            <CardWidget status={selectedAccident ? true : false}>
              <label className="h5">{t("reportIssuePanel.link_incident_to_issue")}</label>
              <div className="darkTable">
                <Table
                  dataReady={dataReady}
                  tableHeaders={relatedAccidentHeaders}
                  tableData={relatedAccidentData}
                  onSelectionChange={(incident) => setSelectedAccident(incident)}
                  hasSelection
                  globalSearch={false}
                  rows={isMobile ? 2 : 5}
                  disableMobileDetail
                />
              </div>
            </CardWidget>
          )}
          {/* {isAccident === true && incidentReportSubmitted === false && (
          <WarningMsg message={t("reportIssuePanel.complete_internal_incident_report")} />
        )} */}
          {((isAccident === true && incidentReportSubmitted === true) || isAccident === false) && (
            <>
              <div>
                <CardWidget status={title && description && iCategory ? true : false}>
                  <label className="h5">{t("reportIssuePanel.issue_category")}</label>
                  <div className="w-100">
                    <FormDropdown
                      onChange={selectIssueCategory}
                      options={
                        listIssueCategories &&
                        listIssueCategories.map((category) => ({
                          name: category.name,
                          code: category.id,
                        }))
                      }
                      dataReady={listIssueCategories}
                      plain_dropdown
                    />
                  </div>
                  <label className="h5">{t("general.issue_title")}</label>
                  <CustomInputText
                    placeholder={t("general.issue_title")}
                    onChange={setTitle}
                    required
                  />
                  <label className="h5 p-mt-4">{t("reportIssuePanel.issue_description")}</label>
                  <CustomTextArea
                    rows={10}
                    value={description}
                    placeholder={t("reportIssuePanel.enter_repair_description")}
                    onChange={setDescription}
                    required
                    autoResize
                  />
                </CardWidget>
                <ChecklistItem
                  value={criticalIssue}
                  onChange={setCriticalIssue}
                  name={"criticalIssueRadio"}
                  labels={[t("reportIssuePanel.critical_issue_question")]}
                  status={criticalIssue !== null ? true : false}
                />
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
              </div>
              <div className="d-flex justify-content-center">
                <div className={`${isMobile ? "p-mb-5" : ""} p-mt-3 p-d-flex p-jc-center btn-1`}>
                  <Button
                    disabled={isBtnDisabled || fileLoading}
                    type="submit"
                    label={t("buttonLabels.submit_issue")}
                  />
                </div>
              </div>
            </>
          )}
        </form>
      </div>

      {isAccident === true && incidentReportSubmitted === false && (
        <div className="p-mt-3">
          <IncidentReportForm
            vehicle={vehicle}
            title={`${t("reportIncidentPanel.report_incident_for_vehicle_vin")} ${vehicle.VIN}`}
            sendIncidentReport={sendIncidentReport}
          />
        </div>
      )}
    </div>
  );
};

export default ReportIssuePanel;
