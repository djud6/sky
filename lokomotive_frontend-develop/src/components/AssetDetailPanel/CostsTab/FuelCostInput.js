import React, { useState, useEffect } from "react";
import axios from "axios";
import { useDispatch, useSelector } from "react-redux";
import { getAuthHeader } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { useRequestedData } from "../../../hooks/dataDetcher";
import { successAlert, loadingAlert, errorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import CustomInputText from "../../ShareComponents/CustomInputText";
import "../../../styles/helpers/button5.scss";

export const updateData = (url, data, setLoading, reset, tryAgainCallback, refresh) => {
  setLoading(true);
  loadingAlert();
  axios
    .post(`${Constants.ENDPOINT_PREFIX}${url}`, data, getAuthHeader())
    .then(() => {
      setLoading(false);
      successAlert();
      reset();
      if (!!refresh) refresh(new Date());
    })
    .catch((error) => {
      setLoading(false);
      ConsoleHelper(error);
      errorAlert(error.customErrorMsg, tryAgainCallback);
    });
};

export default function FuelCostInput({ vin, refresh }) {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { listCurrencies, listFuelUnits } = useSelector((state) => state.apiCallData);
  let fuelTypes;
  let currencyTypes = listCurrencies;
  let volumeUnits = listFuelUnits.volume_unit_choices.map((unit) => {
    return { name: unit };
  });

  const urlArray = ["api/v1/Fuel/Get/All/FuelTypes"];

  const [dataReady, dataArray1, errors] = useRequestedData(urlArray);

  if (dataReady) {
    if (errors) {
      ConsoleHelper("errors:", errors);
    }
    fuelTypes = dataArray1;
  }

  const [loading, setLoading] = useState(false);
  //Fuel
  const [fuelType, setFuelType] = useState("");
  const [fuelVolume, setFuelVolume] = useState("");
  const [fuelVolumeUnit, setFuelVolumeUnit] = useState(null);
  const [fuelTotalCost, setFuelTotalCost] = useState("");
  const [fuelTaxes, setFuelTaxes] = useState("");
  const [fuelCurrency, setFuelCurrency] = useState(null);
  const [fuelError, setFuelError] = useState(true);
  const [dropdownReset, setDropdownReset] = useState(false);

  const fuelReset = () => {
    setFuelType("");
    setFuelVolume("");
    setFuelVolumeUnit(null);
    setFuelTotalCost("");
    setFuelTaxes("");
    setFuelCurrency(null);
    setFuelError(true);
    setDropdownReset(!dropdownReset);
  };

  const handleFuelSubmit = () => {
    if (
      !fuelType ||
      !fuelVolume ||
      !fuelVolumeUnit ||
      !fuelTotalCost ||
      !fuelTaxes ||
      !fuelCurrency
    ) {
      setFuelError(true);
    } else {
      dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
      updateData(
        "/api/v1/Fuel/Add/Cost",
        {
          VIN: vin,
          fuel_type: fuelType.id,
          volume: fuelVolume,
          volume_unit: fuelVolumeUnit.name,
          total_cost: fuelTotalCost,
          taxes: fuelTaxes,
          currency: fuelCurrency.id,
        },
        setLoading,
        fuelReset,
        handleFuelSubmit,
        refresh
      );
    }
  };

  useEffect(() => {
    if (fuelType && fuelVolume && fuelVolumeUnit && fuelTotalCost && fuelTaxes && fuelCurrency) {
      setFuelError(false);
    } else {
      setFuelError(true);
    }
  }, [fuelType, fuelVolume, fuelVolumeUnit, fuelTotalCost, fuelTaxes, fuelCurrency]);

  const selectFuelType = (id) => {
    let selected = fuelTypes.find((v) => v.id === parseInt(id));
    setFuelType(selected);
  };

  const selectFuelVolumeUnit = (name) => {
    let selected = volumeUnits.find((v) => v.name === name);
    setFuelVolumeUnit(selected);
  };

  const selectFuelCurrency = (id) => {
    let selected = currencyTypes.find((v) => v.id === parseInt(id));
    setFuelCurrency(selected);
  };

  return (
    <React.Fragment>
      <div className="cost-input p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.fuel_type")}</label>
        <FormDropdown
          reset={dropdownReset}
          onChange={selectFuelType}
          options={
            fuelTypes &&
            fuelTypes.map((fuelType) => ({
              name: fuelType.name,
              code: fuelType.id,
            }))
          }
          loading={!dataReady}
          disabled={!fuelTypes || !dataReady}
          dataReady={dataReady}
          plain_dropdown
          leftStatus
        />
      </div>

      <div className="cost-input p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.fuel_volume")}</label>
        <CustomInputText
          type="number"
          placeholder={t("costsTab.fuel_volume")}
          value={fuelVolume}
          onChange={(val) => setFuelVolume(parseFloat(val))}
          leftStatus
        />
      </div>

      <div className="cost-input p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.fuel_volume_units")}</label>
        <FormDropdown
          reset={dropdownReset}
          onChange={selectFuelVolumeUnit}
          options={
            volumeUnits &&
            volumeUnits.map((volumeUnit) => ({
              name: volumeUnit.name,
              code: volumeUnit.name,
            }))
          }
          loading={!volumeUnits}
          disabled={!volumeUnits}
          dataReady={volumeUnits}
          plain_dropdown
          leftStatus
        />
      </div>
      <div className="cost-input p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.currency")}</label>
        <FormDropdown
          reset={dropdownReset}
          onChange={selectFuelCurrency}
          options={
            currencyTypes &&
            currencyTypes.map((currencyType) => ({
              name: currencyType.code,
              code: currencyType.id,
            }))
          }
          loading={!currencyTypes}
          disabled={!currencyTypes}
          dataReady={currencyTypes}
          plain_dropdown
          leftStatus
        />
      </div>

      <div className="cost-input p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.total_cost")}</label>
        <CustomInputText
          type="number"
          placeholder={t("costsTab.total_cost")}
          value={fuelTotalCost}
          onChange={(val) => setFuelTotalCost(parseFloat(val))}
          leftStatus
        />
      </div>

      <div className="cost-input p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.taxes")}</label>
        <CustomInputText
          type="number"
          placeholder={t("costsTab.taxes")}
          value={fuelTaxes}
          onChange={(val) => setFuelTaxes(parseFloat(val))}
          leftStatus
        />
      </div>

      <div className="cost-input-btn p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <div className="p-d-flex p-jc-center p-mt-3 p-mb-5">
          <div className="btn-5 disable-bg">
            <Button
              label={loading ? t("costsTab.button_loading") : t("costsTab.button_new_fuel_order")}
              icon={loading ? "pi pi-spin pi-spinner" : "pi pi-check"}
              disabled={loading || fuelError}
              onClick={() => {
                handleFuelSubmit();
              }}
            />
          </div>
        </div>
      </div>
    </React.Fragment>
  );
}
