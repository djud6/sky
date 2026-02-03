import React from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import CardWidget from "../../ShareComponents/CardWidget";
import VendorOption from "./VendorOption";
import "../../../styles/helpers/textfield2.scss";

const Recipient = ({
  method,
  email,
  setEmail,
  approvedVendor,
  setApprovedVendor,
  multiSelectedVendor,
  setMultiSelectedVendor,
  isVendorSelected,
  setIsVendorSelected,
}) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  return (
    <React.Fragment>
      <div
        className={`recipient-container ${
          !isMobile ? "p-sm-12 p-md-12 p-lg-6 p-xl-6" : "w-100 p-m-3"
        }`}
      >
        <h5 className="p-mb-3">{t("removalPanel.last_step_title", { method: method })}</h5>
        <div className="w-100 recipient-content">
          <CardWidget blueBg status={isVendorSelected}>
            <VendorOption
              method={method}
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
      {!isMobile && <div className="p-sm-12 p-md-12 p-lg-6 p-xl-6">{""}</div>}
    </React.Fragment>
  );
};

export default Recipient;
