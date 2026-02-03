import React, { useEffect, useState } from "react";
import axios from "axios";
import swal from "sweetalert";
import * as Constants from "../../../constants";
import { useTranslation } from "react-i18next";
import { useHistory } from "react-router-dom";
import { useDispatch } from "react-redux";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import { TabView, TabPanel } from "primereact/tabview";
import { RadioButton } from "primereact/radiobutton";
import StarRating from "react-svg-star-rating";
import { FaExclamationTriangle, FaCheckCircle } from "react-icons/fa";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faLeaf } from "@fortawesome/free-solid-svg-icons";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import { loadingAlert } from "../../ShareComponents/CommonAlert";
import Table from "../../ShareComponents/Table/Table";
import Spinner from "../../ShareComponents/Spinner";
import CardWidget from "../../ShareComponents/CardWidget";
import WarningMsg from "../../ShareComponents/WarningMsg";
import ChecklistItem from "../../ShareComponents/ChecklistItem";
import DatePicker from "../../ShareComponents/DatePicker";
import VINLink from "../../ShareComponents/helpers/VINLink";
import MultiSelectDropdown from "../../ShareComponents/Forms/MultiSelectDropdown";
import CustomInputText from "../../ShareComponents/CustomInputText";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import CustomInputNumber from "../../ShareComponents/CustomInputNumber";
import FileUploadInput from "../../ShareComponents/FileUploadInput";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import colorVars from "../../../styles/variables.scss";

