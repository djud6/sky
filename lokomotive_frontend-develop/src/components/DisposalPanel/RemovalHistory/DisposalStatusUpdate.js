import React, { useState, useEffect, useMemo } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { Dialog } from "primereact/dialog";
import { Button } from "primereact/button";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import { capitalize } from "../../../helpers/helperFunctions";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import RatingDialog from "../../ShareComponents/RatingDialog";
import "../../../styles/dialogStyles.scss";
import "../../../styles/helpers/fileInput.scss";

const FileInput = ({
  fileInputTitle,
  files,
  setFile,
  fileName,
  setFileName,
  fileIndex,
  margin,
}) => {
  const { t } = useTranslation();
  const inputDocHandler = (e) => {
    if (e.target.files[0]) {
      setFile({
        ...files,
        [`file_${fileIndex}`]: e.target.files[0],
      });
      setFileName({
        ...fileName,
        [`file_${fileIndex}`]: e.target.files[0].name,
      });
    }
  };

  return (
    <React.Fragment>
      <label className={`${margin ? margin : ""}`}>{fileInputTitle}</label>
      <div className="custom-file input-files-container">
        <label className="custom-file-label" htmlFor="disposalFile">
          {!fileName[`file_${fileIndex}`]
            ? t("removalHistory.upload_document")
            : fileName[`file_${fileIndex}`]}
        </label>
        <input
          id="disposalFile"
          name="disposalFile"
          type="file"
          accept=".pdf,.doc,.docx"
          className="custom-file-input"
          onChange={inputDocHandler}
        />
      </div>
    </React.Fragment>
  );
};

const ThreeDocsRequired = ({ titles, files, setFiles, filesName, setFilesName }) => {
  return (
    <React.Fragment>
      <FileInput
        fileInputTitle={titles[0]}
        files={files}
        setFile={setFiles}
        fileName={filesName}
        setFileName={setFilesName}
        fileIndex={0}
      />
      <FileInput
        fileInputTitle={titles[1]}
        files={files}
        setFile={setFiles}
        fileName={filesName}
        setFileName={setFilesName}
        fileIndex={1}
        margin="p-mt-3"
      />
      <FileInput
        fileInputTitle={titles[2]}
        files={files}
        setFile={setFiles}
        fileName={filesName}
        setFileName={setFilesName}
        fileIndex={2}
        margin="p-mt-3"
      />
    </React.Fragment>
  );
};

const TwoDocsRequired = ({ titles, files, setFiles, filesName, setFilesName }) => {
  return (
    <React.Fragment>
      <FileInput
        fileInputTitle={titles[0]}
        files={files}
        setFile={setFiles}
        fileName={filesName}
        setFileName={setFilesName}
        fileIndex={0}
      />
      <FileInput
        fileInputTitle={titles[1]}
        files={files}
        setFile={setFiles}
        fileName={filesName}
        setFileName={setFilesName}
        fileIndex={1}
        margin="p-mt-3"
      />
    </React.Fragment>
  );
};

