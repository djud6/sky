import React, { useState } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import FileUploadInput from "../../ShareComponents/FileUploadInput";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";
import "../../../styles/helpers/fileInput.scss";

const UploadMaintenanceFiles = ({
  maintenance,
  uploadDialogStatus,
  setUploadDialogStatus,
  setSelectedMaintenance,
  setMaintenances,
  maintenanceStatus,
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
        `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Add/Files/${maintenance.maintenance_id}`,
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
    if (maintenanceStatus === "Outstanding") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/List`;
    } else if (maintenanceStatus === "Completed") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Completed/List`;
    } else if (maintenanceStatus === "search") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/VIN/${maintenance.VIN}`;
    }

    if (requestURL) {
      let response = await axios.get(requestURL, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });

      const maintenances = response.data;
      let selectedMaintenance;
      for (var i in maintenances) {
        if (maintenances[i].maintenance_id === maintenance.maintenance_id) {
          selectedMaintenance = maintenances[i];
        }

        if (maintenances[i].in_house) {
          maintenances[i].vendor_name = "In-house Maintenance";
        } else if (!maintenances[i].in_house && !maintenances[i].vendor_name) {
          if (maintenance[i].vendor_email && !["", "NA"].includes(maintenance[i].vendor_email)) {
            maintenance[i].vendor_name = maintenance[i].vendor_email;
          }
        }
      }

      setSelectedMaintenance(selectedMaintenance);
      setMaintenances(maintenances);
      successAlert("msg", t("maintenanceDetails.upload_files_success"));
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
      header={t("maintenanceDetails.upload_maintenance_header")}
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

export default UploadMaintenanceFiles;
