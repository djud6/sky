import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { useRequestedData } from "../../../hooks/dataDetcher";
import { updateData } from "./FuelCostInput";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import CustomInputText from "../../ShareComponents/CustomInputText";
import "../../../styles/helpers/button5.scss";

export default function InsuranceCostInput({ vin, refresh }) {
  const { t } = useTranslation();
  const { listCurrencies } = useSelector((state) => state.apiCallData);
  let accidents;

  const urlArray = [`/api/v1/Accident/VIN/${vin}`];
  const [dataReady, dataArray1, errors] = useRequestedData(urlArray);
  if (dataReady) {
    if (errors) {
      ConsoleHelper("errors:", errors);
    }
    accidents = dataArray1;
  }

  const [loading, setLoading] = useState(false);
  const [insuranceAccident, setInsuranceAccident] = useState(null);
  const [insuranceDeductible, setInsuranceDeductible] = useState("");
  const [insuranceTotalCost, setInsuranceTotalCost] = useState("");
  const [insuranceCurrency, setInsuranceCurrency] = useState(null);
  const [insuranceError, setInsuranceError] = useState(true);
  const [dropdownReset, setDropdownReset] = useState(false);

  const handleInsuranceSubmit = () => {
    if (!insuranceAccident || !insuranceCurrency || !insuranceTotalCost || !insuranceDeductible) {
      setInsuranceError(true);
    } else {
      updateData(
        "/api/v1/Insurance/Add/Cost",
        {
          accident: insuranceAccident.accident_id,
          deductible: insuranceDeductible,
          total_cost: insuranceTotalCost,
          currency: insuranceCurrency.id,
        },
        setLoading,
        insuranceReset,
        handleInsuranceSubmit,
        refresh
      );
    }
  };
  const insuranceReset = () => {
    setInsuranceAccident(null);
    setInsuranceCurrency(null);
    setInsuranceTotalCost("");
    setInsuranceDeductible("");
    setInsuranceError(true);
    setDropdownReset(!dropdownReset);
  };

  useEffect(() => {
    if (insuranceAccident && insuranceDeductible && insuranceTotalCost && insuranceCurrency) {
      setInsuranceError(false);
    } else {
      setInsuranceError(true);
    }
  }, [insuranceAccident, insuranceDeductible, insuranceTotalCost, insuranceCurrency]);

  const selectInsuranceAccident = (id) => {
    let selected = accidents.find((v) => v.custom_id === id);
    setInsuranceAccident(selected);
  };

  const selectInsuranceCurrency = (id) => {
    let selected = listCurrencies.find((v) => v.id === parseInt(id));
    setInsuranceCurrency(selected);
  };

  return (
    <React.Fragment>
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <FormDropdown
          label={t("costsTab.accident_id")}
          reset={dropdownReset}
          onChange={selectInsuranceAccident}
          options={
            accidents &&
            accidents.map((accident) => ({
              name: accident.custom_id,
              code: accident.custom_id,
            }))
          }
          loading={!dataReady}
          disabled={!accidents || !dataReady}
          dataReady={dataReady}
          plain_dropdown
          leftStatus
        />
      </div>

      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <FormDropdown
          label={t("costsTab.currency")}
          reset={dropdownReset}
          onChange={selectInsuranceCurrency}
          options={
            listCurrencies &&
            listCurrencies.map((currencyType) => ({
              name: currencyType.code,
              code: currencyType.id,
            }))
          }
          loading={!listCurrencies}
          disabled={!listCurrencies}
          dataReady={listCurrencies}
          plain_dropdown
          leftStatus
        />
      </div>

      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.insurance_deductible")}</label>
        <CustomInputText
          type="number"
          placeholder={t("costsTab.insurance_deductible")}
          value={insuranceDeductible}
          onChange={(val) => setInsuranceDeductible(parseFloat(val))}
          leftStatus
        />
      </div>

      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.total_cost")}</label>
        <CustomInputText
          type="number"
          placeholder={t("costsTab.total_cost")}
          value={insuranceTotalCost}
          onChange={(val) => setInsuranceTotalCost(parseFloat(val))}
          leftStatus
        />
      </div>

      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <div className="p-d-flex p-jc-center p-mt-3 p-mb-5">
          <div className="btn-5 disable-bg">
            <Button
              label={loading ? t("costsTab.button_loading") : t("costsTab.button_new_insurance")}
              icon={loading ? "pi pi-spin pi-spinner" : "pi pi-check"}
              disabled={loading || insuranceError}
              onClick={() => {
                handleInsuranceSubmit();
              }}
            />
          </div>
        </div>
      </div>
    </React.Fragment>
  );
}
