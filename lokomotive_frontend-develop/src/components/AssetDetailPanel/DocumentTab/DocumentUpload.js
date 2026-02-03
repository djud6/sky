import React, { useState } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dropdown } from "primereact/dropdown";
import * as Constants from "../../../constants";
import { Checkbox } from "primereact/checkbox";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import CardWidget from "../../ShareComponents/CardWidget";
import DatePicker from "../../ShareComponents/DatePicker";
import FileUploadInput from "../../ShareComponents/FileUploadInput";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/fileInput.scss";
import "../../../styles/helpers/button5.scss";
import "../../../styles/helpers/checkbar.scss";


const DocumentUpload = ({ vin, setDataReady }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [selectedDocType, setSelectedDocType] = useState(null);
  const [document, setDocument] = useState([]);
  const [documentName, setDocumentName] = useState([]);
  const [expireDate, setExpireDate] = useState(null);
  const [selectedApplyToSimilar, setSelectedApplyToSimilar] = useState(false);
  const documentTypes = [
    t("documentTab.registration"),
    t("documentTab.insurance"),
    t("documentTab.warranty"),
    t("documentTab.other"),
  ];

  const handleSubmit = (event) => {
    event.preventDefault();
    let docsToUpload = new FormData();
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });


    docsToUpload.append("files", document[0]);

    if(expireDate){
      docsToUpload.append(
        "data",
        JSON.stringify({
          expiration_date: expireDate.toISOString().split("T")[0],
        })
      );
    }


    const headers = getAuthHeader();
    headers.headers["Content-Type"] = "application/json";
    const requestConfig = {
      method: "post",
      url: `${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Add/${selectedDocType}/${vin}`,
      ...headers,
      data: docsToUpload,
      apply_to_similar_type: selectedApplyToSimilar,
    };
    uploadFile(requestConfig);
  };

  const uploadFile = (requestConfig) => {
    loadingAlert();
    axios(requestConfig)
      .then((res) => {
        setDataReady(false);
        successAlert(t("documentTab.upload_document"));
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
        setSelectedDocType(null);
        setDocument([]);
        setDocumentName([]);
        setExpireDate(null);
      })
      .catch((err) => {
        generalErrorAlert(err.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(err);
      })
  };

  return (
    <div className="upload-form">
      <form onSubmit={handleSubmit}>
        <CardWidget status={selectedDocType} blueBg>
          <label className="form-q">{t("documentTab.select_document_type")}</label>
          <div className="w-100">
            <Dropdown
              panelClassName="dropdown-content-form"
              className={`w-100 
                ${selectedDocType ? "activated-styles-inner " : "default-styles-inner"}
              `}
              value={selectedDocType}
              options={documentTypes}
              onChange={(e) => setSelectedDocType(e.value)}
              placeholder={t("documentTab.select_document_type")}
            />
          </div>
        </CardWidget>
        <CardWidget status={document.length!==0} blueBg>
          <label className="form-q">{t("documentTab.upload_document")}</label>
          <div className="custom-file input-files-container">
            <FileUploadInput
              images={document}
              setImages={setDocument}
              imageNames={documentName}
              setImageNames={setDocumentName}
              fileTypes=".pdf,.doc,.docx"
              maxNumberOfFiles={1}
            />
          </div>
        </CardWidget>
        <CardWidget status={expireDate} blueBg>
          <label className="form-q">{t("documentTab.select_expiry_date")}</label>
          <div className="">
            <DatePicker
              onChange={setExpireDate}
              initialDate={expireDate}
              minDate={new Date()}
            />
          </div>
        </CardWidget>
        <div className="p-d-flex p-jc-end p-mt-3 sub-form apply-similar">
                <div className="p-d-flex">
                  <Checkbox
                    onChange={(e) => setSelectedApplyToSimilar(e.checked)}
                    checked={selectedApplyToSimilar}
                  />
                  <div className="apply-text">
                    {t("maintenanceForecastPanel.apply_to_all_label")}
                  </div>
                  <Tooltip
                    label={"tooltip-all"}
                    description={t("maintenanceForecastPanel.tooltip_apply_all")}
                  />
                </div>
              </div>
        <div className="btn-5 p-d-flex p-jc-end p-mt-5">
          <Button
            disabled={!selectedDocType || document.length===0 || (!expireDate && selectedDocType!= t("documentTab.other"))}
            type="submit"
            label={t("documentTab.upload_document")}
          />
        </div>
      </form>
    </div>
  )
}

export default DocumentUpload;
