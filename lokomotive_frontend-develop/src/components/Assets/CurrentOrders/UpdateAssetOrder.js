import React, { useEffect, useState } from "react";
import axios from "axios";
import { useDispatch, useSelector } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import DatePicker from "../../ShareComponents/DatePicker";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import CustomInputNumber from "../../ShareComponents/CustomInputNumber";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";

const UpdateAssetOrder = ({
  request,
  editDialogStatus,
  setEditDialogStatus,
  setSelectedOrder,
  setRequests,
  requestType,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { listBusinessUnits, listAssetRequestJust } = useSelector((state) => state.apiCallData);
  const [defaultBusinessUnit, setDefaultBusinessUnit] = useState(null);
  const [selectedBusinessUnit, setSelectedBusinessUnit] = useState(null);
  const [assetTypes, setAssetTypes] = useState(null);
  const [defaultAssetType, setDefaultAssetType] = useState(null);
  const [selectedAssetType, setSelectedAssetType] = useState(null);
  const [assetManufacturers, setAssetManufacturers] = useState(null);
  const [defaultAssetManufacturer, setDefaultAssetManufacturer] = useState(null);
  const [selectedAssetManufacturer, setSelectedAssetManufacturer] = useState(null);
  const [equipmentTypes, setEquipmentTypes] = useState(null);
  const [defaultEquipmentType, setDefaultEquipmentType] = useState(null);
  const [selectedEquipmentType, setSelectedEquipmentType] = useState(null);
  const [defaultJustification, setDefaultJustification] = useState(null);
  const [selectedJustification, setSelectedJustification] = useState(null);
  const [initDataReady, setInitDataReady] = useState(false);
  const [manufDataReady, setManufDataReady] = useState(false);
  const [lastDataReady, setLastDataReady] = useState(false);
  const [requestDate, setRequestDate] = useState(
    request.date_required ? new Date(request.date_required) : null
  );
  const [description, setDescription] = useState("");
  const [estimatedCost, setEstimatedCost] = useState(null);
  const isExternalVendor =
    request.vendor_email &&
    !["", "NA"].includes(request.vendor_email) &&
    !request.potential_vendor_ids &&
    !request.vendor
      ? true
      : false;

  useEffect(() => {
    if (editDialogStatus) {
      setInitDataReady(false);
      setDefaultBusinessUnit(null);
      setDefaultAssetType(null);
      setRequestDate(request.date_required ? new Date(request.date_required) : null);
      setEstimatedCost(request.estimated_cost);
      if (request.nonstandard_description) setDescription(request.nonstandard_description);
      else setDescription("");

      let tempBusinessU = listBusinessUnits.find((v) => v.name === request.business_unit);
      let reformatBusinessU = {
        name: tempBusinessU.name,
        code: tempBusinessU.business_unit_id,
      };
      setSelectedBusinessUnit(tempBusinessU);
      setDefaultBusinessUnit(reformatBusinessU);

      const authHeader = getAuthHeader();
      let assetTypesAPI = axios.get(
        `${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/List`,
        authHeader
      );

      axios
        .all([assetTypesAPI])
        .then(
          axios.spread((...responses) => {
            const assetTypeAPIResponse = !!responses[0] ? responses[0].data : null;
            setAssetTypes(assetTypeAPIResponse);

            let tempAssetType = responses[0].data.find((v) => v.name === request.asset_type);
            let reformatAssetType = {
              name: tempAssetType.name,
              code: tempAssetType.id,
            };
            setSelectedAssetType(tempAssetType);
            setDefaultAssetType(reformatAssetType);

            setInitDataReady(true);
          })
        )
        .catch((err) => {
          ConsoleHelper(err);
        });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editDialogStatus, request]);

  useEffect(() => {
    if (initDataReady && selectedAssetType) {
      setManufDataReady(false);
      setSelectedAssetManufacturer(null);
      setDefaultAssetManufacturer(null);
      setLastDataReady(false);
      setEquipmentTypes(null);
      setSelectedEquipmentType(null);
      setDefaultEquipmentType(null);

      let assetId = selectedAssetType.id;
      axios
        .get(
          `${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/${assetId}/Manufacturers`,
          getAuthHeader()
        )
        .then((response) => {
          setAssetManufacturers(response.data);

          let tempManufacturer = response.data.find((v) => v.name === request.manufacturer);
          let reformatManufacturer = {};
          if (tempManufacturer) {
            reformatManufacturer = {
              name: tempManufacturer.name,
              code: tempManufacturer.id,
            };
            setSelectedAssetManufacturer(tempManufacturer);
            setDefaultAssetManufacturer(reformatManufacturer);
          } else {
            setSelectedAssetManufacturer(null);
            setDefaultAssetManufacturer(null);
          }

          setManufDataReady(true);
        })
        .catch((err) => {
          ConsoleHelper(err);
        });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initDataReady, selectedAssetType]);

  useEffect(() => {
    if (manufDataReady && selectedAssetManufacturer) {
      setLastDataReady(false);
      setDefaultEquipmentType(null);
      setDefaultJustification(null);

      let tempJustification = listAssetRequestJust.find((v) => v.name === request.justification);
      let reformatJustification = {
        name: tempJustification.name,
        code: tempJustification.justification_id,
      };
      setSelectedJustification(tempJustification);
      setDefaultJustification(reformatJustification);

      const authHeader = getAuthHeader();
      let assetId = selectedAssetType.id;
      let manufacturerId = selectedAssetManufacturer.id;

      let equipmentAPI = axios.get(
        `${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/${assetId}/Manufacturer/${manufacturerId}/Equipments`,
        authHeader
      );

      axios
        .all([equipmentAPI])
        .then(
          axios.spread((...responses) => {
            const equipmentAPIResponse = !!responses[0] ? responses[0].data : null;
            setEquipmentTypes(equipmentAPIResponse);

            let tempEquipmentType = responses[0].data.find(
              (v) => v.model_number === request.model_number
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
            } else {
              setSelectedEquipmentType(null);
              setDefaultEquipmentType(null);
            }
            setLastDataReady(true);
          })
        )
        .catch((err) => {
          ConsoleHelper(err);
        });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [manufDataReady, selectedAssetManufacturer]);

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

  const handleAssetRequestUpdate = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let assetRequest = {
      asset_request_id: request.id,
      business_unit_id: selectedBusinessUnit.business_unit_id,
      equipment_type_id: selectedEquipmentType.equipment_type_id,
      justification_id: selectedJustification.justification_id,
      date_required: requestDate.toISOString().replace("T", " ").split("Z")[0],
      nonstandard_description: description,
      ...(isExternalVendor ? { estimated_cost: estimatedCost } : null),
    };
    handleUpdateSubmit(assetRequest);
  };

  const handleUpdateSubmit = (data) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetRequest/Update`, data, getAuthHeader())
      .then(async (res) => {
        setEditDialogStatus(false);
        refreshData(data);
      })
      .catch((error) => {
        ConsoleHelper(error);
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  const refreshData = async (data) => {
    const cancelTokenSource = axios.CancelToken.source();
    let response = await axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/AssetRequest/${requestType}/List`,
      {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      }
    );

    const orders = response ? response.data : [];

    for (let i in orders) {
      if (!orders[i].vendor) {
        if (orders[i].vendor_email && !["", "NA"].includes(orders[i].vendor_email)) {
          orders[i].vendor_name = orders[i].vendor_email;
        }
      }
    }

    const selectedOrder = orders.filter((o) => o.id === data.asset_request_id);

    setRequests(orders);
    setSelectedOrder(selectedOrder[0]);
    successAlert("msg", t("assetOrderDetails.success_alert_text"));
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label={t("general.cancel")}
          icon="pi pi-times"
          onClick={() => setEditDialogStatus(false)}
          className="p-button-text"
        />
        <Button
          label={t("general.submit")}
          icon="pi pi-check"
          onClick={handleAssetRequestUpdate}
          disabled={
            !initDataReady ||
            !manufDataReady ||
            !lastDataReady ||
            !selectedBusinessUnit ||
            !selectedAssetType ||
            !selectedAssetManufacturer ||
            !selectedEquipmentType ||
            !selectedJustification ||
            !requestDate ||
            !description ||
            (isExternalVendor && estimatedCost === null)
          }
          autoFocus
        />
      </div>
    );
  };

  return (
    <Dialog
      className="custom-main-dialog"
      header={t("assetRequest.edit_asset_request_header")}
      visible={editDialogStatus}
      onHide={() => setEditDialogStatus(false)}
      style={{ width: "50vw" }}
      breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
      footer={renderFooter}
    >
      <div className="p-field">
        <label>{t("assetRequest.business_unit")}</label>
        <FormDropdown
          onChange={selectBusinessUnit}
          options={
            listBusinessUnits &&
            listBusinessUnits.map((businessUnit) => ({
              name: businessUnit.name,
              code: businessUnit.business_unit_id,
            }))
          }
          defaultValue={defaultBusinessUnit}
          loading={!defaultBusinessUnit}
          disabled={!defaultBusinessUnit}
          dataReady={defaultBusinessUnit}
          plain_dropdown
          leftStatus
          reset={"disabled"}
        />
      </div>
      <div className="p-field">
        <label>{t("assetRequest.asset_type")}</label>
        <FormDropdown
          onChange={selectAssetType}
          options={
            assetTypes &&
            assetTypes.map((type) => ({
              name: type.name,
              code: type.id,
            }))
          }
          defaultValue={defaultAssetType}
          loading={!initDataReady}
          disabled={!initDataReady}
          dataReady={initDataReady}
          plain_dropdown
          leftStatus
        />
      </div>
      <div className="p-field">
        <label>{t("assetRequest.manufacturer")}</label>
        <FormDropdown
          onChange={selectManufacturer}
          options={
            assetManufacturers &&
            assetManufacturers.map((manufacturer) => ({
              name: manufacturer.name,
              code: manufacturer.id,
            }))
          }
          defaultValue={defaultAssetManufacturer}
          loading={!manufDataReady}
          disabled={!manufDataReady}
          dataReady={manufDataReady}
          plain_dropdown
          leftStatus
        />
      </div>
      <div className="p-field">
        <label>{t("assetRequest.equipment_type")}</label>
        <FormDropdown
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
          loading={!lastDataReady && selectedAssetManufacturer}
          disabled={
            !initDataReady || !manufDataReady || !lastDataReady || !selectedAssetManufacturer
          }
          dataReady={lastDataReady}
          plain_dropdown
          leftStatus
        />
      </div>
      <div className="p-field">
        <label>{t("assetRequest.justification")}</label>
        <FormDropdown
          onChange={selectJustification}
          options={
            listAssetRequestJust &&
            listAssetRequestJust.map((justification) => ({
              name: justification.name,
              code: justification.justification_id,
            }))
          }
          defaultValue={defaultJustification}
          loading={!lastDataReady && selectedAssetManufacturer}
          disabled={
            !initDataReady || !manufDataReady || !lastDataReady || !selectedAssetManufacturer
          }
          dataReady={lastDataReady}
          plain_dropdown
          leftStatus
        />
      </div>
      {isExternalVendor && (
        <div className="p-field">
          <label>{t("assetRequest.estimated_cost_label")}</label>
          <CustomInputNumber
            value={estimatedCost}
            onChange={setEstimatedCost}
            className="w-100"
            mode="decimal"
            min={0}
            minFractionDigits={2}
            maxFractionDigits={2}
            max={2147483646}
            leftStatus
          />
        </div>
      )}
      <div className="p-field">
        <label>
          {request.vendor_transport_to_client
            ? t("assetRequest.delivery_date_label")
            : t("assetRequest.pickup_date_label")}
          <Tooltip
            label="transport_to_client"
            description={t(
              request.vendor_transport_to_client
                ? "general.transport_to_client_delivery"
                : "general.transport_to_client_pickup",
              { request_type: "asset request" }
            )}
          />
        </label>
        <div className="p-fluid p-grid p-formgrid">
          <div className="p-col-12">
            <DatePicker
              onChange={setRequestDate}
              initialDate={requestDate}
              minDate={new Date()}
              leftStatus
            />
          </div>
        </div>
      </div>
      <div className="p-field">
        <label>{t("assetRequest.details_label")}</label>
        <CustomTextArea
          className="w-100"
          rows={5}
          value={description}
          required
          onChange={setDescription}
          leftStatus
        />
      </div>
    </Dialog>
  );
};

export default UpdateAssetOrder;
