import React, { useRef, useEffect, useState } from "react";
import axios from "axios";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Toast } from 'primereact/toast';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCartPlus } from "@fortawesome/free-solid-svg-icons";
import { getAuthHeader } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import VINLink from "../../ShareComponents/helpers/VINLink";
import { Table } from "../../ShareComponents/Table";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import DatePicker from "../../ShareComponents/DatePicker";
import VendorOption from "./VendorOption";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import AddNewEquipType from "./AddNewEquipType";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/helpers/button1.scss";
import CustomInputNumber from "../../ShareComponents/CustomInputNumber";

const AssetOrderForm = (props) => {
  const dispatch = useDispatch();
  const { t } = useTranslation();
  const location = useLocation();
  const history = useHistory();
  const toastRef = useRef(null);
  const { listBusinessUnits, listAssetRequestJust } = useSelector((state) => state.apiCallData);
  const [dataReady, setDataReady] = useState(false);
  const [manufDataReady, setManufDataReady] = useState(false);
  const [equipDataReady, setEquipDataReady] = useState(false);
  const [defaultBusinessUnit, setDefaultBusinessUnit] = useState(null);
  const [selectedBusinessUnit, setSelectedBusinessUnit] = useState(null);
  const [assetTypes, setAssetTypes] = useState(null);
  const [defaultAssetType, setDefaultAssetType] = useState(null);
  const [selectedAssetType, setSelectedAssetType] = useState(null);
  const [selectedJustification, setSelectedJustification] = useState(null);
  const [assetManufacturers, setAssetManufacturers] = useState(null);
  const [defaultAssetManufacturer, setDefaultAssetManufacturer] = useState(null);
  const [selectedAssetManufacturer, setSelectedAssetManufacturer] = useState(null);
  const [equipmentTypes, setEquipmentTypes] = useState(null);
  const [defaultEquipmentType, setDefaultEquipmentType] = useState(null);
  const [selectedEquipmentType, setSelectedEquipmentType] = useState(null);
  const [accidentReported, setAccidentReported] = useState("");
  const [disposalReported, setDisposalReported] = useState("");
  const [isTradeIn, setIsTradeIn] = useState("");
  const [disposalReports, setDisposalReports] = useState([]);
  const [selectedDisposal, setSelectedDisposal] = useState(null);
  const [disposalDataReady, setDisposalDataReady] = useState(false);
  const [requestDate, setRequestDate] = useState(null);
  const [description, setDescription] = useState("");
  const [quantity, setQuantity] = useState(null);
  const [hideContent, setHideContent] = useState(false);
  const [dropdownReset, setDropdownReset] = useState(false);
  const [approvedVendors, setApprovedVendors] = useState(null);
  const [approvedVendor, setApprovedVendor] = useState(null);
  const [multiSelectedVendor, setMultiSelectedVendor] = useState([]);
  const [vendorEmail, setVendorEmail] = useState("");
  const [isVendorSelected, setIsVendorSelected] = useState(false);
  const [showInfoMsg, setShowInfoMsg] = useState(true);
  const [quoteDeadline, setQuoteDeadline] = useState(null);
  const [vendorTransportToClient, setVendorTransportToClient] = useState(null);
  const booleanOptions = [
    { name: "Yes", code: "Yes" },
    { name: "No", code: "No" },
  ];

  const inTransitToClientOption = [
    { name: t("general.transport_vendor_delivery"), code: true },
    { name: t("general.transport_client_pickup"), code: false },
  ];

  let hideValues = ["Life Cycle Replacement", "Equipment Failure", "Accident"];

  const showInfo = () => {
    toastRef.current.show({
      severity: "info",
      summary: t("assetRequestPanel.auto_populate_pending_header"),
      detail: t("assetRequestPanel.auto_populate_pending_text"),
      life: 7000,
    });
  };

  const showSuccess = () => {
    toastRef.current.show({
      severity: "success",
      summary: t("assetRequestPanel.auto_populate_success_header"),
      detail: t("assetRequestPanel.auto_populate_success_text"),
      life: 3000,
    });
  };

  const resetForm = () => {
    setSelectedBusinessUnit(null);
    setSelectedAssetManufacturer(null);
    setSelectedAssetType(null);
    setSelectedEquipmentType(null);
    setSelectedJustification(null);
    setIsTradeIn("");
    setSelectedDisposal(null);
    setApprovedVendor(null);
    setMultiSelectedVendor([]);
    setVendorEmail("");
    setIsVendorSelected(false);
    setDescription("");
    setQuantity(null);
    setDropdownReset(!dropdownReset);
    setRequestDate(null);
    setQuoteDeadline(null);
    setVendorTransportToClient(null);
  };

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    if (location.state && showInfoMsg) {
      showInfo();
      setShowInfoMsg(false);
    }

    let assetTypes = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/List`, {
      ...getAuthHeader(),
      cancelToken: cancelTokenSource.token,
    });
    let approvedVendors = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/ApprovedVendor/List/By/Task/asset request`,
      { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
    );

    axios
      .all([assetTypes, approvedVendors])
      .then(
        axios.spread((...responses) => {
          const assetTypeAPIResponse = !!responses[0] ? responses[0].data : null;
          setAssetTypes(assetTypeAPIResponse);

          const approvedVendorAPIResponse = !!responses[1] ? responses[1].data : null;

          setApprovedVendors(approvedVendorAPIResponse);
          setDataReady(true);
        })
      )
      .catch((err) => {
        ConsoleHelper(err);
      });
    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props, location.state]);

  //Auto-populate fields (business unit & asset type)
  useEffect(() => {
    if (location.state && dataReady) {
      let tempBusinessU = listBusinessUnits.find(
        (v) => v.name === location.state.vehicle.businessUnit
      );
      let reformatBusinessU = {};
      if (tempBusinessU) {
        reformatBusinessU = {
          name: tempBusinessU.name,
          code: tempBusinessU.business_unit_id,
        };
        setSelectedBusinessUnit(tempBusinessU);
        setDefaultBusinessUnit(reformatBusinessU);
      }
      let tempAssetType = assetTypes.find((v) => v.name === location.state.vehicle.asset_type);
      let reformatAssetType = {};
      if (tempAssetType) {
        reformatAssetType = {
          name: tempAssetType.name,
          code: tempAssetType.id,
        };
        setSelectedAssetType(tempAssetType);
        setDefaultAssetType(reformatAssetType);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state, dataReady]);

  useEffect(() => {
    // Clear below fields if asset type changes
    setManufDataReady(false);
    setSelectedAssetManufacturer(null);
    setAssetManufacturers(null);
    setSelectedJustification(null);
    if (selectedAssetType != null) {
      const cancelTokenSource = axios.CancelToken.source();
      let assetId = selectedAssetType.id;
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/${assetId}/Manufacturers`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((manufacturers) => {
          setAssetManufacturers(manufacturers.data);
          setManufDataReady(true);
        })
        .catch((err) => {
          ConsoleHelper(err);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
  }, [selectedAssetType]);

  //Auto-populate fields (manufacturer)
  useEffect(() => {
    if (location.state && manufDataReady) {
      let tempManufacturer = assetManufacturers.find(
        (v) => v.name === location.state.vehicle.manufacturer
      );
      let reformatManufacturer = {};
      if (tempManufacturer) {
        reformatManufacturer = {
          name: tempManufacturer.name,
          code: tempManufacturer.id,
        };
        setSelectedAssetManufacturer(tempManufacturer);
        setDefaultAssetManufacturer(reformatManufacturer);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state, manufDataReady]);

  useEffect(() => {
    // Clear below fields if asset manufacturer changes
    setEquipmentTypes(null);
    setSelectedEquipmentType(null);
    setSelectedJustification(null);
    setEquipDataReady(false);
    if (selectedAssetManufacturer != null && selectedAssetType != null) {
      const cancelTokenSource = axios.CancelToken.source();
      let assetId = selectedAssetType.id;
      let manufacturerId = selectedAssetManufacturer.id;
      axios
        .get(
          `${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/${assetId}/Manufacturer/${manufacturerId}/Equipments`,
          { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
        )
        .then((equipments) => {
          setEquipmentTypes(equipments.data);
          setEquipDataReady(true);
        })
        .catch((err) => {
          ConsoleHelper(err);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedAssetManufacturer]);

  //Auto-populate fields (manufacturer)
  useEffect(() => {
    if (location.state && equipDataReady) {
      let tempEquipmentType = equipmentTypes.find(
        (v) => v.model_number === location.state.vehicle.model_number
      );
      let reformatEquipmentType = {};
      if (tempEquipmentType) {
        reformatEquipmentType = {
          name: `${tempEquipmentType.model_number} ${
            tempEquipmentType.engine
              ? " - " + t("assetRequestPanel.engine_label") + tempEquipmentType.engine
              : ""
          } ${
            tempEquipmentType.fuel
              ? " - " + t("assetRequestPanel.fuel_label") + tempEquipmentType.fuel
              : ""
          }`,
          code: tempEquipmentType.equipment_type_id,
        };
        setSelectedEquipmentType(tempEquipmentType);
        setDefaultEquipmentType(reformatEquipmentType);
      }
      showSuccess();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state, equipDataReady]);

  useEffect(() => {
    setDisposalReported("");
    setAccidentReported("");
    if (selectedJustification != null && hideValues.includes(selectedJustification.name)) {
      setHideContent(true);
    } else {
      setHideContent(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedJustification]);

  useEffect(() => {
    if (disposalReported === true || accidentReported === true) {
      setHideContent(false);
    } else if (disposalReported === false || accidentReported === false) {
      setHideContent(true);
    }
  }, [disposalReported, accidentReported]);

  useEffect(() => {
    if (isTradeIn) {
      setDisposalDataReady(false);
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetDisposal/Get/Tradein/NoAssetRequest`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          setDisposalReports(response.data);
          setDisposalDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
  }, [isTradeIn]);

  let tradeInHeaders = [];
  let tradeInData = [];

  if (disposalReports) {
    tradeInHeaders = [
      { header: t("general.id"), colFilter: { field: "custom_id" } },
      { header: t("general.vin"), colFilter: { field: "VIN" } },
    ];

    tradeInData = disposalReports.map((disposal) => {
      return {
        id: disposal.id,
        dataPoint: disposal,
        cells: [disposal.custom_id, <VINLink vin={disposal.VIN} />],
      };
    });
  }

  const selectBusinessUnit = (id) => {
    let selected = listBusinessUnits.find((v) => v.business_unit_id === parseInt(id));
    setSelectedBusinessUnit(selected);
  };

  const selectAssetType = (id) => {
    let selected = assetTypes.find((v) => v.id === parseInt(id));
    setSelectedAssetType(selected);
  };

  const selectManufacturer = (id) => {
    let selected = assetManufacturers.find((v) => v.id === parseInt(id));
    setSelectedAssetManufacturer(selected);
  };

  const selectEquipment = (id) => {
    let selected = equipmentTypes.find((v) => v.equipment_type_id === parseInt(id));
    setSelectedEquipmentType(selected);
  };

  const selectJustification = (id) => {
    let selected = listAssetRequestJust.find((v) => v.justification_id === parseInt(id));
    setSelectedJustification(selected);
  };

  const selectTradeIn = (id) => {
    if (id === "Yes") setIsTradeIn(true);
    else setIsTradeIn(false);
  };

  const selectAccident = (id) => {
    if (id === "Yes") setAccidentReported(true);
    else setAccidentReported(false);
  };

  const selectDisposalReport = (id) => {
    if (id === "Yes") setDisposalReported(true);
    else setDisposalReported(false);
  };

  const handleTransferToDisposal = (e) => {
    e.preventDefault();
    history.push(`/asset-removal`);
  };

  const sendAssetRequest = (assetRequest) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetRequest/Add`, assetRequest, getAuthHeader())
      .then((res) => {
        successAlert();
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
        resetForm();
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  const handleSubmit = (event) => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    event.preventDefault();
    let assetRequestData = {
      business_unit: selectedBusinessUnit.business_unit_id,
      equipment: selectedEquipmentType.equipment_type_id,
      vendor_transport_to_client: vendorTransportToClient,
      date_required: requestDate,
      quote_deadline: quoteDeadline,
      justification: selectedJustification.justification_id,
      ...(approvedVendor === t("general.approved_vendors")
        ? {
            vendor: null, //TODO need to auto setup this in the future
            potential_vendor_ids: `-${multiSelectedVendor.map((el) => el.code).join("-")}-`,
          }
        : null),
      ...(approvedVendor === t("general.other_vendors") ? { vendor_email: vendorEmail } : null),
      ...(isTradeIn && { disposal: selectedDisposal.id }),
      quantity: quantity,
    };

    if (description) {
      assetRequestData["nonstandard_description"] = description;
    }

    const assetRequest = {
      asset_request_data: assetRequestData,
      // TODO: Replace the placeholder info for approval_data
      approval_data: {
        title: "Asset Order Approval",
        description: "This is an approval made for testing purposes.",
      },
    };

    sendAssetRequest(assetRequest);
  };

  let formFilled = false;
  if (
    selectedBusinessUnit &&
    selectedAssetType &&
    selectedAssetManufacturer &&
    selectedEquipmentType &&
    selectedJustification &&
    vendorTransportToClient !== null &&
    requestDate &&
    quantity &&
    isTradeIn !== ""
  ) {
    if (isTradeIn && !selectedDisposal) formFilled = false;
    else formFilled = true;
  }

  return (
    <div className="asset-request-form">
      <Toast ref={toastRef} />
      <div className="p-mt-5 p-mx-4 header">
        <div className="p-d-flex p-jc-between p-mb-2">
          <h3 className="p-mb-3">
            <FontAwesomeIcon className="p-mr-3" icon={faCartPlus} />
            {t("assetRequestPanel.panel_header")}
          </h3>
          <AddNewEquipType />
        </div>
        <form id="request-form" onSubmit={handleSubmit}>
          <div className="p-d-flex p-jc-between p-ai-center p-mb-2">
            <label className="h5">{t("assetRequest.business_unit")}</label>
            <div className="w-50">
              <FormDropdown
                reset={dropdownReset}
                onChange={selectBusinessUnit}
                options={
                  listBusinessUnits &&
                  listBusinessUnits.map((businessUnit) => ({
                    name: businessUnit.name,
                    code: businessUnit.business_unit_id,
                  }))
                }
                defaultValue={defaultBusinessUnit}
                loading={!listBusinessUnits}
                disabled={!listBusinessUnits}
                dataReady={listBusinessUnits}
                plain_dropdown
                leftStatus
              />
            </div>
          </div>
          <div className="p-d-flex p-jc-between p-ai-center p-mb-2">
            <label className="h5">{t("assetRequest.asset_type")}</label>
            <div className="w-50">
              <FormDropdown
                reset={dropdownReset}
                onChange={selectAssetType}
                options={
                  assetTypes &&
                  assetTypes.map((type) => ({
                    name: type.name,
                    code: type.id,
                  }))
                }
                defaultValue={defaultAssetType}
                loading={!dataReady}
                dataReady={dataReady}
                disabled={!assetTypes || !dataReady}
                plain_dropdown
                leftStatus
              />
            </div>
          </div>
          <div className="p-d-flex p-jc-between p-ai-center p-mb-2">
            <label className="h5">{t("assetRequest.manufacturer")}</label>
            <div className="w-50">
              <FormDropdown
                reset={dropdownReset || selectedAssetType}
                onChange={selectManufacturer}
                options={
                  assetManufacturers &&
                  assetManufacturers.map((manufacturer) => ({
                    name: manufacturer.name,
                    code: manufacturer.id,
                  }))
                }
                defaultValue={defaultAssetManufacturer}
                dataReady={manufDataReady}
                disabled={!selectedAssetType || !assetManufacturers}
                loading={!assetManufacturers && selectedAssetType}
                plain_dropdown
                leftStatus
              />
            </div>
          </div>
          <div className="p-d-flex p-jc-between p-ai-center p-mb-2">
            <label className="h5">{t("assetRequest.equipment_type")}</label>
            <div className="w-50">
              <FormDropdown
                reset={dropdownReset || selectedAssetManufacturer}
                onChange={selectEquipment}
                options={
                  equipmentTypes &&
                  equipmentTypes.map((type) => ({
                    name: `${type.model_number} ${
                      type.engine ? " - " + t("assetRequestPanel.engine_label") + type.engine : ""
                    } ${type.fuel ? " - " + t("assetRequestPanel.fuel_label") + type.fuel : ""}`,
                    code: type.equipment_type_id,
                  }))
                }
                defaultValue={defaultEquipmentType}
                dataReady={equipDataReady}
                disabled={!selectedAssetManufacturer}
                loading={!equipmentTypes && selectedAssetManufacturer}
                plain_dropdown
                leftStatus
              />
            </div>
          </div>
          <div className="p-d-flex p-jc-between p-ai-center p-mb-2">
            <label className="h5">{t("assetRequest.justification")}</label>
            <div className="w-50">
              <FormDropdown
                reset={dropdownReset || selectedEquipmentType}
                onChange={selectJustification}
                options={
                  listAssetRequestJust &&
                  listAssetRequestJust.map((justification) => ({
                    name: justification.name,
                    code: justification.justification_id,
                  }))
                }
                disabled={!selectedEquipmentType}
                plain_dropdown
                leftStatus
              />
            </div>
          </div>
          {selectedJustification && (
            <React.Fragment>
              {selectedJustification.name.toLowerCase() === "accident" && (
                <div className="p-d-flex p-jc-between p-ai-center p-mb-2">
                  <label className="h5">{t("assetRequest.accident_label")}</label>
                  <div className="w-50">
                    <FormDropdown
                      reset={dropdownReset}
                      onChange={selectAccident}
                      options={booleanOptions}
                      plain_dropdown
                      leftStatus
                    />
                  </div>
                </div>
              )}
              {(selectedJustification.name.toLowerCase() === "life cycle replacement" ||
                selectedJustification.name.toLowerCase() === "equipment failure") && (
                <div className="p-d-flex p-jc-between p-ai-center p-mb-2">
                  <label className="h5">{t("assetRequest.disposal_label")}</label>
                  <div className="w-50">
                    <FormDropdown
                      reset={dropdownReset}
                      onChange={selectDisposalReport}
                      options={booleanOptions}
                      plain_dropdown
                      leftStatus
                    />
                  </div>
                </div>
              )}
            </React.Fragment>
          )}
          {!hideContent && (
            <React.Fragment>
              <div className="p-d-flex p-flex-column">
                <VendorOption
                  dataReady={dataReady}
                  approvedVendors={approvedVendors}
                  approvedVendor={approvedVendor}
                  setApprovedVendor={setApprovedVendor}
                  multiSelectedVendor={multiSelectedVendor}
                  setMultiSelectedVendor={setMultiSelectedVendor}
                  vendorEmail={vendorEmail}
                  setVendorEmail={setVendorEmail}
                  setIsVendorSelected={setIsVendorSelected}
                  dropdownReset={dropdownReset}
                />
              </div>
              <div className="p-d-flex p-jc-between p-ai-center p-mb-2">
                <label className="h5">
                  {t("general.in_transit_to_client_label")}
                  <Tooltip
                    label="in_transit_to_client"
                    description={t("general.transport_to_client_question", {
                      request_type: "asset built",
                    })}
                  />
                </label>
                <div className="w-50">
                  <FormDropdown
                    reset={dropdownReset}
                    onChange={setVendorTransportToClient}
                    options={inTransitToClientOption}
                    loading={!inTransitToClientOption}
                    disabled={!inTransitToClientOption}
                    plain_dropdown
                    leftStatus
                  />
                </div>
              </div>
              {vendorTransportToClient !== null && (
                <div className="p-d-flex p-jc-between p-ai-center p-mb-2 date-picker">
                  <label className="h5">
                    {vendorTransportToClient
                      ? t("assetRequest.delivery_date_label")
                      : t("assetRequest.pickup_date_label")}
                  </label>
                  <div className="w-50">
                    <DatePicker
                      initialDate={requestDate}
                      onChange={setRequestDate}
                      minDate={new Date()}
                      required
                      leftStatus
                    />
                  </div>
                </div>
              )}
              <div className="p-d-flex p-jc-between p-ai-center p-mb-2 date-picker">
                <label className="h5">
                  {t("general.quote_deadline_label")}
                  <Tooltip
                    label="asset_quote_deadline"
                    description={t("general.quote_deadline_explanation")}
                  />
                </label>
                <div className="w-50">
                  <DatePicker
                    initialDate={quoteDeadline}
                    onChange={setQuoteDeadline}
                    minDate={new Date()}
                    required
                    leftStatus
                  />
                </div>
              </div>
              <div className="p-d-flex p-jc-between p-mb-2">
                <label className="h5">{t("assetRequest.quantity_label")}</label>
                <div className="w-50">
                  <CustomInputNumber
                    value={quantity}
                    onChange={setQuantity}
                    placeholder="Enter quantity"
                    max={4000}
                    leftStatus
                    style={{ width: "100%" }}
                  />
                </div>
              </div>
              <div className="p-d-flex p-jc-between p-mb-2">
                <label className="h5">{t("assetRequest.details_label")}</label>
                <div className="w-50">
                  <CustomTextArea
                    value={description}
                    onChange={setDescription}
                    rows={3}
                    leftStatus
                  />
                </div>
              </div>
              <div>
                <div className="p-d-flex p-jc-between p-ai-center p-mb-2">
                  <label className="h5">{t("assetRequest.is_trade_in_label")}</label>
                  <div className="w-50">
                    <FormDropdown
                      reset={dropdownReset}
                      onChange={selectTradeIn}
                      options={booleanOptions}
                      plain_dropdown
                      leftStatus
                    />
                  </div>
                </div>
                {isTradeIn ? (
                  disposalDataReady ? (
                    disposalReports.length !== 0 ? (
                      <div className="p-mt-3 tradein-msg-container">
                        <div className="tradein-msg">
                          <div className="p-d-flex p-ai-center p-ml-2 p-p-2">
                            <i className="pi pi-exclamation-circle p-mr-2">{""}</i>
                            <div>{t("assetRequestPanel.disposal_not_found_text")}</div>
                          </div>
                        </div>
                        <div className="darkTable p-mt-2">
                          <Table
                            dataReady={dataReady}
                            tableHeaders={tradeInHeaders}
                            tableData={tradeInData}
                            onSelectionChange={(disposal) => setSelectedDisposal(disposal)}
                            hasSelection
                            rows={5}
                            globalSearch={false}
                          />
                        </div>
                      </div>
                    ) : (
                      <div className="tradein-msg">
                        <div className="p-d-flex p-ai-center p-ml-2">
                          <i className="pi pi-exclamation-circle p-mr-2">{""}</i>
                          <div>{t("assetRequestPanel.disposal_not_submit_text")}</div>
                          <Button
                            label={t("assetRequestPanel.disposal_button")}
                            className="p-button-text"
                            onClick={handleTransferToDisposal}
                          />
                        </div>
                      </div>
                    )
                  ) : (
                    <div className="tradein-msg-pending w-100">
                      <div className="spinner-grow" role="status" style={{ color: "#8D249899" }}>
                        <span className="sr-only">{""}</span>
                      </div>
                      <div className="spinner-grow" role="status" style={{ color: "#8D249899" }}>
                        <span className="sr-only">{""}</span>
                      </div>
                      <div className="spinner-grow" role="status" style={{ color: "#8D249899" }}>
                        <span className="sr-only">{""}</span>
                      </div>
                    </div>
                  )
                ) : null}
              </div>
            </React.Fragment>
          )}
          {accidentReported === false && (
            <div className="btn-1 p-my-5 p-d-flex p-jc-end">
              <Button
                label={t("buttonLabels.complete_incident")}
                className="p-button-lg p-text-uppercase w-50"
                onClick={() => history.push("/incidents/new/")}
              />
            </div>
          )}
          {disposalReported === false && (
            <div className="btn-1 p-my-5 p-d-flex p-jc-end">
              <Button
                label={t("buttonLabels.complete_disposal")}
                className="p-button-lg p-text-uppercase w-50"
                onClick={() => history.push("/asset-removal")}
              />
            </div>
          )}
          {disposalReported !== false && accidentReported !== false && !hideContent && (
            <div className="btn-1 p-my-5 p-d-flex p-jc-end">
              <Button
                label={t("buttonLabels.complete_asset_request")}
                className="p-button-lg p-text-uppercase w-50"
                disabled={!formFilled}
              />
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default AssetOrderForm;