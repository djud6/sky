import React, { useState } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import CustomInputText from "../../ShareComponents/CustomInputText";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import GeneralRadio from "../../ShareComponents/GeneralRadio";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";

const UpdateIssue = ({
  issue,
  editDialogStatus,
  setEditDialogStatus,
  setSelectedIssue,
  setIssues,
  issuePanel,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [title, setTitle] = useState(issue.issue_title);
  const [description, setDescription] = useState(issue.issue_details);
  const [criticalIssue, setCriticalIssue] = useState(issue.issue_type === "Critical");

  const renderFooter = (cancelAction, confirmAction) => {
    return (
      <div>
        <Button
          label="Cancel"
          icon="pi pi-times"
          onClick={() => cancelAction(false)}
          className="p-button-text"
        />
        <Button
          label="Confirm"
          icon="pi pi-check"
          onClick={() => confirmAction()}
          autoFocus
          disabled={!title || !description}
        />
      </div>
    );
  };

  const handleUpdateDetails = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let issueDetails = {
      issue_id: issue.issue_id,
      issue_title: title,
      issue_details: description,
      ...(criticalIssue
        ? { issue_type: t("general.critical") }
        : { issue_type: t("general.non_critical") }),
    };
    handleUpdateSubmit(issueDetails);
  };

  const handleUpdateSubmit = (data) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Issues/Update`, data, getAuthHeader())
      .then((res) => {
        setEditDialogStatus(false);
        refreshData();
      })
      .catch((error) => {
        ConsoleHelper(error);
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  const refreshData = async () => {
    const cancelTokenSource = axios.CancelToken.source();
    let response;
    if (issuePanel === "all") {
      response = await axios.post(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Issues/List/Type`,
        {},
        { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
      );
    } else if (issuePanel === "search") {
      response = await axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Issues/VIN/${issue.VIN}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });
    }

    const getIssues = response.data;
    const filteredIssue = getIssues.filter((i) => 
      i.issue_id === issue.issue_id
    );

    setSelectedIssue(filteredIssue[0]);
    setIssues(getIssues);
    successAlert(t("issueDetails.update_success_text"));
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
  };

  return (
    <div>
      {/* Edit Details Dialog */}
      <Dialog
        className="custom-main-dialog"
        header={t("issueDetails.edit_issue_header")}
        visible={editDialogStatus}
        onHide={() => setEditDialogStatus(false)}
        style={{ width: "50vw" }}
        breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
        footer={renderFooter(setEditDialogStatus, handleUpdateDetails)}
      >
        <div className="p-field">
          <label>{t("general.issue_title")}</label>
          <CustomInputText
            className="w-100"
            value={title}
            onChange={(val) => {
              if (val.trim() === "") {
                val = "";
              }
              setTitle(val);
            }}
            required
            leftStatus
          />
        </div>
        <div className="p-field">
          <label>{t("reportIssuePanel.issue_description")}</label>
          <CustomTextArea
            className="w-100"
            rows={5}
            value={description}
            onChange={setDescription}
            required
            leftStatus
          />
        </div>
        <div className="p-field">
          <GeneralRadio
            value={criticalIssue}
            onChange={setCriticalIssue}
            name={"criticalIssueRadio"}
            labels={[
              t("reportIssuePanel.critical_issue_question"),
              t("general.critical"),
              t("general.non_critical"),
            ]}
          />
        </div>
      </Dialog>
    </div>
  );
};

export default UpdateIssue;
