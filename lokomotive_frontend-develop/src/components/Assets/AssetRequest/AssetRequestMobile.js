import React from "react";
import { useTranslation } from "react-i18next";
import { Button } from 'primereact/button';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCartPlus, faArrowRight } from "@fortawesome/free-solid-svg-icons";
import "../../../styles/helpers/button2.scss";
import "../../../styles/Assets/AssetRequestMobile.scss";

const AssetRequestMobile = ({ setMobileForm }) => {
  const { t } = useTranslation();

  return (
    <div className="asset-request-mobile">
      <h3>{t("assetRequestPanel.asset_request")}</h3>
      <div className="btn-2 p-mt-4">
        <Button 
          className="p-d-flex p-jc-center w-100"
          onClick={() => setMobileForm(true)}
        >
          <FontAwesomeIcon icon={faCartPlus} color="#FEFEFE" />
          <span className="p-px-3">{t("assetRequestPanel.panel_header")}</span>
          <FontAwesomeIcon icon={faArrowRight} color="#FEFEFE" />
        </Button>
      </div>
    </div>
  )
}

export default AssetRequestMobile;