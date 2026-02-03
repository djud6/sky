import React, { useState } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import * as Constants from "../../constants";
import { getAuthHeader } from "../../helpers/Authorization";
import { isEmptyString } from "../../helpers/helperFunctions";
import ApprovalStatusBadge from "./ApprovalStatusBadge";
import CustomTextArea from "../ShareComponents/CustomTextArea";
import DetailsView from "../ShareComponents/DetailView/DetailsView";
import DetailsViewMobile from "../ShareComponents/DetailView/DetailsViewMobile";
import RequestTypeDetails from "./RequestTypeDetails";
import Quote from "./Quote";
import { loadingAlert, successAlert, generalErrorAlert } from "../ShareComponents/CommonAlert";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import "../../styles/dialogStyles.scss";
import "../../styles/helpers/button4.scss";

const ApprovalDetails = ({
  selectedRequest,
  setSelectedRequest,
  setDataReady,
  withApproval = false,
  setMobileDetails,
}) => {
  const { t } = useTranslation();
  const [dialogStatus, setDialogStatus] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [typeDataReady, setTypeDataReady] = useState(false);
  const [requestFiles, setRequestFiles] = useState([]);
  const [quotesList, setQuotesList] = useState([]);
  const [selectedQuote, setSelectedQuote] = useState(null);
  const [selectedRow, setSelectedRow] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const onBack = () => {
    setMobileDetails(false);
    setSelectedRequest(null);
  };

  let detailViewTitles = [
    t("general.title"),
    t("approvalDetails.request_type"),
    t("general.status"),
    ...(selectedRequest.is_approved.toLowerCase() === "rejected"
      ? [t("approvalDetails.reject_reason")]
      : []),
    t("general.current_location"),
    t("approvalDetails.request_user_lable"),
    t("general.date_created"),
    t("general.date_updated"),
  ];
  let detailViewValues = [
    selectedRequest.title,
    selectedRequest.request_type,
    <ApprovalStatusBadge isApproved={selectedRequest.is_approved} />,
    ...(selectedRequest.is_approved.toLowerCase() === "rejected"
      ? [selectedRequest.deny_reason]
      : []),
    selectedRequest.current_location,
    selectedRequest.requesting_user || t("general.not_applicable"),
    selectedRequest.date_created,
    selectedRequest.date_modified,
  ];

  const handleRejection = () => {
    let data = {
      approval_id: selectedRequest.approval_id,
      is_approved: false,
      deny_reason: rejectReason,
    };
    handleApprovalRequest(data);
  };

  const handleApprovalRequest = (requestData) => {
    loadingAlert();
    const quoteApprovalAPI = `${Constants.ENDPOINT_PREFIX}/api-vendor/v1/Request/Quote/Approve/${selectedQuote?.id}`;
    const requestApprovalAPI = `${Constants.ENDPOINT_PREFIX}/api/v1/Approval/Set/Status`;

    const callback = async (ApiToRun) => {
      return axios.post(ApiToRun, requestData, getAuthHeader()).then((response) => {
        successAlert("msg", t("approvalDetails.submit_success"));
        setDataReady(false);
      });
    };

    const errorHandler = (error) => {
      ConsoleHelper(error);
      generalErrorAlert(error.customErrorMsg);
    };
    if( (selectedRow.in_house === false && (selectedRow.potential_vendors !== null)) || selectedRequest.request_type.toLowerCase() === "asset transfer"){
        // quote approval
      callback(quoteApprovalAPI).catch(errorHandler);
    }
    else{
      // set status
      callback(requestApprovalAPI).catch(errorHandler);
    }
  };

  const renderFooter = () => {
    return (
      <Button
        label={t("approvalDetails.reject_btn")}
        icon="pi pi-times"
        className="p-mt-4"
        onClick={() => handleRejection()}
        disabled={isEmptyString(rejectReason)}
      />
    );
  };

  return (
    <React.Fragment>
      {isMobile ? (
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
            header={t("general.header_vin", { vin: selectedRequest.VIN })}
            titles={detailViewTitles}
            values={detailViewValues}
            description={[
              t("general.description"),
              selectedRequest.description || t("general.not_applicable"),
            ]}
            optionalActionGroup={
              requestFiles && requestFiles.length !== 0 ? (
                <Quote
                  files={requestFiles}
                  quotesList={quotesList}
                  selectedQuote={selectedQuote}
                  setSelectedQuote={setSelectedQuote}
                  withApproval={withApproval}
                  requestStatus={selectedRequest.is_approved}
                  handleQuoteApproval={() => {
                    handleApprovalRequest({
                      approval_id: selectedRequest.approval_id,
                      is_approved: true,
                      deny_reason: null,
                    });
                  }}
                />
              ) : null
            }
            actionBtn1={
              selectedRow &&
              (selectedRow.potential_vendor_ids !== null || selectedRow.estimated_cost !== null) &&
              selectedRequest.is_approved.toLowerCase() === "awaiting approval"
                ? [t("approvalDetails.approve_btn"), "pi-check-circle", "detail-action-color-1"]
                : ""
            }
            onActionBtn1={() => {
              handleApprovalRequest({
                approval_id: selectedRequest.approval_id,
                is_approved: true,
                deny_reason: null,
              });
            }}
            actionBtn2={
              selectedRow &&
              (selectedRow.potential_vendor_ids !== null || selectedRow.estimated_cost !== null) &&
              selectedRequest.is_approved.toLowerCase() === "awaiting approval"
                ? [t("approvalDetails.reject_btn"), "pi-times-circle", "detail-action-color-3"]
                : ""
            }
            onActionBtn2={() => setDialogStatus(true)}
            additionalDescr={
              <RequestTypeDetails
                request={selectedRequest}
                dataReady={typeDataReady}
                setDataReady={setTypeDataReady}
                setSelectedRequest={setSelectedRow}
                setRequestFiles={setRequestFiles}
                setQuotesList={setQuotesList}
              />
            }
          />
        </div>
      ) : (
        <DetailsView
          headers={[
            t("approvalDetails.approval_request_details_title"),
            t("general.header_vin", { vin: selectedRequest.VIN }),
          ]}
          titles={detailViewTitles}
          values={detailViewValues}
          description={[
            t("general.description"),
            selectedRequest.description || t("general.not_applicable"),
          ]}
          onHideDialog={setSelectedRequest}
          optionalActionGroup={
            requestFiles && requestFiles.length !== 0 ? (
              <Quote
                files={requestFiles}
                quotesList={quotesList}
                selectedQuote={selectedQuote}
                setSelectedQuote={setSelectedQuote}
                withApproval={withApproval}
                requestStatus={selectedRequest.is_approved}
                handleQuoteApproval={() => {
                  handleApprovalRequest({
                    approval_id: selectedRequest.approval_id,
                    is_approved: true,
                    deny_reason: null,
                  });
                }}
              />
            ) : null
          }
          actionBtn1={
            selectedRow &&
            (selectedRow.potential_vendor_ids !== null || selectedRow.estimated_cost !== null) &&
            selectedRequest.is_approved.toLowerCase() === "awaiting approval"
              ? [t("approvalDetails.approve_btn"), "pi-check-circle", "detail-action-color-1"]
              : ""
          }
          onActionBtn1={() => {
            handleApprovalRequest({
              approval_id: selectedRequest.approval_id,
              is_approved: true,
              deny_reason: null,
            });
          }}
          actionBtn2={
            selectedRow &&
            (selectedRow.potential_vendor_ids !== null || selectedRow.estimated_cost !== null) &&
            selectedRequest.is_approved.toLowerCase() === "awaiting approval"
              ? [t("approvalDetails.reject_btn"), "pi-times-circle", "detail-action-color-3"]
              : ""
          }
          onActionBtn2={() => setDialogStatus(true)}
          additionalDescr={
            <RequestTypeDetails
              request={selectedRequest}
              dataReady={typeDataReady}
              setDataReady={setTypeDataReady}
              setSelectedRequest={setSelectedRow}
              setRequestFiles={setRequestFiles}
              setQuotesList={setQuotesList}
            />
          }
        />
      )}
      <Dialog
        className="custom-main-dialog"
        header={t("approvalDetails.reject_title")}
        visible={dialogStatus}
        onHide={() => {
          setDialogStatus(false);
          setTypeDataReady(false);
        }}
        style={{ width: "40vw" }}
        breakpoints={{ "1280px": "40vw", "960px": "60vw", "768px": "80vw" }}
        footer={renderFooter}
      >
        <div className="p-field">
          <label>{t("approvalDetails.reject_input_title")}</label>
          <CustomTextArea value={rejectReason} onChange={setRejectReason} rows={5} leftStatus />
        </div>
      </Dialog>
    </React.Fragment>
  );
};

export default ApprovalDetails;
