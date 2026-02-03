import React, { useState } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import FileUploadInput from "../../ShareComponents/FileUploadInput";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import CustomInputText from "../../ShareComponents/CustomInputText";
import { RadioButton } from "primereact/radiobutton";
import "../../../styles/dialogStyles.scss";
import "../../../styles/helpers/fileInput.scss";
import "../../../styles/helpers/radiobutton.scss";

const TransferStatusUpdate = ({
  transfer,
  updateDialogStatus,
  setUpdateDialogStatus,
  setSelectedTransfer,
  setTransfers,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [docReq, setDocReq] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState(null);
  const [files, setFiles] = useState([]);
  const [fileNames, setFileNames] = useState([]);
  const [fileLoading, setFileLoading] = useState(false);
  const [interiorCond, setInteriorCond] = useState({});
  const [interiorDets, setInteriorDets] = useState("");
  const [exteriorCond, setExteriorCond] = useState({});
  const [exteriorDets, setExteriorDets] = useState("");
  const [mileage, setMileage] = useState(0);
  const [hours, setHours] = useState(0);

  let statusOptions;
  if (transfer.status.toLowerCase() === "awaiting approval") {
    statusOptions = [
      {
        name: t("requestProgress.cancelled"),
        code: "cancelled",
      },
    ];
  } else if (transfer.status.toLowerCase() === "approved") {
    statusOptions = [
      {
        name: t("requestProgress.cancelled"),
        code: "cancelled",
      },
      {
        name: t("requestProgress.awaiting_transfer"),
        code: "awaiting transfer",
      },
    ];
  } else if (transfer.status.toLowerCase() === "awaiting transfer") {
    statusOptions = [
      {
        name: t("requestProgress.in_transit"),
        code: "in transit",
      },
    ];
  } else if (transfer.status.toLowerCase() === "in transit") {
    statusOptions = [
      {
        name: t("requestProgress.delivered"),
        code: "delivered",
      },
    ];
  } else if (transfer.status.toLowerCase() === "delivered") {
    statusOptions = [
      {
        name: t("requestProgress.delivered"),
        code: "delivered",
      },
    ];
  }

  const interiorConditionStatus = [
    { name: t("removalPanel.condition_poor"), code: "i_poor" },
    { name: t("removalPanel.condition_avg"), code: "i_avg" },
    { name: t("removalPanel.condition_good"), code: "i_good" },
    { name: t("removalPanel.condition_na"), code: "i_na" },
  ];
  const exteriorConditionStatus = [
    { name: t("removalPanel.condition_poor"), code: "e_poor" },
    { name: t("removalPanel.condition_avg"), code: "e_avg" },
    { name: t("removalPanel.condition_good"), code: "e_good" },
    { name: t("removalPanel.condition_na"), code: "e_na" },
  ];

  const handleStatusUpdate = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });

    let data = {
      transfer_id: transfer.asset_transfer_id,
      status: selectedStatus,
      interior_condition: interiorCond.name && interiorCond.name.toLowerCase(),
      exterior_condition: exteriorCond.name && exteriorCond.name.toLowerCase(),
      interior_condition_details: interiorDets,
      exterior_condition_details: exteriorDets,
      mileage: parseFloat(mileage),
      hours: parseFloat(hours),
    };
    let updateData = new FormData();
    updateData.append("data", JSON.stringify(data));
    if (files.length > 0) {
      let required_file_specs = {
        file_info: [],
      };
      for (let i = 0; i < files.length; i++) {
        required_file_specs.file_info.push({ file_name: files[i].name, purpose: "other" });
        updateData.append("files", files[i]);
      }
      updateData.append("file_specs", JSON.stringify(required_file_specs));
    } else {
      updateData.append("file_specs", "{}");
      updateData.append("files", {});
    }
    handleSubmit(updateData);
  };

  const handleSubmit = (data) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Transfer/Update/Status`, data, getAuthHeader())
      .then(() => {
        setUpdateDialogStatus(false);
        refreshData(data);
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  const refreshData = async (data) => {
    const cancelTokenSource = axios.CancelToken.source();
    let requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Transfer/List`;

    let response = await axios.get(requestURL, {
      ...getAuthHeader(),
      cancelToken: cancelTokenSource.token,
    });

    const transfers = response.data;
    let selectedTransfer;
    for (var i in transfers) {
      if (transfers[i].asset_transfer_id === JSON.parse(data.get("data")).transfer_id) {
        selectedTransfer = transfers[i];
      }
    }
    setSelectedTransfer(selectedTransfer);
    setTransfers(transfers);
    successAlert("msg", t("assetTransferPanel.update_success_text"));
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
  };

  const renderFooter = () => {
    return (
      <Button
        label={t("general.update")}
        icon="pi pi-check"
        className="p-button-success p-mt-4"
        onClick={() => {
          handleStatusUpdate();
        }}
        disabled={!(selectedStatus && (!docReq || files.length > 0)) || fileLoading}
      />
    );
  };

  const selectStatus = (status) => {
    if (status === "cancelled") setDocReq(false);
    else setDocReq(true);
    setSelectedStatus(status);
  };

  return (
    <div>
      <Dialog
        className="custom-main-dialog"
        header={t("assetTransferPanel.transfer_status_update")}
        visible={updateDialogStatus}
        footer={renderFooter}
        onHide={() => setUpdateDialogStatus(false)}
        style={{ width: "40vw" }}
        breakpoints={{ "1280px": "40vw", "960px": "60vw", "768px": "80vw" }}
      >
        <div className="p-field">
          <label>{t("general.update_status")}</label>
          <FormDropdown
            className="w-100"
            onChange={selectStatus}
            options={statusOptions}
            dataReady={statusOptions}
            plain_dropdown
            leftStatus
          />
        </div>
        <div className="p-field">
          <label>{t("general.add_supporting_file")}</label>
          <div className="custom-file input-files-container">
            <FileUploadInput
              images={files}
              setImages={setFiles}
              imageNames={fileNames}
              setImageNames={setFileNames}
              fileLoading={fileLoading}
              setFileLoading={setFileLoading}
              fileTypes=".pdf, image/*, .heic"
              maxNumberOfFiles={10}
            />
          </div>
        </div>
        {selectedStatus === "in transit" && (
          <React.Fragment>
            <hr />
            <h4 className="font-weight-bold p-mb-3">
              {t("assetTransferPanel.asset_condition_check")}
            </h4>
            <label>{t("removalPanel.interior_condition_of_the_asset")}</label>
            <div className="p-d-flex p-flex-wrap">
              {interiorConditionStatus.map((status) => {
                return (
                  <div key={status.code} className="darkRadio p-d-flex p-ai-center p-my-1">
                    <RadioButton
                      inputId={status.code}
                      name="status"
                      value={status}
                      onChange={(e) => setInteriorCond(e.value)}
                      checked={interiorCond.code === status.code}
                    />
                    <label className="mb-0 ml-2 mr-3" htmlFor={status.code}>
                      {status.name}
                    </label>
                  </div>
                );
              })}
            </div>
            <label className="p-mt-2">{t("removalPanel.interior_condition_details")}</label>
            <div className="txtField-2">
              <CustomTextArea
                className="w-100"
                value={interiorDets}
                onChange={setInteriorDets}
                leftStatus
              />
            </div>
            <label className="p-mt-2">{t("removalPanel.exterior_condition_of_the_asset")}</label>
            <div className="p-d-flex p-flex-wrap">
              {exteriorConditionStatus.map((status) => {
                return (
                  <div key={status.code} className="darkRadio p-d-flex p-ai-center p-my-1">
                    <RadioButton
                      inputId={status.code}
                      name="status"
                      value={status}
                      onChange={(e) => setExteriorCond(e.value)}
                      checked={exteriorCond.code === status.code}
                    />
                    <label className="mb-0 ml-2 mr-3" htmlFor={status.code}>
                      {status.name}
                    </label>
                  </div>
                );
              })}
            </div>
            <label className="p-mt-2">{t("removalPanel.exterior_condition_details")}</label>
            <div className="txtField-2">
              <CustomTextArea
                className="w-100"
                value={exteriorDets}
                onChange={setExteriorDets}
                leftStatus
              />
            </div>
            <label className="h5 p-mt-3 font-weight-bold">{t("general.mileage")}</label>
            <div className="txtField-2">
              <CustomInputText
                className="w-100"
                keyfilter={/^\d*\.?\d*$/}
                onChange={setMileage}
                leftStatus
              />
            </div>
            <label className="h5 p-mt-3 font-weight-bold">{t("general.hours")}</label>
            <div className="txtField-2">
              <CustomInputText
                className="w-100"
                keyfilter={/^\d*\.?\d*$/}
                onChange={setHours}
                leftStatus
              />
            </div>
          </React.Fragment>
        )}
      </Dialog>
    </div>
  );
};

export default TransferStatusUpdate;
