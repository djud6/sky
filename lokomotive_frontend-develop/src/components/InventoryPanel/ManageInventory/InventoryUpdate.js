import React, { useEffect, useState } from "react";
import axios from "axios";
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
import moment from "moment";

const InventoryUpdate = ({
  updateDialog,
  setUpdateDialog,
  inventory,
  setSelectedInventory,
  setInventory,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [inventoryType, setInventoryType] = useState("");
  const [description, setDescription] = useState("");
  const [unitCost, setUnitCost] = useState(null);
  const [dateOfManuf, setDateOfManuf] = useState(new Date());
  const [locations, setLocations] = useState(null);
  const [isLocationsReady, setIsLocationsReady] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [defaultLocation, setDefaultLocation] = useState(null);
  const [reset, setReset] = useState(true);

  useEffect(() => {
    if (inventory) {
      setInventoryType(inventory.inventory_type);
      setDescription(inventory.description);
      setUnitCost(inventory.per_unit_cost);
      setDateOfManuf(new Date(inventory.date_of_manufacture));
    }
  }, [inventory]);

  // GET LOCATIONS
  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();

    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Location/List`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((res) => {
        const data = res.data;
        setLocations(data);
        setIsLocationsReady(true);
      })
      .catch((error) => {
        ConsoleHelper(error);
      });

    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call from custom hook");
    };
  }, []);

  //PRESET EXIESTING LOCATION
  useEffect(() => {
    if (isLocationsReady && locations && inventory && reset) {
      const existingLocation = locations.find(
        (loc) => loc.location_name.toLowerCase() === inventory.location?.toLowerCase()
      );
      let reformatExistingLocation = null;
      if (existingLocation) {
        reformatExistingLocation = {
          name: existingLocation.location_name,
          code: existingLocation.location_id,
        };
      }
      setDefaultLocation(reformatExistingLocation);
      setSelectedLocation(existingLocation);
      setReset(false);
    }
  }, [inventory, isLocationsReady, locations, reset]);

  const handleUpdate = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    const updateData = {
      inventory_type: inventoryType,
      description: description,
      per_unit_cost: unitCost,
      date_of_manufacture: moment(dateOfManuf).format("YYYY-MM-DD"),
      location: selectedLocation.location_id,
    };
    const formData = {
      inventory_id: inventory.id,
      update_data: updateData,
    };

    handleUpdateSubmit(formData);
  };

  const handleUpdateSubmit = (data) => {
    loadingAlert();

    let url = `${Constants.ENDPOINT_PREFIX}/api/v1/Inventory/Update`;

    axios
      .post(url, data, getAuthHeader())
      .then(() => {
        setUpdateDialog(false);
        refreshData(data);
      })
      .catch((err) => {
        ConsoleHelper(err);
        generalErrorAlert(err.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  const refreshData = (data) => {
    const cancelTokenSource = axios.CancelToken.source();

    let requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Inventory/List`;

    axios
      .get(requestURL, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((res) => {
        let selectedInventory;
        const allInventory = res.data;
        for (let i in allInventory) {
          if (allInventory[i].id === data.inventory_id) {
            selectedInventory = allInventory[i];
          }
        }

        setSelectedInventory(selectedInventory);
        setInventory(allInventory);
        successAlert("msg", t("inventoryPanelIndex.success_update_inventory"));
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
      });
  };

  const selectLocation = (id) => {
    let selected = locations.find((v) => v.location_id === parseInt(id));
    setSelectedLocation(selected);
  };

  const onHide = () => {
    setUpdateDialog(false);
    setInventoryType(inventory.inventory_type);
    setDescription(inventory.description);
    setUnitCost(inventory.per_unit_cost);
    setDateOfManuf(new Date(inventory.date_of_manufacture));
    setReset(true);
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label={t("general.submit")}
          icon="pi pi-check"
          onClick={handleUpdate}
          disabled={
            !inventoryType || !description || !unitCost || !dateOfManuf || !selectedLocation
          }
          autoFocus
        />
      </div>
    );
  };

  return (
    <Dialog
      className="custom-main-dialog"
      header={t("inventoryPanelIndex.update_inventory")}
      visible={updateDialog}
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
          defaultValue={defaultLocation}
          onChange={selectLocation}
          options={
            locations &&
            locations.map((loc) => ({
              name: loc.location_name,
              code: loc.location_id,
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

export default InventoryUpdate;
