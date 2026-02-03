import React, { useState, useEffect } from "react";
import axios from "axios";
import moment from "moment";
import { useHistory } from "react-router-dom";
import { useMediaQuery } from "react-responsive";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import { getAuthHeader, getRolePermissions } from "../../../helpers/Authorization";
import UpdateIssue from "./UpdateIssue";
import LinkAccident from "./LinkAccident";
import DetailsView from "../../ShareComponents/DetailView/DetailsView";
import DetailsViewMobile from "../../ShareComponents/DetailView/DetailsViewMobile";
import IssueTypeBadge from "../../ShareComponents/helpers/IssueTypeBadge";
import LoadingAnimation from "../../ShareComponents/LoadingAnimation";
import { generalErrorAlert } from "../../ShareComponents/CommonAlert";
import { capitalize } from "../../../helpers/helperFunctions";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";
import "../../../styles/helpers/button4.scss";

const IssueDetails = ({
  issue,
  setSelectedIssue,
  setIssues,
  setMobileDetails,
  issuePanel,
  disableButtons,
  disableMobileVersion,
  detailsReady,
}) => {
  const history = useHistory();
  const { t } = useTranslation();
  const [isOperator, setIsOperator] = useState(false);
  const [editDialogStatus, setEditDialogStatus] = useState(false);
  const [displayAccidentTable, setDisplayAccidentTable] = useState(false);
  const [incidentDeets, setIncidentDeets] = useState(null);
  const [iDataPending, setiDataPending] = useState(false);
  const [repairDeets, setRepairDeets] = useState(null);
  const [rDataPending, setrDataPending] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    const rolePermissions = getRolePermissions();
    if (rolePermissions.role.toLowerCase() === "operator") setIsOperator(true);
  }, []);

  const onBack = () => {
    setMobileDetails(false);
    setSelectedIssue(null);
  };

  const onRepairRequest = () => {
    history.push({
      pathname: "/repairs/request",
      state: {
        vehicle: issue,
      },
    });
  };

  const getIncidentDetails = () => {
    if (!incidentDeets) {
      setiDataPending(true);
      axios
        .get(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Accident/Get/Details/CustomID/${issue.accident_custom_id}`,
          getAuthHeader()
        )
        .then((res) => {
          setIncidentDeets(res.data);
          setiDataPending(false);
        })
        .catch((error) => {
          generalErrorAlert(error.customErrorMsg);
          setiDataPending(false);
          ConsoleHelper(error);
        });
    }
  };

  const getRepairDetails = () => {
    if (!repairDeets) {
      setrDataPending(true);
      axios
        .get(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Get/Details/WorkOrder/${issue.repair_work_order}`,
          getAuthHeader()
        )
        .then((res) => {
          setRepairDeets(res.data);
          setrDataPending(false);
        })
        .catch((error) => {
          generalErrorAlert(error.customErrorMsg);
          setrDataPending(false);
          ConsoleHelper(error);
        });
    }
  };

  let detailViewTitles = [
    t("general.id"),
    t("general.asset_type"),
    t("general.location"),
    t("general.issue_type"),
    t("general.issue_title"),
    t("general.status"),
    t("general.created_by"),
    t("general.modified_by"),
    t("general.date_created"),
    t("general.date_updated"),
  ];
  let detailViewValues = [
    issue.custom_id,
    issue.asset_type,
    issue.current_location || t("general.not_applicable"),
    <IssueTypeBadge issueType={issue.issue_type} />,
    issue.issue_title,
    issue.is_resolved === true ? t("general.resolved") : t("general.unresolved"),
    issue.created_by,
    issue.modified_by || t("general.not_applicable"),
    moment(issue.issue_created).format("YYYY-MM-DD") || t("general.not_applicable"),
    moment(issue.issue_updated).format("YYYY-MM-DD") || t("general.not_applicable"),
  ];

  const otherDetails = (
    <React.Fragment>
      {issue.accident_custom_id && (
        <div
          className={`add-descr-section p-d-flex p-flex-column ${isMobile ? "main-details" : ""}`}
        >
          {isMobile && <hr />}
          <div className="p-d-flex p-jc-between">
            <span className="title">{t("issueDetails.linked_incident")}</span>
            <span className="value clickable-id" onClick={() => getIncidentDetails()}>
              {issue.accident_custom_id}
            </span>
          </div>
          {incidentDeets ? (
            <div className="p-mt-2 p-d-flex p-flex-column">
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.status")}:`}</span>
                <span className="sub-value">
                  {incidentDeets.is_resolved ? t("general.resolved") : t("general.unresolved")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("incidentsDetails.incident_type_label")}:`}</span>
                <span className="sub-value">
                  {incidentDeets.is_preventable
                    ? t("incidentsDetails.preventable")
                    : t("incidentsDetails.not_preventable")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("incidentsDetails.equipment_failure")}:`}</span>
                <span className="sub-value">
                  {incidentDeets.is_equipment_failure ? t("general.yes") : t("general.no")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("incidentsDetails.asset_state")}:`}</span>
                <span className="sub-value">
                  {incidentDeets.is_operational
                    ? t("general.operational")
                    : t("general.inoperational")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.date_created")}:`}</span>
                <span className="sub-value">
                  {moment(incidentDeets.date_created).format("YYYY-MM-DD")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.created_by")}:`}</span>
                <span className="sub-value">{incidentDeets.created_by}</span>
              </div>
              <div className="p-d-flex p-flex-column">
                <span className="sub-title">{`${t("incidentsDetails.accident_summary")}:`}</span>
                <span className="sub-value">
                  {incidentDeets.accident_summary
                    ? incidentDeets.accident_summary
                    : t("general.not_applicable")}
                </span>
              </div>
            </div>
          ) : iDataPending ? (
            <div className="p-mt-2">
              <LoadingAnimation height={"150px"} />
            </div>
          ) : null}
          {!isMobile && <hr />}
        </div>
      )}
      {issue.repair_work_order && issue.repair_work_order !== t("general.not_applicable") && (
        <div
          className={`add-descr-section p-d-flex p-flex-column ${isMobile ? "main-details" : ""}`}
        >
          {isMobile && <hr />}
          <div className="p-d-flex p-jc-between">
            <span className="title">{t("issueDetails.linked_repair")}</span>
            <span className="value clickable-id" onClick={() => getRepairDetails()}>
              {issue.repair_work_order}
            </span>
          </div>
          {repairDeets ? (
            <div className="p-mt-2 p-d-flex p-flex-column">
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.status")}:`}</span>
                <span className="sub-value">{capitalize(repairDeets.status)}</span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.vendor_name")}:`}</span>
                <span className="sub-value">
                  {repairDeets.vendor_name ? repairDeets.vendor_name : t("general.not_applicable")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.vendor_email")}:`}</span>
                <span className="sub-value">
                  {repairDeets.vendor_email
                    ? repairDeets.vendor_email
                    : t("general.not_applicable")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.requested_delivery_date")}:`}</span>
                <span className="sub-value">
                  {moment(repairDeets.requested_delivery_date).format("YYYY-MM-DD")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.date_created")}:`}</span>
                <span className="sub-value">
                  {moment(repairDeets.date_created).format("YYYY-MM-DD")}
                </span>
              </div>
              <div className="p-d-flex p-jc-between">
                <span className="sub-title">{`${t("general.created_by")}:`}</span>
                <span className="sub-value">{repairDeets.created_by}</span>
              </div>
              <div className="p-d-flex p-flex-column">
                <span className="sub-title">
                  {`${t("repairRequestPanel.repair_description_label")}:`}
                </span>
                <span className="sub-value">
                  {repairDeets.description ? repairDeets.description : t("general.not_applicable")}
                </span>
              </div>
            </div>
          ) : rDataPending ? (
            <div className="p-mt-2">
              <LoadingAnimation height={"150px"} />
            </div>
          ) : null}
          {!isMobile && <hr />}
        </div>
      )}
    </React.Fragment>
  );

  return (
    <React.Fragment>
      {/* Issue Details View */}
      {isMobile && !disableMobileVersion ? (
        <div className="p-mx-2 p-my-3">
          <div className="no-style-btn p-my-3">
            <Button
              label={t("general.back")}
              className="p-button-link"
              icon="pi pi-chevron-left"
              onClick={() => onBack()}
            />
          </div>
          <DetailsViewMobile
            header={t("general.header_vin", { vin: issue.VIN })}
            titles={detailViewTitles}
            values={detailViewValues}
            description={[
              t("issueDetails.description"),
              issue.issue_details || t("general.not_applicable"),
            ]}
            files={issue.files}
            editBtn={
              !isOperator && !issue.is_resolved && !disableButtons
                ? t("issueDetails.edit_issue_header")
                : ""
            }
            onEdit={() => setEditDialogStatus(true)}
            actionBtn1={
              !issue.is_resolved && !issue.repair_id && !isOperator && !disableButtons
                ? [t("issueDetails.repair_request"), "pi-external-link", "detail-action-color-1"]
                : ""
            }
            onActionBtn1={() => onRepairRequest()}
            actionBtn2={
              !issue.is_resolved && !issue.accident_id && !isOperator && !disableButtons
                ? [t("issueDetails.link_accident"), "pi-link", "detail-action-color-2"]
                : ""
            }
            onActionBtn2={() => setDisplayAccidentTable(true)}
            additionalDescr={otherDetails}
          />
        </div>
      ) : (
        <DetailsView
          headers={[t("issueDetails.issue_details"), t("general.header_vin", { vin: issue.VIN })]}
          titles={detailViewTitles}
          values={detailViewValues}
          description={[
            t("issueDetails.description"),
            issue.issue_details || t("general.not_applicable"),
          ]}
          files={issue.files}
          onHideDialog={setSelectedIssue}
          editBtn={
            !isOperator && !issue.is_resolved && !disableButtons
              ? t("issueDetails.edit_issue_header")
              : ""
          }
          onEdit={() => setEditDialogStatus(true)}
          actionBtn1={
            !issue.is_resolved && !issue.repair_id && !isOperator && !disableButtons
              ? [t("issueDetails.repair_request"), "pi-external-link", "detail-action-color-1"]
              : ""
          }
          onActionBtn1={() => onRepairRequest()}
          actionBtn2={
            !issue.is_resolved && !issue.accident_id && !isOperator && !disableButtons
              ? [t("issueDetails.link_accident"), "pi-link", "detail-action-color-2"]
              : ""
          }
          onActionBtn2={() => setDisplayAccidentTable(true)}
          detailsReady={detailsReady}
          additionalDescr={otherDetails}
        />
      )}
      {/* Update Accident Dialog */}
      <UpdateIssue
        issue={issue}
        editDialogStatus={editDialogStatus}
        setEditDialogStatus={setEditDialogStatus}
        setSelectedIssue={setSelectedIssue}
        setIssues={setIssues}
        issuePanel={issuePanel}
      />
      {/* Link Accident Dialog */}
      <LinkAccident
        issue={issue}
        displayAccidentTable={displayAccidentTable}
        setDisplayAccidentTable={setDisplayAccidentTable}
        setSelectedIssue={setSelectedIssue}
        setIssues={setIssues}
        issuePanel={issuePanel}
      />
    </React.Fragment>
  );
};

export default IssueDetails;
