import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { updateData } from "./FuelCostInput";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import CustomInputText from "../../ShareComponents/CustomInputText";

const AcquisitionCostInput = ({ vin, refresh }) => {
  const { t } = useTranslation();
  const { listCurrencies } = useSelector((state) => state.apiCallData);
  const [loading, setLoading] = useState(false);
  const [miscCost, setMiscCost] = useState("");
  const [adminCost, setAdminCost] = useState("");
  const [totalCost, setTotalCost] = useState("");
  const [taxes, setTaxes] = useState("");
  const [dropdownReset, setDropdownReset] = useState(false);
  const [currency, setCurrency] = useState(null);

  useEffect(() => {
    let autoCalculate = 
      parseFloat(miscCost ? miscCost : "0") + 
      parseFloat(adminCost ? adminCost : "0") + 
      parseFloat(taxes ? taxes : "0");
      
    setTotalCost(autoCalculate);
  }, [miscCost, adminCost, taxes]);

  const handleSubmit = () => {
    updateData(
      "/api/v1/Acquisition/Add/Cost",
      {
        VIN: vin,
        total_cost: totalCost,
        taxes: taxes, 
        administrative_cost: adminCost,
        misc_cost: miscCost, 
        currency: currency.id
      },
      setLoading,
      resetData,
      handleSubmit,
      refresh
    );
  };

  const resetData = () => {
    setCurrency(null);
    setMiscCost("");
    setAdminCost("");
    setTotalCost("");
    setTaxes("");
    setDropdownReset(!dropdownReset);
  };

  const selectCurrency = (id) => {
    let selected = listCurrencies.find((v) => v.id === parseInt(id));
    setCurrency(selected);
  };

  return (
    <React.Fragment>
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <FormDropdown
          label={t("costsTab.currency")}
          reset={dropdownReset}
          onChange={selectCurrency}
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
        <label>{t("costsTab.misc_cost")}</label>
        <CustomInputText
          type="number"
          value={miscCost}
          onChange={(val) => setMiscCost(parseFloat(val))}
          className="w-100"
          leftStatus
        />
      </div>
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.administrative_cost")}</label>
        <CustomInputText
          type="number"
          value={adminCost}
          onChange={(val) => setAdminCost(parseFloat(val))}
          className="w-100"
          leftStatus
        />
      </div>
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.taxes")}</label>
        <CustomInputText
          type="number"
          value={taxes}
          onChange={(val) => setTaxes(parseFloat(val))}
          className="w-100"
          leftStatus
        />
      </div>
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.total_cost")}</label>
        <CustomInputText
          type="number"
          value={totalCost}
          onChange={(val) => setTotalCost(parseFloat(val))}
          className="w-100"
          leftStatus
        />
      </div>
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <div className="p-d-flex p-jc-center p-mt-3 p-mb-5">
          <div className="btn-5 disable-bg">
            <Button
              label={loading ? t("costsTab.button_loading") : t("costsTab.button_new_acquisition")}
              icon={loading ? "pi pi-spin pi-spinner" : "pi pi-check"}
              disabled={loading || !currency || !miscCost || !adminCost || !totalCost || !taxes}
              onClick={() => {
                handleSubmit();
              }}
            />
          </div>
        </div>
      </div>
    </React.Fragment>
  )
}

export default AcquisitionCostInput;