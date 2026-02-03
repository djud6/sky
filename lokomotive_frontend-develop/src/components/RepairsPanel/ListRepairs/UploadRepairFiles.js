import React, { useState } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import FileUploadInput from "../../ShareComponents/FileUploadInput";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";
import "../../../styles/helpers/fileInput.scss";

const UploadRepairFiles = ({
  repair,
  uploadDialogStatus,
  setUploadDialogStatus,
  setSelectedRepair,
  setRepairRequests,
  category,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [files, setFiles] = useState([]);
  const [fileNames, setFileNames] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [invoicesNames, setInvoicesNames] = useState([]);

  const handleUploadData = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let newFiles = new FormData();
    let required_file_specs = {
      file_info: [],
    };
    if (files.length > 0) {
      for (let i = 0; i < files.length; i++) {
        required_file_specs.file_info.push({ file_name: files[i].name, purpose: "other" });
        newFiles.append("files", files[i]);
      }
      newFiles.append("file_specs", JSON.stringify(required_file_specs));
    }
    if (invoices.length > 0) {
      for (let i = 0; i < invoices.length; i++) {
        required_file_specs.file_info.push({ file_name: invoices[i].name, purpose: "invoice" });
        newFiles.append("files", invoices[i]);
      }
      newFiles.append("file_specs", JSON.stringify(required_file_specs));
    }

    handleSubmit(newFiles);
  };

  const handleSubmit = (data) => {
    loadingAlert();
    axios
      .post(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Add/Files/${repair.repair_id}`,
        data,
        getAuthHeader()
      )
      .then((res) => {
        setUploadDialogStatus(false);
        refreshData();
      })
      .catch((error) => {
        ConsoleHelper(error);
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  const refreshData = async () => {
    // reset fields
    setFiles([]);
    setFileNames([]);
    setInvoices([]);
    setInvoicesNames([]);

    const cancelTokenSource = axios.CancelToken.source();
    let requestURL;
    if (category === "inProgress") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/List`;
    } else if (category === "completed") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Complete/List`;
    }

    if (requestURL) {
      let response = await axios.get(requestURL, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });

      const repairs = response.data;
      let selectedRepair;
      if (category === "inProgress") {
        for (var i in repairs) {
          if (repairs[i].repair_id === repair.repair_id) {
            selectedRepair = repairs[i];
          }
          if (repairs[i].is_urgent) repairs[i].is_urgent = "Yes";
          else repairs[i].is_urgent = "No";

          if (repairs[i].in_house) {
            repairs[i].vendor_name = "In-house Repair";
          } else if (!repairs[i].in_house && !repairs[i].vendor_name) {
            if (repairs[i].vendor_email && !["", "NA"].includes(repairs[i].vendor_email)) {
              repairs[i].vendor_name = repairs[i].vendor_email;
            }
          }
        }
      } else if (category === "completed") {
        for (var y in repairs) {
          if (repairs[y].repair_id === repair.repair_id) {
            selectedRepair = repairs[y];
          }
          if (repairs[y].in_house) {
            repairs[y].vendor_name = "In-house Repair";
          } else if (!repairs[y].in_house && !repairs[y].vendor_name) {
            if (repairs[y].vendor_email && !["", "NA"].includes(repairs[y].vendor_email)) {
              repairs[y].vendor_name = repairs[y].vendor_email;
            }
          }
        }
      }

      setSelectedRepair(selectedRepair);
      setRepairRequests(repairs);
      successAlert("msg", t("repairDetails.upload_files_success"));
      dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
    }
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label={t("general.cancel")}
          icon="pi pi-times"
          onClick={() => setUploadDialogStatus(false)}
          className="p-button-text"
        />
        <Button
          label={t("general.submit")}
          icon="pi pi-check"
          onClick={handleUploadData}
          disabled={files.length === 0 && invoices.length === 0}
          autoFocus
        />
      </div>
    );
  };

  return (
    <Dialog
      className="custom-main-dialog"
      header={t("repairDetails.upload_repair_header")}
      visible={uploadDialogStatus}
      onHide={() => setUploadDialogStatus(false)}
      style={{ width: "50vw" }}
      breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
      footer={renderFooter}
    >
      <div className="p-field">
        <label>{t("general.add_supporting_file")}</label>
        <div className="custom-file input-files-container">
          <FileUploadInput
            images={files}
            setImages={setFiles}
            imageNames={fileNames}
            setImageNames={setFileNames}
            fileTypes=".pdf,.doc,.docx"
            maxNumberOfFiles={10}
          />
        </div>
      </div>
      <div className="p-field">
        <label>{t("general.add_invoice_doc")}</label>
        <div className="custom-file input-files-container">
          <FileUploadInput
            images={invoices}
            setImages={setInvoices}
            imageNames={invoicesNames}
            setImageNames={setInvoicesNames}
            fileTypes=".pdf,.doc,.docx"
            maxNumberOfFiles={10}
          />
        </div>
      </div>
    </Dialog>
  );
};

export default UploadRepairFiles;
