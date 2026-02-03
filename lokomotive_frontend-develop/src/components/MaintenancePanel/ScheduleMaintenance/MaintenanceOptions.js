import React, { useState, useEffect } from "react";
import axios from "axios";
import swal from "sweetalert";
import { useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import StarRating from "react-svg-star-rating";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faLeaf } from "@fortawesome/free-solid-svg-icons";
import { InputText } from "primereact/inputtext";
import { RadioButton } from "primereact/radiobutton";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import DatePicker from "../../ShareComponents/DatePicker";
import CardWidget from "../../ShareComponents/CardWidget";
import ChecklistItem from "../../ShareComponents/ChecklistItem";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import MultiSelectDropdown from "../../ShareComponents/Forms/MultiSelectDropdown";
import WarningMsg from "../../ShareComponents/WarningMsg";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import CustomInputText from "../../ShareComponents/CustomInputText";
import CustomInputNumber from "../../ShareComponents/CustomInputNumber";
import robot from "../../../images/robots/robot-hi.png";
import "../../../styles/helpers/button1.scss";
import "../../../styles/helpers/fileInput.scss";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/MaintenancePanel/scheduleMaintenance.scss";

// Rendering maintenance schedule options
const MaintenanceOptions = ({
  selectedVehicles,
  maintenanceTypes,
  maintenanceType,
  setMaintenanceType,
  mileageNhours,
  setMileageNhours,
  setUsageWarningMsg,
  usageWarningMsg,
  files,
  setFiles,
  pickupDate,
  setPickupDate,
  requestedDeliveryDate,
  setRequestedDeliveryDate,
  inHouse,
  setInHouse,
  approvedVendors,
  approvedVendor,
  setApprovedVendor,
  multiSelectedVendor,
  setMultiSelectedVendor,
  vendorEmail,
  setVendorEmail,
  dataReady,
  handleSubmit,
  quoteDeadline,
  setQuoteDeadline,
  vendorTransportToVendor,
  setVendorTransportToVendor,
  vendorTransportToClient,
  setVendorTransportToClient,
  estimatedCost,
  setEstimatedCost,
}) => {
  const { t } = useTranslation();
  const history = useHistory();
  const [forceUpdateField, setForceUpdateField] = useState(Date.now);
  const [mileageHourStatus, setMileageHourStatus] = useState([]);
  const [usageValidateSearch, setUsageValidateSearch] = useState(false);
  const [warningDataReady, setWarningDataReady] = useState(false);
  const [disableBtn, setDisableBtn] = useState(true);
  const [isFromAccident, setIsFromAccident] = useState("");
  const [fileStatus, setFileStatus] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const emailPattern = new RegExp("[a-z0-9._%+-]+@[a-z0-9.-]+.[a-z]{2,4}$");

  useEffect(() => {
    setIsFromAccident("");
    setFileStatus(false);
    setMileageNhours([]);
    setMileageHourStatus([]);
    setFiles({});
    setUsageWarningMsg([]);
    setWarningDataReady(false);
    setForceUpdateField(Date.now);
    selectedVehicles.forEach((vehicle, i) => {
      let mileage_hours = {};
      mileage_hours.VIN = vehicle.VIN;
      vehicle.hours_or_mileage.toLowerCase() === "mileage" ||
      vehicle.hours_or_mileage.toLowerCase() === "both"
        ? (mileage_hours.Mileage = "")
        : (mileage_hours.Mileage = "na");
      vehicle.hours_or_mileage.toLowerCase() === "hours" ||
      vehicle.hours_or_mileage.toLowerCase() === "both"
        ? (mileage_hours.Hours = "")
        : (mileage_hours.Hours = "na");

      setFiles((prevState) => ({ ...prevState, [vehicle.VIN]: [] }));
      setMileageNhours((prevArray) => [...prevArray, mileage_hours]);
      if (vehicle.hours_or_mileage.toLowerCase() === "neither") {
        setMileageHourStatus((prevStatus) => [...prevStatus, true]);
      } else {
        setMileageHourStatus((prevStatus) => [...prevStatus, false]);
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedVehicles]);

  useEffect(() => {
    if (mileageHourStatus.length > 0 && mileageHourStatus.every(Boolean)) {
      const delayDebounceFn = setTimeout(() => {
        setUsageWarningMsg([]);
        setWarningDataReady(false);
        setUsageValidateSearch(true);

        let promises = [];
        for (let i = 0; i < mileageNhours.length; i++) {
          let data = { VIN: mileageNhours[i].VIN };
          if (mileageNhours[i].Mileage !== "na") {
            data = { ...data, mileage: parseFloat(mileageNhours[i].Mileage) };
          }
          if (mileageNhours[i].Hours !== "na") {
            data = { ...data, hours: parseFloat(mileageNhours[i].Hours) };
          }
          promises.push(
            axios
              .post(
                `${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Validate/Usage`,
                data,
                getAuthHeader()
              )
              .catch((error) => {
                setUsageWarningMsg((prevArray) => [
                  ...prevArray,
                  data.VIN + ":",
                  error.customErrorMsg,
                ]);
              })
          );
        }
        Promise.all(promises).then(() => {
          setUsageValidateSearch(false);
          setWarningDataReady(true);
        });
      }, 1000);
      return () => clearTimeout(delayDebounceFn);
    }
  }, [mileageHourStatus]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (
      !maintenanceType ||
      !quoteDeadline ||
      !inHouse ||
      mileageHourStatus.length === 0 ||
      !mileageHourStatus.every(Boolean) ||
      (inHouse === t("general.yes") && estimatedCost === null) ||
      (inHouse === t("general.no") &&
        (!approvedVendor ||
          vendorTransportToVendor === null ||
          (vendorTransportToVendor !== null && !pickupDate) ||
          vendorTransportToClient === null ||
          (vendorTransportToClient !== null && !requestedDeliveryDate)))
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
    maintenanceType,
    pickupDate,
    requestedDeliveryDate,
    quoteDeadline,
    inHouse,
    mileageHourStatus,
    approvedVendor,
    multiSelectedVendor,
    vendorEmail,
    vendorTransportToVendor,
    vendorTransportToClient,
    estimatedCost,
  ]);

  useEffect(() => {
    if (isFromAccident) {
      return swal({
        title: t("general.warning"),
        text: t("maintenanceSchedulePanel.alert_accident"),
        icon: "warning",
        buttons: {
          cancel: t("general.cancel"),
          ok: t("navigationItems.repair_request"),
        },
      }).then((value) => {
        switch (value) {
          case "cancel":
            setIsFromAccident("");
            break;
          case "ok":
            history.push("/repairs/request");
            break;
          default:
            setIsFromAccident("");
        }
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isFromAccident]);

  useEffect(() => {
    !Object.values(files).every((file) => file.length && file[0]) && setFileStatus(false);
    Object.entries(files).forEach(([key, file]) => {
      (file.length && !file[0]) && setFiles((pre) => ({ ...pre, [key]: [] }));
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [files]);

  const onEditorValueChange = (rowData, value, field) => {
    let updatedValues = mileageNhours;
    var findIndex = updatedValues.findIndex((values) => values.VIN === rowData.VIN);
    updatedValues[findIndex][field] = value;
    setMileageNhours(updatedValues);

    let status = mileageNhours.map(function (obj) {
      return !Object.values(obj).some((value) => !value);
    });
    setMileageHourStatus(status);
  };

  const mileageEditorTemplate = (rowData) => {
    return (
      <span className="p-input-icon-right w-100">
        {usageValidateSearch && rowData.Mileage !== "na" ? (
          <i className="pi pi-spin pi-spinner" />
        ) : null}
        <InputText
          className="w-100"
          keyfilter={/^\d*\.?\d*$/}
          value={
            rowData.Mileage === "na"
              ? t("maintenanceSchedulePanel.no_info_needed")
              : rowData.Mileage
          }
          onChange={(e) => onEditorValueChange(rowData, e.target.value, "Mileage")}
          disabled={rowData.Mileage === "na" || usageValidateSearch}
          placeholder={isMobile ? "Enter Mileage" : ""}
        />
      </span>
    );
  };

  const hoursEditorTemplate = (rowData) => {
    return (
      <span className="p-input-icon-right w-100">
        {usageValidateSearch && rowData.Hours !== "na" ? (
          <i className="pi pi-spin pi-spinner" />
        ) : null}
        <InputText
          keyfilter={/^\d*\.?\d*$/}
          value={
            rowData.Hours === "na" ? t("maintenanceSchedulePanel.no_info_needed") : rowData.Hours
          }
          onChange={(e) => onEditorValueChange(rowData, e.target.value, "Hours")}
          disabled={rowData.Hours === "na" || usageValidateSearch}
          placeholder={isMobile ? "Enter Hours" : ""}
        />
      </span>
    );
  };

  const selectInHouse = (e) => {
    setInHouse(e.value);
    setApprovedVendor(null);
    setVendorTransportToVendor(null);
    setVendorTransportToClient(null);
    setPickupDate(null);
    setRequestedDeliveryDate(null);
    setApprovedVendor(null);
    setVendorEmail(null);
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
            />
            )
          </>
        )}
      </div>
    );
  };

  return (
    <div className={`p-mx-3 ${!isMobile ? "p-mt-5" : ""}`}>
      <div className="report-form-container">
        <div className="schedule-maintenance-form-container">
          {(isFromAccident === "" || isFromAccident === true) && (
            <div className="fleet-guru p-d-flex p-ai-center p-mb-5">
              <div className="topbar-son">
                <img src={robot} alt="" />
              </div>
              <ChecklistItem
                value={isFromAccident}
                onChange={setIsFromAccident}
                name={"accidentRadio"}
                labels={[t("reportIncidentPanel.is_accident")]}
                status={isFromAccident !== "" ? true : false}
              />
            </div>
          )}
          {isFromAccident === false && (
            <React.Fragment>
              <h4 className="p-mb-3 schedule-maintenance-form-container-title">
                {t("maintenanceSchedulePanel.selected_assets_label")}
                {": "}
                {selectedVehicles.map((vehicle, index) => {
                  if (selectedVehicles.length - 1 === index) {
                    return `${vehicle.VIN}`;
                  }
                  return `${vehicle.VIN} / `;
                })}
              </h4>

              <CardWidget status={maintenanceType ? true : false}>
                <label className="h5 p-mb-2">
                  {t("maintenanceSchedulePanel.maintenance_type_label")}
                </label>
                <FormDropdown
                  dataReady
                  reset="disabled"
                  defaultValue={
                    maintenanceType && {
                      code: maintenanceType,
                      name: maintenanceTypes.find((type) => type.id === maintenanceType)
                        .inspection_name,
                    }
                  }
                  onChange={(e) => {
                    setMaintenanceType(e);
                  }}
                  options={
                    maintenanceTypes &&
                    maintenanceTypes.map((maintenanceTypeItem) => ({
                      name: maintenanceTypeItem.inspection_name,
                      code: maintenanceTypeItem.id,
                    }))
                  }
                  loading={!dataReady}
                  disabled={!dataReady}
                  plain_dropdown
                />
              </CardWidget>

              <div
                className="schedule-maintenance-hours-mileage darkTable"
                style={{ padding: "0" }}
              >
                <CardWidget
                  status={
                    mileageHourStatus.length > 0 && mileageHourStatus.every(Boolean) ? true : false
                  }
                >
                  <DataTable key={forceUpdateField} value={mileageNhours}>
                    <Column field="VIN" header="VIN" />
                    <Column body={mileageEditorTemplate} header="Mileage" />
                    <Column body={hoursEditorTemplate} header="Hours" />
                  </DataTable>
                  {warningDataReady && usageWarningMsg.length > 0 && (
                    <div className="p-mt-3">
                      <WarningMsg message={usageWarningMsg} sm />
                    </div>
                  )}
                </CardWidget>
              </div>

              {/* Input files */}
              <CardWidget status={fileStatus}>
                {selectedVehicles.map((vehicle, index) => {
                  return (
                    <div key={index}>
                      {files[vehicle.VIN] ? (
                        <div className={`${index !== 0 && "p-mt-3"}`}>
                          <label className="h5 form-tooltip">
                            {t("maintenanceSchedulePanel.supporting_file", { vin: vehicle.VIN })}
                            <Tooltip
                              label={"upload-tooltip"}
                              description={t("maintenanceSchedulePanel.supporting_file_tooltip", {
                                vin: vehicle.VIN,
                              })}
                            />
                          </label>
                          <div className="custom-file input-files-container">
                            <input
                              name="file"
                              type="file"
                              className="custom-file-input"
                              accept=".pdf,.doc,.docx"
                              onChange={(e) => {
                                setFiles((pre) => ({
                                  ...pre,
                                  [vehicle.VIN]: [e.target.files[0]],
                                }));
                                setFileStatus(true);
                              }}
                              multiple={1}
                            />
                            <label className="custom-file-label" htmlFor="customFile">
                              {files[vehicle.VIN].length && files[vehicle.VIN][0]
                                ? files[vehicle.VIN][0]["name"]
                                : t("fileUploadInput.file_choose")}
                            </label>
                          </div>
                        </div>
                      ) : null}
                    </div>
                  );
                })}
              </CardWidget>

              {/* inHouse question */}
              <CardWidget
                status={
                  (inHouse === t("general.yes") && estimatedCost !== null) ||
                  (inHouse === t("general.no") && approvedVendor)
                    ? (approvedVendor === t("general.other_vendors") &&
                        (!vendorEmail || !emailPattern.test(vendorEmail))) ||
                      (approvedVendor === t("general.approved_vendors") &&
                        !multiSelectedVendor.length)
                      ? false
                      : true
                    : false
                }
              >
                <label htmlFor="vendor" className="h5">
                  {t("maintenanceSchedulePanel.in_house_question")}
                </label>
                <div className="p-d-flex">
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
                    <label className="h5 p-mt-3">
                      {t("maintenanceSchedulePanel.estimated_cost_label")}
                    </label>
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
                      {t("general.vendor_question", { request_type: "maintenance" })}
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
                    <label htmlFor="vendor" className="h5 p-mt-3">
                      {t("maintenanceSchedulePanel.vendor_email_label")}
                    </label>
                    <CustomInputText
                      type="email"
                      className="form-control"
                      id="vendor"
                      placeholder={t("maintenanceSchedulePanel.vendor_email_placeholder")}
                      value={vendorEmail}
                      onChange={setVendorEmail}
                      pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$"
                    />
                  </React.Fragment>
                )}
              </CardWidget>

              {inHouse === t("general.no") && (
                <>
                  <CardWidget
                    status={vendorTransportToVendor !== null && pickupDate ? true : false}
                  >
                    <React.Fragment>
                      <label htmlFor="tansportToVendor" className="h5 p-mt-3">
                        {t("general.transport_to_vendor_question", { request_type: "maintenance" })}
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
                        {t("general.transport_to_client_question", { request_type: "maintenance" })}
                      </label>
                      <div className="p-d-flex darkRadio">
                        <div className="p-field-radiobutton p-mr-3 p-mb-0">
                          <RadioButton
                            inputId="tansportToClientTrue"
                            name="tansportToClient"
                            value={vendorTransportToClient}
                            onChange={(e) => {
                              setVendorTransportToClient(true);
                              setRequestedDeliveryDate(null);
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
                            ? t("maintenanceSchedulePanel.requested_date_label")
                            : t("maintenanceSchedulePanel.pickup_date_label")}
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
                    label="maintenance_quote_deadline"
                    description={t("general.quote_deadline_explanation")}
                  />
                </label>
                <DatePicker
                  onChange={setQuoteDeadline}
                  initialDate={quoteDeadline}
                  minDate={new Date()}
                />
              </CardWidget>

              <div className="d-flex justify-content-center p-my-5 p-pb-5">
                <div className="p-d-flex p-jc-center btn-1">
                  <Button
                    className="text-uppercase"
                    type="submit"
                    label={t("maintenanceSchedulePanel.button_submit")}
                    onClick={handleSubmit}
                    disabled={disableBtn}
                  />
                </div>
              </div>
            </React.Fragment>
          )}
        </div>
      </div>
    </div>
  );
};

export default MaintenanceOptions;
