import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { updateData } from "./FuelCostInput";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import CustomInputText from "../../ShareComponents/CustomInputText";
import "../../../styles/helpers/button5.scss";

export default function LicenseCostInput({ vin, refresh }) {
  const { t } = useTranslation();
  const { listCurrencies } = useSelector((state) => state.apiCallData);
  const [loading, setLoading] = useState(false);
  const [licenseRegistration, setLicenseRegistration] = useState("");
  const [licensePlateRenewal, setLicensePlateRenewal] = useState("");
  const [licenseTaxes, setLicenseTaxes] = useState("");
  const [licenseTotalCost, setLicenseTotalCost] = useState("");
  const [licenseCurrency, setLicenseCurrency] = useState(null);
  const [licenseError, setLicenseError] = useState(true);
  const [dropdownReset, setDropdownReset] = useState(false);

  const handleLicenseSubmit = () => {
    if (
      !licenseCurrency ||
      !licensePlateRenewal ||
      !licenseRegistration ||
      !licenseTaxes ||
      !licenseTotalCost
    ) {
      setLicenseError(true);
    } else {
      updateData(
        "/api/v1/License/Add/Cost",
        {
          VIN: vin,
          license_registration: licenseRegistration,
          taxes: licenseTaxes,
          license_plate_renewal: licensePlateRenewal,
          total_cost: licenseTotalCost,
          currency: licenseCurrency.id,
        },
        setLoading,
        licenseReset,
        handleLicenseSubmit,
        refresh
      );
    }
  };

  const licenseReset = () => {
    setLicenseCurrency(null);
    setLicensePlateRenewal("");
    setLicenseRegistration("");
    setLicenseTaxes("");
    setLicenseTotalCost("");
    setLicenseError(true);
    setDropdownReset(!dropdownReset);
  };

  useEffect(() => {
    if (
      licenseCurrency &&
      licenseRegistration &&
      licensePlateRenewal &&
      licenseTotalCost &&
      licenseTaxes
    ) {
      setLicenseError(false);
    } else {
      setLicenseError(true);
    }
  }, [licenseCurrency, licenseRegistration, licensePlateRenewal, licenseTotalCost, licenseTaxes]);

  const selectLicenseCurrency = (id) => {
    let selected = listCurrencies.find((v) => v.id === parseInt(id));
    setLicenseCurrency(selected);
  };

  return (
    <React.Fragment>
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <FormDropdown
          label={t("costsTab.currency")}
          reset={dropdownReset}
          onChange={selectLicenseCurrency}
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
        <label>{t("costsTab.license_reg_cost")}</label>
        <CustomInputText
          type="number"
          placeholder={t("costsTab.license_reg_cost")}
          value={licenseRegistration}
          onChange={(val) => setLicenseRegistration(parseFloat(val))}
          leftStatus
        />
      </div>

      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.license_plate_cost")}</label>
        <CustomInputText
          type="number"
          placeholder={t("costsTab.license_plate_cost")}
          value={licensePlateRenewal}
          onChange={(val) => setLicensePlateRenewal(parseFloat(val))}
          leftStatus
        />
      </div>

      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.total_cost")}</label>
        <CustomInputText
          type="number"
          placeholder={t("costsTab.total_cost")}
          value={licenseTotalCost}
          onChange={(val) => setLicenseTotalCost(parseFloat(val))}
          leftStatus
        />
      </div>

      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.taxes")}</label>
        <CustomInputText
          type="number"
          placeholder={t("costsTab.taxes")}
          value={licenseTaxes}
          onChange={(val) => setLicenseTaxes(parseFloat(val))}
          leftStatus
        />
      </div>

      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <div className="p-d-flex p-jc-center p-mt-3 p-mb-5">
          <div className="btn-5 disable-bg">
            <Button
              label={loading ? t("costsTab.button_loading") : t("costsTab.button_new_license")}
              icon={loading ? "pi pi-spin pi-spinner" : "pi pi-check"}
              disabled={loading || licenseError}
              onClick={() => {
                handleLicenseSubmit();
              }}
            />
          </div>
        </div>
      </div>
    </React.Fragment>
  );
}
