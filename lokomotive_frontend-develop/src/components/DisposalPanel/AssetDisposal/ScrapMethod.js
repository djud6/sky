import React from "react";
import { useTranslation } from "react-i18next";
import { RadioButton } from "primereact/radiobutton";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import CardWidget from "../../ShareComponents/CardWidget";
import VendorOption from "./VendorOption";
import "../../../styles/helpers/textfield2.scss";

const ScrapMethod = ({
  email,
  setEmail,
  approvedVendor,
  setApprovedVendor,
  multiSelectedVendor,
  setMultiSelectedVendor,
  isVendorSelected,
  setIsVendorSelected,
  isStripped,
  setIsStripped,
}) => {
  const { t } = useTranslation();
  const generalStatus = [
    { name: t("general.yes"), key: "Y" },
    { name: t("general.no"), key: "N" },
  ];

  return (
    <React.Fragment>
      <div className="scrap-form-container p-sm-12 p-md-12 p-lg-6 p-xl-6">
        <h5 className="p-mb-3">{t("removalPanel.scrap_title")}</h5>
        <div className="scrap-form-content w-100">
          <CardWidget YN status={Object.keys(isStripped).length !== 0} lightBg>
            <label className="h5 font-weight-bold">
              {t("removalPanel.asset_stripped")}
              <Tooltip
                label={"upload-tooltip"}
                description={t("removalPanel.asset_stripped_tooltip")}
              />
            </label>
            <div className="p-d-flex">
              {generalStatus.map((status) => {
                return (
                  <div key={status.key} className="p-d-flex p-ai-center">
                    <RadioButton
                      inputId={status.key}
                      name="stripStatus"
                      value={status}
                      onChange={(e) => setIsStripped(e.value)}
                      checked={isStripped.key === status.key}
                    />
                    <label className="mb-0 ml-2 mr-3" htmlFor={status.key}>
                      {status.name}
                    </label>
                  </div>
                );
              })}
            </div>
          </CardWidget>
          <CardWidget status={isVendorSelected} lightBg>
            <VendorOption
              method={t("removalPanel.scrap")}
              email={email}
              setEmail={setEmail}
              approvedVendor={approvedVendor}
              setApprovedVendor={setApprovedVendor}
              multiSelectedVendor={multiSelectedVendor}
              setMultiSelectedVendor={setMultiSelectedVendor}
              setIsVendorSelected={setIsVendorSelected}
              vendorType="disposal"
            />
          </CardWidget>
        </div>
      </div>
      <div className="p-sm-12 p-md-12 p-lg-6 p-xl-6">{""}</div>
    </React.Fragment>
  );
};

export default ScrapMethod;
