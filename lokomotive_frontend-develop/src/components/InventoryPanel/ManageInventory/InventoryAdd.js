import React, { useEffect, useState } from "react";
import axios from "axios";
import moment from "moment";
import { useTranslation } from "react-i18next";
import * as Constants from "../../../constants";
import { useDispatch } from "react-redux";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import { getAuthHeader } from "../../../helpers/Authorization";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import DatePicker from "../../ShareComponents/DatePicker";
import CustomInputNumber from "../../ShareComponents/CustomInputNumber";
import CustomInputText from "../../ShareComponents/CustomInputText";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";

const InventoryAdd = ({ setDataReady, addDialog, setAddDialog }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [inventoryType, setInventoryType] = useState("");
  const [description, setDescription] = useState("");
  const [unitCost, setUnitCost] = useState(null);
  const [dateOfManuf, setDateOfManuf] = useState(new Date());
  const [locations, setLocations] = useState(null);
  const [isLocationsReady, setIsLocationsReady] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [assetTypes, setAssetTypes] = useState(null);
  const [manufacturers, setManufacturers] = useState(null);
  const [equipmentTypes, setEquipmentTypes] = useState(null);
  const [selectedAssetType, setSelectedAssetType] = useState(null);
  const [selectedManufacturer, setSelectedManufacturer] = useState(null);
  const [selectedEquipment, setSelectedEquipment] = useState(null);
  const [assetDataReady, setAssetDataReady] = useState(false);
  const [manufDataReady, setManufDataReady] = useState(false);
  const [equipDataReady, setEquipDataReady] = useState(false);
  const [formFilled, setFormFilled] = useState(false);

  // GET LOCATIONS
  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();

    if (addDialog) {
      const callback1 = (res) => {
        const data = res.data;
        setLocations(data);
        setIsLocationsReady(true);
      };

      const callback2 = (res) => {
        const data = res.data;
        const assetTypes = [{ id: 99999, name: "N/A" }].concat(data);
        setAssetTypes(assetTypes);
        setAssetDataReady(true);
      };

      const errorHandler = (error) => {
        ConsoleHelper(error);
      };

      const locationRequest = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Location/List`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });
      const assetTypesRequest = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/List`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });

      Promise.allSettled([locationRequest, assetTypesRequest])
        .then((results) => {
          [callback1, callback2].forEach((cb, index) => {
            if (results[index].status === "fulfilled") {
              cb(results[index].value);
            } else if (results[index].status === "rejected") {
              errorHandler(results[index].reason);
            }
          });
        })
        .catch(errorHandler);
    }

    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call from custom hook");
    };
  }, [addDialog]);

  useEffect(() => {
    setManufacturers(null);
    setSelectedManufacturer(null);
    const cancelTokenSource = axios.CancelToken.source();
    if (selectedAssetType && selectedAssetType.name !== "N/A") {
      axios
        .get(
          `${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/${selectedAssetType.id}/Manufacturers`,
          {
            ...getAuthHeader(),
            cancelToken: cancelTokenSource.token,
          }
        )
        .then((res) => {
          const data = res.data;
          setManufacturers(data);
          setManufDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
    }
  }, [selectedAssetType]);

  useEffect(() => {
    setEquipmentTypes(null);
    setSelectedEquipment(null);
    const cancelTokenSource = axios.CancelToken.source();
    if (selectedAssetType && selectedManufacturer) {
      axios
        .get(
          `${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/${selectedAssetType.id}/Manufacturer/${selectedManufacturer.id}/Equipments`,
          {
            ...getAuthHeader(),
            cancelToken: cancelTokenSource.token,
          }
        )
        .then((res) => {
          const data = res.data;
          setEquipmentTypes(data);
          setEquipDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
    }
  }, [selectedAssetType, selectedManufacturer]);

  useEffect(() => {
    if (!inventoryType || !description || !unitCost || !dateOfManuf || !selectedLocation) {
      setFormFilled(false);
    } else {
      if (!selectedAssetType) {
        setFormFilled(false);
      } else {
        if (selectedAssetType.name !== "N/A") {
          if (selectedManufacturer && selectedEquipment) {
            setFormFilled(true);
          } else setFormFilled(false);
        } else if (selectedAssetType.name === "N/A") {
          setFormFilled(true);
        }
      }
    }
  }, [
    dateOfManuf,
    description,
    inventoryType,
    selectedAssetType,
    selectedEquipment,
    selectedLocation,
    selectedManufacturer,
    unitCost,
  ]);

  const handleUpdate = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    const updateData = {
      custom_id: `${description}-${inventoryType}`,
      inventory_type: inventoryType,
      description: description,
      per_unit_cost: unitCost,
      date_of_manufacture: moment(dateOfManuf).format("YYYY-MM-DD"),
      location: selectedLocation.location_id,
      ...(selectedEquipment && { equipment_type: selectedEquipment.equipment_type_id }),
    };

    handleUpdateSubmit(updateData);
  };

  const handleUpdateSubmit = (data) => {
    loadingAlert();

    let url = `${Constants.ENDPOINT_PREFIX}/api/v1/Inventory/Add`;

    axios
      .post(url, data, getAuthHeader())
      .then(() => {
        onHide();
        refreshData(data);
      })
      .catch((err) => {
        ConsoleHelper(err);
        generalErrorAlert(err.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  const refreshData = (data) => {
    setDataReady(false);
    successAlert("msg", t("inventoryPanelIndex.success_add_inventory"));
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
  };

  const selectLocation = (id) => {
    let selected = locations.find((v) => v.location_id === parseInt(id));
    setSelectedLocation(selected);
  };

  const selectAssetType = (id) => {
    let selected = assetTypes.find((v) => v.id === parseInt(id));
    setSelectedAssetType(selected);
  };

  const selectManufacturer = (id) => {
    let selected = manufacturers.find((v) => v.id === parseInt(id));
    setSelectedManufacturer(selected);
  };

  const selectEquipment = (id) => {
    let selected = equipmentTypes.find((v) => v.equipment_type_id === parseInt(id));
    setSelectedEquipment(selected);
  };

  const onHide = () => {
    setAddDialog(false);
    setInventoryType("");
    setDescription("");
    setUnitCost(null);
    setDateOfManuf(new Date());
    setSelectedLocation(null);
    setAssetTypes(null);
    setSelectedAssetType(null);
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label={t("general.submit")}
          icon="pi pi-check"
          onClick={handleUpdate}
          disabled={!formFilled}
          autoFocus
        />
      </div>
    );
  };

  return (
    <Dialog
      className="custom-main-dialog"
      header={t("inventoryPanelIndex.add_inventory")}
      visible={addDialog}
      onHide={onHide}
      style={{ width: "50vw" }}
      breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
      footer={renderFooter}
    >
      <div className="p-field">
        <label>{t("inventoryPanelIndex.inventory_type")}</label>
        <CustomInputText onChange={(v) => setInventoryType(v)} value={inventoryType} leftStatus />
      </div>
      <div className="p-field">
        <label>{t("inventoryPanelIndex.description")}</label>
        <CustomTextArea
          rows={3}
          value={description}
          onChange={setDescription}
          required
          autoResize
          leftStatus
        />
      </div>
      <div className="p-field">
        <label>{t("inventoryPanelIndex.location")}</label>
        <FormDropdown
          onChange={selectLocation}
          options={
            locations &&
            locations.map((loc) => ({
              name: loc?.location_name,
              code: loc?.location_id,
            }))
          }
          reset="disabled"
          loading={!isLocationsReady}
          dataReady={isLocationsReady}
          disabled={!locations || !isLocationsReady}
          plain_dropdown
          leftStatus
        />
      </div>
      <div className="p-field">
        <label>{t("assetRequest.asset_type")}</label>
        <FormDropdown
          onChange={selectAssetType}
          options={
            assetTypes &&
            assetTypes.map((type) => ({
              name: type?.name,
              code: type?.id,
            }))
          }
          reset="disabled"
          loading={!assetDataReady}
          dataReady={assetDataReady}
          disabled={!assetDataReady}
          plain_dropdown
          leftStatus
        />
      </div>
      {selectedAssetType && selectedAssetType.name !== "N/A" ? (
        <React.Fragment>
          <div className="p-field">
            <label>{t("assetRequest.manufacturer")}</label>
            <FormDropdown
              onChange={selectManufacturer}
              options={
                manufacturers &&
                manufacturers.map((manuf) => ({
                  name: manuf?.name,
                  code: manuf?.id,
                }))
              }
              reset={manufacturers && "disabled"}
              loading={!manufDataReady && selectedAssetType}
              dataReady={manufDataReady}
              disabled={!manufDataReady || !selectedAssetType}
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
                equipmentTypes.map((equip) => ({
                  name: equip?.model_number,
                  code: equip?.equipment_type_id,
                }))
              }
              reset={equipmentTypes && "disabled"}
              loading={!equipDataReady && selectedManufacturer}
              dataReady={equipDataReady}
              disabled={!equipDataReady || !selectedManufacturer}
              plain_dropdown
              leftStatus
            />
          </div>
        </React.Fragment>
      ) : null}
      <div className="p-field">
        <label>{t("inventoryPanelIndex.per_unit_cost")}</label>
        <CustomInputNumber
          value={unitCost}
          onChange={(v) => setUnitCost(v)}
          className="w-100"
          mode="decimal"
          minFractionDigits={2}
          maxFractionDigits={2}
          max={2147483646}
          leftStatus
        />
      </div>
      <div className="p-field">
        <label>{t("inventoryPanelIndex.date_of_manufacture")}</label>
        <div className="p-fluid p-grid p-formgrid">
          <div className="p-col-12">
            <DatePicker onChange={setDateOfManuf} initialDate={dateOfManuf} leftStatus />
          </div>
        </div>
      </div>
    </Dialog>
  );
};

export default InventoryAdd;