const DisposalStatusUpdate = ({
  disposal,
  completeDialog,
  setCompleteDialog,
  setRemovalData,
  setSelectedAsset,
  setDataReady,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [selectedStatus, setSelectedStatus] = useState(null);
  const [disableButton, setDisableButton] = useState(true);
  const [isRatingFormShown, setIsRatingFormShown] = useState(false);
  const [ratingData, setRatingData] = useState({});
  const [files, setFiles] = useState({
    file_0: null,
    file_1: null,
    file_2: null,
  });
  const [filesName, setFilesName] = useState({
    file_0: null,
    file_1: null,
    file_2: null,
  });

  const statusOptions = useMemo(() => {
    let options = [];
    if (!disposal.vendor) {
      options = [
        {
          name: t("requestProgress.awaiting_approval"),
          code: "awaiting approval",
        },
        {
          name: t("requestProgress.approved"),
          code: "approved",
        },
        {
          name: t("requestProgress.in_transit_to_vendor"),
          code: "in transit - to vendor",
        },
        {
          name: t("requestProgress.at_vendor"),
          code: "at vendor",
        },
        {
          name: t("requestProgress.in_progress"),
          code: "in progress",
        },
        {
          name: t("requestProgress.complete"),
          code: "complete",
        },
        {
          name: t("requestProgress.cancelled"),
          code: "cancelled",
        },
      ].filter((el) => el.code !== disposal.status?.toLowerCase());
    } else {
      if (disposal.status?.toLowerCase() === "awaiting approval") {
        options = [
          {
            name: t("requestProgress.cancelled"),
            code: "cancelled",
          },
        ];
      } else if (disposal.status?.toLowerCase() === "approved") {
        options = [
          {
            name: t("requestProgress.in_transit_to_vendor"),
            code: "in transit - to vendor",
          },
          {
            name: t("requestProgress.cancelled"),
            code: "cancelled",
          },
        ];
      } else if (disposal.status?.toLowerCase() === "in progress") {
        options = [
          {
            name: t("requestProgress.complete"),
            code: "complete",
          },
        ];
      }
    }

    return options;
  }, [disposal, t]);

  useEffect(() => {
    setFiles({
      file_0: null,
      file_1: null,
      file_2: null,
    });
    setFilesName({
      file_0: null,
      file_1: null,
      file_2: null,
    });
  }, [disposal]);

  useEffect(() => {
    if (disposal) {
      if (disposal.disposal_type.toLowerCase() === "company directed sale") {
        if (!files["file_0"] || !files["file_1"] || !files["file_2"]) setDisableButton(true);
        else setDisableButton(false);
      } else if (
        disposal.disposal_type.toLowerCase() === "write-off" ||
        disposal.disposal_type.toLowerCase() === "trade in" ||
        disposal.disposal_type.toLowerCase() === "auction" ||
        disposal.disposal_type.toLowerCase() === "scrap"
      ) {
        if (!files["file_0"] || !files["file_1"]) setDisableButton(true);
        else setDisableButton(false);
      } else if (
        disposal.disposal_type.toLowerCase() === "donate" ||
        disposal.disposal_type.toLowerCase() === "repurpose" ||
        disposal.disposal_type.toLowerCase() === "transfer"
      ) {
        if (!files["file_0"]) setDisableButton(true);
        else setDisableButton(false);
      }
    }
  }, [files, filesName, disposal]);

  const selectStatus = (status) => {
    setSelectedStatus(status);
    if (status !== "complete") {
      setDisableButton(false);
    }
  };

  const disposalUpdate = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    const disposal_data = {
      disposal_id: disposal.id,
      status: selectedStatus ? selectedStatus : disposal.status,
    };

    let required_file_specs = { file_info: [] };
    let required_files = new FormData();

    const getRequiredFiles = (purposes) => {
      purposes.forEach((purpose, index) => {
        required_file_specs["file_info"].push({
          file_name: filesName[`file_${index}`],
          purpose: purpose,
        });
        required_files.append("files", files[`file_${index}`]);
      });
    };

    if (disposal.disposal_type.toLowerCase() === "company directed sale") {
      getRequiredFiles(["bill of sale", "method of payment", "letter of release"]);
      submitUpdateDisposal(
        disposal_data,
        required_file_specs,
        required_files,
        "CompanyDirectedSale"
      );
    } else if (disposal.disposal_type.toLowerCase() === "write-off") {
      getRequiredFiles(["insurance", "total loss declaration"]);
      submitUpdateDisposal(disposal_data, required_file_specs, required_files, "WriteOff");
    } else if (disposal.disposal_type.toLowerCase() === "trade in") {
      getRequiredFiles(["bill of sale", "letter of release"]);
      submitUpdateDisposal(disposal_data, required_file_specs, required_files, "TradeIn");
    } else if (disposal.disposal_type.toLowerCase() === "donate") {
      getRequiredFiles(["tax receipt"]);
      submitUpdateDisposal(disposal_data, required_file_specs, required_files, "Donation");
    } else if (disposal.disposal_type.toLowerCase() === "auction") {
      getRequiredFiles(["bill of sale", "method of payment"]);
      submitUpdateDisposal(disposal_data, required_file_specs, required_files, "Auction");
    } else if (disposal.disposal_type.toLowerCase() === "scrap") {
      getRequiredFiles(["invoice", "proceeds"]);
      submitUpdateDisposal(disposal_data, required_file_specs, required_files, "Scrap");
    } else if (disposal.disposal_type.toLowerCase() === "repurpose") {
      getRequiredFiles(["other"]);
      submitUpdateDisposal(disposal_data, required_file_specs, required_files, "Repurpose");
    } else if (disposal.disposal_type.toLowerCase() === "transfer") {
      getRequiredFiles(["other"]);
      submitUpdateDisposal(disposal_data, required_file_specs, required_files, "Transfer");
    }
  };

  const getVendorRatingInfo = () => {
    const serviceType = "disposal";
    if (disposal.vendor) {
      setIsRatingFormShown(true);
      setRatingData({
        vendor_name: disposal.vendor_name,
        service_type: serviceType,
        request_status: "complete",
        request_id: disposal.custom_id,
      });
    }
  };

  const submitUpdateDisposal = (data, file_specs, form_data, APIsuffix) => {
    form_data.append("instructions", JSON.stringify(data));
    form_data.append("file_specs", JSON.stringify(file_specs));

    loadingAlert();
    const headers = getAuthHeader();
    headers.headers["Content-Type"] = "application/json";
    const requestConfig = {
      method: "post",
      url: `${Constants.ENDPOINT_PREFIX}/api/v1/AssetDisposal/Update/Status/${APIsuffix}`,
      ...headers,
      data: form_data,
    };

    axios(requestConfig)
      .then((response) => {
        setCompleteDialog(false);
        setSelectedAsset({ ...disposal, status: "complete" });
        refreshData();
      })
      .catch((error) => {
        ConsoleHelper(error);
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  const submitVendorRating = (rating, feedback) => {
    const cancelTokenSource = axios.CancelToken.source();
    loadingAlert();
    setRatingData((prev) => {
      prev["rating"] = rating;
      prev["feedback"] = feedback;
      return prev;
    });

    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api-vendor/v1/Ratings/Add`, ratingData, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then(() => {
        setIsRatingFormShown(false);
        setDataReady(false);

        successAlert("msg", t("general.rating_update_success"));
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  const refreshData = async () => {
    const cancelTokenSource = axios.CancelToken.source();
    const response = await axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetDisposal/List`, {
      ...getAuthHeader(),
      cancelToken: cancelTokenSource.token,
    });
    const removalData = response.data;
    let selectedRemoval;
    removalData.forEach((dis, index) => {
      if (dis.id === disposal.id) {
        selectedRemoval = dis;
      }
      return (removalData[index].disposal_type = capitalize(dis.disposal_type));
    });

    setRemovalData(removalData);
    setSelectedAsset(selectedRemoval);

    successAlert("msg", t("removalPanel.success_update_status"), () => {
      if (selectedStatus === "complete") {
        getVendorRatingInfo();
      }
    });
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label="Cancel"
          icon="pi pi-times"
          className="p-button-text"
          onClick={() => {
            setDisableButton(true);
            setSelectedStatus(null);
            setCompleteDialog(false);
          }}
        />
        <Button
          label="Confirm"
          icon="pi pi-check"
          onClick={disposalUpdate}
          disabled={disableButton}
        />
      </div>
    );
  };

  return (
    <>
      <Dialog
        className="custom-main-dialog"
        header={t("removalPanel.update_removal_status")}
        visible={completeDialog}
        onHide={() => {
          setDisableButton(true);
          setSelectedStatus(null);
          setCompleteDialog(false);
        }}
        style={{ width: "50vw" }}
        breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
        footer={renderFooter()}
      >
        <div className="p-field">
          <label className="h6">{t("general.update_status")}</label>
          <FormDropdown
            className="w-100"
            onChange={selectStatus}
            options={statusOptions}
            dataReady={statusOptions.length !== 0 ? true : false}
            plain_dropdown
            leftStatus
            reset={"disabled"}
          />
        </div>
        {selectedStatus === "complete" && (
          <>
            {disposal.disposal_type?.toLowerCase() === "company directed sale" && (
              <ThreeDocsRequired
                titles={[
                  t("removalHistory.upload_bill_of_sale"),
                  t("removalHistory.upload_method_of_payment"),
                  t("removalHistory.upload_letter_of_release"),
                ]}
                files={files}
                setFiles={setFiles}
                filesName={filesName}
                setFilesName={setFilesName}
              />
            )}
            {disposal.disposal_type?.toLowerCase() === "write-off" && (
              <TwoDocsRequired
                titles={[
                  t("removalHistory.upload_insurance_document"),
                  t("removalHistory.upload_total_loss_declaration"),
                ]}
                files={files}
                setFiles={setFiles}
                filesName={filesName}
                setFilesName={setFilesName}
              />
            )}
            {disposal.disposal_type?.toLowerCase() === "trade in" && (
              <TwoDocsRequired
                titles={[
                  t("removalHistory.upload_bill_of_sale_trade"),
                  t("removalHistory.upload_letter_of_release"),
                ]}
                files={files}
                setFiles={setFiles}
                filesName={filesName}
                setFilesName={setFilesName}
              />
            )}
            {disposal.disposal_type?.toLowerCase() === "auction" && (
              <TwoDocsRequired
                titles={[
                  t("removalHistory.upload_bill_of_sale"),
                  t("removalHistory.upload_method_of_payment"),
                ]}
                files={files}
                setFiles={setFiles}
                filesName={filesName}
                setFilesName={setFilesName}
              />
            )}
            {disposal.disposal_type?.toLowerCase() === "scrap" && (
              <TwoDocsRequired
                titles={[t("removalHistory.upload_invoice"), t("removalHistory.upload_proceeds")]}
                files={files}
                setFiles={setFiles}
                filesName={filesName}
                setFilesName={setFilesName}
              />
            )}
            {disposal.disposal_type?.toLowerCase() === "donate" && (
              <FileInput
                fileInputTitle={t("removalHistory.upload_tax_receipt")}
                files={files}
                setFile={setFiles}
                fileName={filesName}
                setFileName={setFilesName}
                fileIndex={0}
              />
            )}
            {disposal.disposal_type?.toLowerCase() === "repurpose" && (
              <FileInput
                fileInputTitle={t("removalHistory.upload_other")}
                files={files}
                setFile={setFiles}
                fileName={filesName}
                setFileName={setFilesName}
                fileIndex={0}
              />
            )}
            {disposal.disposal_type?.toLowerCase() === "transfer" && (
              <FileInput
                fileInputTitle={t("removalHistory.upload_other")}
                files={files}
                setFile={setFiles}
                fileName={filesName}
                setFileName={setFilesName}
                fileIndex={0}
              />
            )}
          </>
        )}
      </Dialog>
      {isRatingFormShown && (
        <RatingDialog
          headerTitle={t("general.rate_vendor")}
          data={ratingData}
          btn1Label={t("general.skip")}
          btn1Action={() => {
            setDataReady(false);
          }}
          btn2Action={(rating, feedback) => {
            submitVendorRating(rating, feedback);
          }}
        />
      )}
    </>
  );
};

export default DisposalStatusUpdate;