const RepairRequestForm = ({ issues, vehicle, resetForm, setSubmitSuccessForceUpdate }) => {
  const history = useHistory();
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [requestedDeliveryDate, setRequestedDeliveryDate] = useState(null);
  const [pickupDate, setPickupDate] = useState(null);
  const [quoteDeadline, setQuoteDeadline] = useState(null);
  const [mileage, setMileage] = useState(null);
  const [hours, setHours] = useState(null);
  const [files, setFiles] = useState([]);
  const [fileNames, setFileNames] = useState([]);
  const [fileLoading, setFileLoading] = useState(false);
  const [urgent, setUrgent] = useState("");
  const [description, setDescription] = useState("");
  const [vendorEmail, setVendorEmail] = useState("");
  const [inHouse, setInHouse] = useState(null);
  const [approvedVendors, setApprovedVendors] = useState(null);
  const [dataReady, setDataReady] = useState(false);
  const [dataLoadingError, setDataLoadingError] = useState(false);
  const [replaceAssets, setReplaceAssets] = useState([]);
  const [showRecommends, setShowRecommends] = useState(false);
  const [isUrgentRepairRequire, setIsUrgentRepairRequire] = useState(true);
  const [validationWarningMsg, setValidationWarningMsg] = useState(null);
  const [validationSearch, setValidationSearch] = useState(false);
  const [disableBtn, setDisableBtn] = useState(true);
  const [multiSelectedVendor, setMultiSelectedVendor] = useState([]);
  const [approvedVendor, setApprovedVendor] = useState(null);
  const [vendorTransportToVendor, setVendorTransportToVendor] = useState(null);
  const [vendorTransportToClient, setVendorTransportToClient] = useState(null);
  const [estimatedCost, setEstimatedCost] = useState(null);
  const emailPattern = new RegExp("[a-z0-9._%+-]+@[a-z0-9.-]+.[a-z]{2,4}$");

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    setDataReady(false);
    setDataLoadingError(false);
    setReplaceAssets([]);
    setIsUrgentRepairRequire(true);

    let replacementAPI = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Replacement/Suggestions/${vehicle.VIN}`,
      getAuthHeader()
    );
    let approvedVendorsAPI = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/ApprovedVendor/List/By/Task/repair`,
      getAuthHeader()
    );

    axios
      .all([replacementAPI, approvedVendorsAPI])
      .then(
        axios.spread((...responses) => {
          setReplaceAssets(responses[0].data);
          setIsUrgentRepairRequire(
            responses[0].data.replacements_ordered_by_mileage.length === 0 &&
              responses[0].data.replacements_ordered_by_hours.length === 0
          );
          const approvedVendorAPIResponse = !!responses[1] ? responses[1].data : null;
          setApprovedVendors(approvedVendorAPIResponse);
          setDataReady(true);
        })
      )
      .catch((err) => {
        setDataLoadingError(true);
        ConsoleHelper(err);
      });

    return () => {
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [vehicle.VIN]);

  useEffect(() => {
    if (mileage || hours) {
      if (vehicle.hours_or_mileage.toLowerCase() === "both" && !hours) {
        setValidationWarningMsg("Please provide hours for auto-validation.");
      } else if (vehicle.hours_or_mileage.toLowerCase() === "both" && !mileage) {
        setValidationWarningMsg("Please provide mileage for auto-validation.");
      } else {
        const delayDebounceFn = setTimeout(() => {
          setDataReady(false);
          setValidationSearch(true);
          setValidationWarningMsg(null);
          axios
            .post(
              `${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Validate/Usage`,
              {
                VIN: vehicle.VIN,
                mileage: parseFloat(mileage),
                hours: parseFloat(hours),
              },
              getAuthHeader()
            )
            .then((response) => {
              setValidationSearch(false);
              setDataReady(true);
            })
            .catch((error) => {
              setValidationWarningMsg(error.customErrorMsg);
              setValidationSearch(false);
              setDataReady(true);
              ConsoleHelper(error);
            });
        }, 1000);
        return () => clearTimeout(delayDebounceFn);
      }
    }
  }, [mileage, hours]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (
      fileLoading ||
      !dataReady ||
      !inHouse ||
      (inHouse === t("general.yes") && estimatedCost === null) ||
      (inHouse === t("general.no") &&
        (!approvedVendor ||
          vendorTransportToVendor === null ||
          (vendorTransportToVendor !== null && !pickupDate) ||
          vendorTransportToClient === null ||
          (vendorTransportToClient !== null && !requestedDeliveryDate))) ||
      !description ||
      !quoteDeadline ||
      urgent === "" ||
      (vehicle.hours_or_mileage.toLowerCase() === "both" && (!mileage || !hours)) ||
      (vehicle.hours_or_mileage.toLowerCase() === "mileage" && !mileage) ||
      (vehicle.hours_or_mileage.toLowerCase() === "hours" && !hours)
    ) {
      setDisableBtn(true);
    } else if (inHouse === t("general.no") && approvedVendor) {
      if (approvedVendor === t("general.approved_vendors")) {
        !multiSelectedVendor.length ? setDisableBtn(true) : setDisableBtn(false);
      } else if (approvedVendor === t("general.other_vendors")) {
        !vendorEmail || !emailPattern.test(vendorEmail)
          ? setDisableBtn(true)
          : setDisableBtn(false);
      }
    } else {
      setDisableBtn(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    fileLoading,
    dataReady,
    inHouse,
    approvedVendor,
    multiSelectedVendor,
    vendorEmail,
    description,
    pickupDate,
    requestedDeliveryDate,
    quoteDeadline,
    urgent,
    mileage,
    hours,
    vendorTransportToVendor,
    vendorTransportToClient,
    estimatedCost,
  ]);

  const sendRepairRequest = (repairRequest) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Add`, repairRequest, getAuthHeader())
      .then((response) => {
        successAlert();
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
      })
      .catch((error) => {
        errorAlert(error.customErrorMsg, repairRequest);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  const successAlert = () => {
    return swal({
      title: t("general.success"),
      text: t("repairRequestPanel.success_alert_text"),
      icon: "success",
      buttons: {
        return: t("general.return"),
        new: t("general.new_request"),
      },
    }).then((value) => {
      switch (value) {
        case "return":
          history.push("/repairs");
          break;
        default:
          resetForm();
          setSubmitSuccessForceUpdate(Date.now);
      }
    });
  };

  const errorAlert = (errorMsg, repairRequest) => {
    return swal({
      title: `${t("swal.error")}`,
      text: errorMsg,
      icon: "error",
      buttons: { resend: "Try Again", cancel: "Cancel" },
    }).then((value) => {
      switch (value) {
        case "resend":
          sendRepairRequest(repairRequest);
          break;
        case "cancel":
          resetForm();
          break;
        default:
          resetForm();
      }
    });
  };

  /* 
      If user still clicks urgent repair box show a swal warning message that 
      it is not required but let them proceed with it if they want to.
    */
  const urgentNotRequiredAlert = () => {
    return swal({
      title: t("repairRequestPanel.urgent_not_required_alert_title"),
      text: t("repairRequestPanel.urgent_not_required_alert_text"),
      icon: "warning",
      buttons: {
        cancel: t("swal.cancel_button"),
        urgent: t("repairRequestPanel.urgent_repair_button"),
      },
    }).then((value) => {
      switch (value) {
        case "urgent":
          setUrgent(true);
          break;
        default:
          return;
      }
    });
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let repairReport = new FormData();

    repairReport.append(
      "data",
      JSON.stringify({
        repair_data: {
          VIN: vehicle.VIN,
          description: description,
          is_complete: false,
          quote_deadline: quoteDeadline.toISOString(),
          is_urgent: urgent,
          ...(inHouse === t("general.yes")
            ? { in_house: true, estimated_cost: estimatedCost }
            : { in_house: false }),
          ...(inHouse === t("general.no")
            ? {
                vendor_transport_to_vendor: vendorTransportToVendor,
                available_pickup_date: pickupDate.toISOString(),
                vendor_transport_to_client: vendorTransportToClient,
                requested_delivery_date: requestedDeliveryDate.toISOString(),
              }
            : { available_pickup_date: new Date().toISOString() }), // todo remove hard-coding once backend is ready
          ...(inHouse === t("general.no") && approvedVendor === t("general.approved_vendors")
            ? {
                vendor: null, //TODO need to auto setup this in the future
                potential_vendor_ids: `-${multiSelectedVendor.map((el) => el.code).join("-")}-`,
              }
            : null),
          ...(inHouse === t("general.no") && approvedVendor === t("general.other_vendors")
            ? { vendor_email: vendorEmail }
            : null),
          ...(vehicle.hours_or_mileage.toLowerCase() === "both" && {
            mileage: parseFloat(mileage),
            hours: parseFloat(hours),
          }),
          ...(vehicle.hours_or_mileage.toLowerCase() === "mileage" && {
            mileage: parseFloat(mileage),
          }),
          ...(vehicle.hours_or_mileage.toLowerCase() === "hours" && { hours: parseFloat(hours) }),
        },
        assetissuemodel_set: {
          issue_set: issues.map((issue) => {
            return issue.issue_id;
          }),
        },
        // TODO: Replace the placeholder info for approval_data
        approval_data: {
          title: "Repair Approval",
          description: "This is an approval made for testing purposes.",
        },
      })
    );

    let required_file_specs = {
      file_info: [],
    };
    if (files.length > 0) {
      for (let i = 0; i < files.length; i++) {
        required_file_specs.file_info.push({ file_name: files[i].name, purpose: "other" });
        repairReport.append("files", files[i]);
      }
    }
    repairReport.append("file_specs", JSON.stringify(required_file_specs));

    sendRepairRequest(repairReport);
  };

  const ReplacementAssetTable = ({ replacementAssets }) => {
    let tableHeaders = [
      { header: t("general.vin"), colFilter: { field: "VIN" } },
      {
        header: t("repairRequestPanel.asset_type_label"),
        colFilter: { field: "asset_type", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("general.location"),
        colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("repairRequestPanel.asset_utilization_label"),
        colFilter: { field: "daily_average_mileage" },
      },
    ];

    let tableData = replacementAssets.map((item) => {
      return {
        id: item.VIN,
        dataPoint: item,
        cells: [
          <VINLink vin={item.VIN} />,
          item.asset_type,
          item.current_location,
          item.daily_average_mileage.toFixed(2),
        ],
      };
    });

    return (
      <Table tableHeaders={tableHeaders} tableData={tableData} globalSearch={false} rows={5} />
    );
  };

  const UrgentRepairRecommend = () => {
    let showAssetsButton = (
      <div className="btn-2">
        <Button
          label={t("repairRequestPanel.show_under_utilized_assets_button")}
          className="p-button-lg p-button-primary p-ml-3"
          disabled={!dataReady}
          onClick={() => setShowRecommends(true)}
        />
      </div>
    );
    return isUrgentRepairRequire ? (
      <h5 className="text-center repair-form-urgent-msg">
        <FaExclamationTriangle color={colorVars.orange} className="p-mr-2 h1" />{" "}
        {t("repairRequestPanel.urgent_repair_required_text")}
      </h5>
    ) : (
      <div>
        <Dialog
          header={t("repairRequestPanel.under_utilized_table_dialog_title")}
          className="custom-main-dialog"
          visible={showRecommends}
          onHide={() => setShowRecommends(false)}
          style={{ width: "50vw" }}
          breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "95vw" }}
          footer={<></>}
        >
          <div className="under-util-container">
            {replaceAssets.replacements_ordered_by_mileage.length !== 0 &&
            replaceAssets.replacements_ordered_by_hours.length !== 0 ? (
              <TabView className="darkSubTab darkTable">
                <TabPanel header={t("repairRequestPanel.order_by_mileage")}>
                  <ReplacementAssetTable
                    replacementAssets={replaceAssets.replacements_ordered_by_mileage}
                  />
                </TabPanel>
                <TabPanel header={t("repairRequestPanel.order_by_hours")}>
                  <ReplacementAssetTable
                    replacementAssets={replaceAssets.replacements_ordered_by_hours}
                  />
                </TabPanel>
              </TabView>
            ) : replaceAssets.replacements_ordered_by_mileage.length === 0 &&
              replaceAssets.replacements_ordered_by_hours.length !== 0 ? (
              <TabView className="darkSubTab darkTable">
                <TabPanel header={t("repairRequestPanel.order_by_hours")}>
                  <ReplacementAssetTable
                    replacementAssets={replaceAssets.replacements_ordered_by_hours}
                  />
                </TabPanel>
              </TabView>
            ) : replaceAssets.replacements_ordered_by_mileage.length !== 0 &&
              replaceAssets.replacements_ordered_by_hours.length === 0 ? (
              <TabView className="darkSubTab darkTable">
                <TabPanel header={t("repairRequestPanel.order_by_mileage")}>
                  <ReplacementAssetTable
                    replacementAssets={replaceAssets.replacements_ordered_by_mileage}
                  />
                </TabPanel>
              </TabView>
            ) : null}
          </div>
        </Dialog>
        <h5 className="repair-form-urgent-msg p-d-flex p-jc-center p-ai-center p-flex-wrap">
          <FaCheckCircle color={colorVars.green} className="p-mr-2 h1" />
          {t("repairRequestPanel.urgent_repair_not_required_text")}
          {showAssetsButton}
        </h5>
      </div>
    );
  };

  let tooltip = {
    label: "urgent-repair-tooltip",
    description: t("repairRequestPanel.urgent_repair_tooltip"),
  };

  const selectInHouse = (e) => {
    setInHouse(e.value);
    setApprovedVendor(null);
    setVendorTransportToVendor(null);
    setPickupDate(null);
    setVendorTransportToClient(null);
    setRequestedDeliveryDate(null);
    setEstimatedCost(null);
  };

  const itemTemplate = (option) => {
    const rating = option.rating?.toFixed(1);
    return (
      <div>
        <span>
          <i>{option.name}</i>
          {option.is_vendor_green && (
            <FontAwesomeIcon
              icon={faLeaf}
              color={"#54d67b"}
              style={{ margin: "0 3px", verticalAlign: "middle" }}
            />
          )}
        </span>{" "}
        {option.code !== 9999 && (
          <>
            (<span> {rating} </span>
            <StarRating
              unit="float"
              initialRating={rating}
              activeColor={"#2196F3"}
              isReadOnly
              style={{ display: "inline-block" }}
              size={20}
            />{" "}
            )
          </>
        )}
      </div>
    );
  };

  if (issues)
    return (
      <form onSubmit={handleSubmit}>
        <CardWidget
          status={
            (inHouse === t("general.yes") && estimatedCost !== null && description) ||
            (inHouse === t("general.no") && approvedVendor && description)
              ? (approvedVendor === t("general.other_vendors") &&
                  (!vendorEmail || !emailPattern.test(vendorEmail))) ||
                (approvedVendor === t("general.approved_vendors") && !multiSelectedVendor.length)
                ? false
                : true
              : false
          }
        >
          <label htmlFor="vendor" className="h5">
            {t("repairRequestPanel.in_house_question")}
          </label>
          <div className="p-d-flex darkRadio">
            <div className="p-field-radiobutton p-mr-3 p-mb-0">
              <RadioButton
                inputId="inHouseTrue"
                name="house"
                value={t("general.yes")}
                onChange={selectInHouse}
                checked={inHouse === t("general.yes")}
              />
              <label className="p-m-0 p-m-2" htmlFor="inHouseTrue">
                {t("general.yes")}
              </label>
            </div>
            <div className="p-field-radiobutton p-mb-0">
              <RadioButton
                inputId="inHouseFalse"
                name="house"
                value={t("general.no")}
                onChange={selectInHouse}
                checked={inHouse === t("general.no")}
              />
              <label className="p-m-0 p-m-2" htmlFor="inHouseFalse">
                {t("general.no")}
              </label>
            </div>
          </div>
          {inHouse === t("general.yes") ? (
            <React.Fragment>
              <label className="h5 p-mt-3">{t("repairRequestPanel.estimated_cost_label")}</label>
              <CustomInputNumber
                value={estimatedCost}
                onChange={setEstimatedCost}
                className="w-100"
                mode="decimal"
                min={0}
                minFractionDigits={2}
                maxFractionDigits={2}
                max={2147483646}
              />
            </React.Fragment>
          ) : null}
          {inHouse === t("general.no") ? (
            <React.Fragment>
              <label htmlFor="vendor" className="h5 p-mt-3">
                {t("general.vendor_question", { request_type: "repair" })}
              </label>
              <div className="p-d-flex darkRadio">
                <div className="p-field-radiobutton p-mr-3 p-mb-0">
                  <RadioButton
                    inputId="approvedVendorTrue"
                    name="vendor"
                    value={t("general.approved_vendors")}
                    onChange={(e) => {
                      setApprovedVendor(e.value);
                      setVendorEmail("");
                    }}
                    checked={approvedVendor === t("general.approved_vendors")}
                  />
                  <label className="p-m-0 p-m-2" htmlFor="approvedVendorTrue">
                    {t("general.approved_vendors")}
                  </label>
                </div>
                <div className="p-field-radiobutton p-mb-0">
                  <RadioButton
                    inputId="approvedVendorFalse"
                    name="vendor"
                    value={t("general.other_vendors")}
                    onChange={(e) => {
                      setApprovedVendor(e.value);
                      setMultiSelectedVendor([]);
                    }}
                    checked={approvedVendor === t("general.other_vendors")}
                  />
                  <label className="p-m-0 p-m-2" htmlFor="approvedVendorFalse">
                    {t("general.other_vendors")}
                  </label>
                </div>
              </div>
            </React.Fragment>
          ) : null}
          {approvedVendor === t("general.approved_vendors") && (
            <React.Fragment>
              <label className="h5 p-mt-3">{t("general.approved_vendor")}</label>
              <MultiSelectDropdown
                value={multiSelectedVendor}
                options={
                  approvedVendors
                    ? approvedVendors.map((vendor) => ({
                        name: `${vendor.vendor_name}${
                          vendor.primary_email ? " - " + vendor.primary_email : ""
                        }`,
                        is_vendor_green: vendor.is_vendor_green,
                        rating: vendor.rating,
                        code: vendor.vendor_id,
                      }))
                    : []
                }
                disabled={!dataReady}
                itemTemplate={itemTemplate}
                onChange={(e) => setMultiSelectedVendor(e.value)}
                maxSelectedLabels={3}
                selectedItemsLabel={"{0} vendors selected"}
                placeholder={t("general.approved_vendors_placeholder")}
              />
            </React.Fragment>
          )}
          {approvedVendor === t("general.other_vendors") && (
            <React.Fragment>
              <label className="h5 p-mt-3">{t("repairRequestPanel.vendor_email_label")}</label>
              <CustomInputText
                type="email"
                placeholder={t("repairRequestPanel.vendor_email_placeholder")}
                value={vendorEmail}
                onChange={setVendorEmail}
                required
              />
            </React.Fragment>
          )}
          <label className="h5 p-mt-3">{t("repairRequestPanel.repair_description_label")}</label>
          <CustomTextArea
            rows={3}
            value={description}
            placeholder={t("repairRequestPanel.repair_description_placeholder")}
            onChange={setDescription}
            required
            autoResize
          />
        </CardWidget>

        {vehicle.hours_or_mileage.toLowerCase() === "mileage" ||
        vehicle.hours_or_mileage.toLowerCase() === "both" ? (
          <CardWidget status={mileage ? true : false}>
            <label className="h5">{t("general.mileage")}</label>
            <span className="p-input-icon-right w-100">
              {validationSearch ? <i className="pi pi-spin pi-spinner" /> : null}
              <CustomInputText
                className="w-100"
                placeholder={t("general.enter_mileage")}
                onChange={setMileage}
                keyfilter={/^\d*\.?\d*$/}
                disabled={validationSearch}
              />
            </span>
          </CardWidget>
        ) : null}
        {vehicle.hours_or_mileage.toLowerCase() === "hours" ||
        vehicle.hours_or_mileage.toLowerCase() === "both" ? (
          <CardWidget status={hours ? true : false}>
            <label className="h5">{t("general.hours")}</label>
            <span className="p-input-icon-right w-100">
              {validationSearch ? <i className="pi pi-spin pi-spinner" /> : null}
              <CustomInputText
                className="w-100"
                placeholder={t("general.enter_hours")}
                onChange={setHours}
                keyfilter={/^\d*\.?\d*$/}
                disabled={validationSearch}
              />
            </span>
          </CardWidget>
        ) : null}

        {validationWarningMsg && (
          <div className="p-mt-3">
            <WarningMsg message={validationWarningMsg} sm />
          </div>
        )}

        <CardWidget status={files.length > 0}>
          <label className="h5 form-tooltip">{t("general.supporting_file")}</label>
          <div className="custom-file input-files-container">
            <FileUploadInput
              images={files}
              setImages={setFiles}
              imageNames={fileNames}
              setImageNames={setFileNames}
              fileLoading={fileLoading}
              setFileLoading={setFileLoading}
              fileTypes=".pdf,.doc,.docx,image/*,.heic"
              maxNumberOfFiles={20}
            />
          </div>
        </CardWidget>

        {inHouse === t("general.no") && (
          <>
            <CardWidget status={vendorTransportToVendor !== null && pickupDate ? true : false}>
              <React.Fragment>
                <label htmlFor="tansportToVendor" className="h5 p-mt-3">
                  {t("general.transport_to_vendor_question", { request_type: "repair" })}
                </label>
                <div className="p-d-flex darkRadio">
                  <div className="p-field-radiobutton p-mr-3 p-mb-0">
                    <RadioButton
                      inputId="tansportToVendorTrue"
                      name="tansportToVendor"
                      value={vendorTransportToVendor}
                      onChange={(e) => {
                        setVendorTransportToVendor(true);
                        setPickupDate(null);
                      }}
                      checked={vendorTransportToVendor === true}
                    />
                    <label className="p-m-0 p-m-2" htmlFor="tansportToVendorTrue">
                      {t("general.transport_vendor_pickup")}
                    </label>
                  </div>
                  <div className="p-field-radiobutton p-mb-0">
                    <RadioButton
                      inputId="tansportToVendorFalse"
                      name="tansportToVendor"
                      value={vendorTransportToVendor}
                      onChange={(e) => {
                        setVendorTransportToVendor(false);
                        setPickupDate(null);
                      }}
                      checked={vendorTransportToVendor === false}
                    />
                    <label className="p-m-0 p-m-2" htmlFor="tansportToVendorFalse">
                      {t("general.transport_client_dropoff")}
                    </label>
                  </div>
                </div>
              </React.Fragment>
              {vendorTransportToVendor !== null && (
                <React.Fragment>
                  <label className="h5 p-mt-3">
                    {vendorTransportToVendor
                      ? t("general.available_pickup_date")
                      : t("general.client_dropoff_date")}
                  </label>
                  <DatePicker
                    onChange={(e) => {
                      setPickupDate(e);
                      if (
                        requestedDeliveryDate &&
                        Date.parse(e) > Date.parse(requestedDeliveryDate)
                      ) {
                        setRequestedDeliveryDate(null);
                      }
                    }}
                    initialDate={pickupDate}
                    minDate={new Date()}
                  />
                </React.Fragment>
              )}
            </CardWidget>

            <CardWidget status={vendorTransportToClient !== null && requestedDeliveryDate}>
              <React.Fragment>
                <label htmlFor="tansportToClient" className="h5 p-mt-3">
                  {t("general.transport_to_client_question", { request_type: "repair" })}
                </label>
                <div className="p-d-flex darkRadio">
                  <div className="p-field-radiobutton p-mr-3 p-mb-0">
                    <RadioButton
                      inputId="tansportToClientTrue"
                      name="tansportToClient"
                      value={vendorTransportToClient}
                      onChange={(e) => {
                        setVendorTransportToClient(true);
                      }}
                      checked={vendorTransportToClient === true}
                    />
                    <label className="p-m-0 p-m-2" htmlFor="tansportToClientTrue">
                      {t("general.transport_vendor_delivery")}
                    </label>
                  </div>
                  <div className="p-field-radiobutton p-mb-0">
                    <RadioButton
                      inputId="tansportToClientFalse"
                      name="tansportToClient"
                      value={vendorTransportToClient}
                      onChange={(e) => {
                        setVendorTransportToClient(false);
                        setRequestedDeliveryDate(null);
                      }}
                      checked={vendorTransportToClient === false}
                    />
                    <label className="p-m-0 p-m-2" htmlFor="tansportToClientFalse">
                      {t("general.transport_client_pickup")}
                    </label>
                  </div>
                </div>
              </React.Fragment>
              {vendorTransportToClient !== null && (
                <React.Fragment>
                  <label className="h5 mt-3">
                    {vendorTransportToClient
                      ? t("repairRequestPanel.requested_delivery_date_label")
                      : t("repairRequestPanel.requested_pickup_date_label")}
                  </label>
                  <DatePicker
                    onChange={setRequestedDeliveryDate}
                    initialDate={requestedDeliveryDate}
                    minDate={pickupDate || new Date()}
                    required
                  />
                </React.Fragment>
              )}
            </CardWidget>
          </>
        )}

        <CardWidget status={quoteDeadline}>
          <label className="h5">
            {t("general.quote_deadline_label")}
            <Tooltip
              label="repair_quote_deadline"
              description={t("general.quote_deadline_explanation")}
            />
          </label>
          <DatePicker
            onChange={setQuoteDeadline}
            initialDate={quoteDeadline}
            minDate={new Date()}
            required
          />
        </CardWidget>

        {dataReady ? (
          <div className="p-mt-5">
            {dataLoadingError ? null : <UrgentRepairRecommend />}
            <ChecklistItem
              value={urgent}
              onChange={(isUrgent) => {
                if (!isUrgentRepairRequire && isUrgent) urgentNotRequiredAlert();
                else setUrgent(isUrgent);
              }}
              name={"urgentRadio"}
              labels={[t("repairRequestPanel.urgent_radio_btn_label")]}
              required
              status={urgent !== "" ? true : false}
              tooltip={tooltip}
            />
          </div>
        ) : (
          <Spinner>
            <h4 className="repair-form-urgent-msg">
              {t("repairRequestPanel.check_replacement_loading_text")}
            </h4>
          </Spinner>
        )}
        <div className="d-flex justify-content-center p-mt-5 p-mb-5">
          <div className="p-d-flex p-jc-center btn-1">
            <Button
              type="submit"
              label={t("repairRequestPanel.btn_submit_request")}
              disabled={disableBtn}
            />
          </div>
        </div>
      </form>
    );
};

export default RepairRequestForm;
