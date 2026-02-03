import React, { useState } from "react";
import axios from "axios";
import swal from "sweetalert";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../constants";
import { CTRL_AUDIO_PLAY } from "../../redux/types/audioTypes";
import { getAuthHeader } from "../../helpers/Authorization";
import { faEnvelope } from "@fortawesome/free-solid-svg-icons";
import PanelHeader from "../ShareComponents/helpers/PanelHeader";
import Tooltip from "../ShareComponents/Tooltip/Tooltip";
import FileUploadInput from "../ShareComponents/FileUploadInput";
import CustomTextArea from "../ShareComponents/CustomTextArea";
import CustomInputText from "../ShareComponents/CustomInputText";
import FormDropdown from "../ShareComponents/Forms/FormDropdown";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import "../../styles/FeedbackPanel.scss";
import "../../styles/helpers/button1.scss";
import "../../styles/helpers/fileInput.scss";

const FeedbackPanel = () => {
  const { t } = useTranslation();
  return (
    <div className="feedback-panel">
      <PanelHeader icon={faEnvelope} text={t("feedbackPanel.panel_header")} disableBg />
      <div>
        <FeedbackForm />
      </div>
    </div>
  );
};

const FeedbackForm = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [description, setDescription] = useState("");
  const [steps, setSteps] = useState("");
  const [title, setTitle] = useState("");
  const [issueType, setIssueType] = useState("");
  const [photos, setPhotos] = useState([]);
  const [photoNames, setPhotoNames] = useState([]);
  const [fileLoading, setFileLoading] = useState(false);
  const [formReset, setFormReset] = useState(Date.now());
  const isBigScreen = useMediaQuery({ query: "(min-width: 1315px)" });
  const typeOptions = [
    {
      name: isBigScreen
        ? t("feedbackPanel.label_critical_desk")
        : t("feedbackPanel.label_critical"),
      code: t("feedbackPanel.label_critical"),
    },
    {
      name: isBigScreen
        ? t("feedbackPanel.label_undesired_desk")
        : t("feedbackPanel.label_undesired"),
      code: t("feedbackPanel.label_undesired"),
    },
    {
      name: isBigScreen
        ? t("feedbackPanel.label_feedback_desk")
        : t("feedbackPanel.label_feedback"),
      code: t("feedbackPanel.label_feedback"),
    },
  ];

  const resetForm = () => {
    setDescription("");
    setIssueType("");
    setTitle("");
    setSteps("");
    setPhotos([]);
    setPhotoNames([]);
    setFormReset(Date.now());
  };

  const handleSubmit = (event) => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    event.preventDefault();
    let feedbackReport = new FormData();
    feedbackReport.append(
      "data",
      JSON.stringify({
        issue_type: issueType.toLowerCase(),
        error_title: title,
        error_description: description,
        steps_to_reproduce: steps,
      })
    );
    for (let i = 0; i < photos.length; i++) {
      feedbackReport.append("files", photos[i]);
    }
    sendFeedbackReport(feedbackReport);
  };

  const sendFeedbackReport = (feedbackReport) => {
    loadingAlert();
    const headers = getAuthHeader();
    headers.headers["Content-Type"] = "application/json";
    const requestConfig = {
      method: "post",
      url: `${Constants.ENDPOINT_PREFIX}/api/v1/ErrorReport/Create`,
      ...headers,
      data: feedbackReport,
    };
    axios(requestConfig)
      .then(() => {
        successAlert();
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
      })
      .catch((error) => {
        errorAlert(error.customErrorMsg, feedbackReport);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  const loadingAlert = () => {
    return swal({
      title: t("general.sending_request"),
      text: t("general.please_wait"),
      button: false,
      closeOnClickOutside: false,
      closeOnEsc: false,
    });
  };

  const errorAlert = (errorMsg, data) => {
    return swal({
      title: t("general.error"),
      text: errorMsg,
      icon: "error",
      buttons: { resend: t("general.try_again"), cancel: t("general.cancel") },
    }).then((value) => {
      if (value === "resend") sendFeedbackReport(data);
    });
  };

  const successAlert = () => {
    return swal({
      title: t("general.success"),
      text: t("general.your_feedback_has_been_submitted"),
      icon: "success",
      buttons: { return: t("general.return") },
    }).then((value) => {
      switch (value) {
        case "return":
          resetForm();
          break;
        default:
          resetForm();
      }
    });
  };

  return (
    <div className="p-d-flex p-jc-center">
      <form className="p-d-flex p-flex-column form-container" onSubmit={handleSubmit}>
        <div className="form-q-wrapper w-100 p-d-flex p-flex-wrap">
          <label className="form-q">{t("feedbackPanel.feedback_input_title")}</label>
          <div className="form-input">
            <CustomInputText
              placeholder={t("feedbackPanel.feedback_input_placeholder")}
              onChange={setTitle}
              value={title}
              leftStatus
            />
          </div>
        </div>
        <div className="form-q-wrapper w-100 p-d-flex p-flex-wrap">
          <div className="form-q">
            <label>{t("feedbackPanel.type_input_title")}</label>
            {!isBigScreen && (
              <Tooltip
                label={"upload-tooltip"}
                description={`${t("feedbackPanel.label_critical_desk")}. ${t(
                  "feedbackPanel.label_undesired_desk"
                )}. ${t("feedbackPanel.label_feedback_desk")}.`}
              />
            )}
          </div>
          <div className="form-input">
            <FormDropdown
              onChange={(type) => setIssueType(type)}
              options={typeOptions}
              plain_dropdown
              leftStatus
              reset={formReset}
            />
          </div>
        </div>
        <div className="form-q-wrapper w-100 p-d-flex p-flex-wrap">
          <label className="form-q">{t("feedbackPanel.description_input_title")}</label>
          <div className="form-input">
            <CustomTextArea
              rows="8"
              placeholder={t("feedbackPanel.description_placeholder")}
              value={description}
              onChange={setDescription}
              leftStatus
            />
          </div>
        </div>
        <div className="form-q-wrapper w-100 p-d-flex p-flex-wrap">
          <label className="form-q">{t("feedbackPanel.steps_input_title")}</label>
          <div className="form-input">
            <CustomTextArea
              rows="8"
              placeholder={t("feedbackPanel.steps_placeholder")}
              value={steps}
              onChange={setSteps}
              leftStatus
            />
          </div>
        </div>
        <div className="form-q-wrapper w-100 p-d-flex p-flex-wrap">
          <label className="form-q">{t("feedbackPanel.screenshots_input_title")}</label>
          <div className="form-input custom-file input-files-container ">
            <FileUploadInput
              images={photos}
              setImages={setPhotos}
              imageNames={photoNames}
              setImageNames={setPhotoNames}
              fileLoading={fileLoading}
              setFileLoading={setFileLoading}
              fileTypes="image/*,.heic"
              maxNumberOfFiles={10}
            />
          </div>
        </div>
        <div className="p-d-flex p-jc-center submit-btn btn-1 p-mb-5">
          <Button label="Submit" icon="pi pi-send" disabled={fileLoading} />
        </div>
      </form>
    </div>
  );
};

export default FeedbackPanel;
