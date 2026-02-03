import React from "react";
import { useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";

const AssetTransferBtn = ({ vin, asset }) => {
  const { t } = useTranslation();
  let history = useHistory();
  const handleAssetTransfer = (e) => {
    e.preventDefault();
    history.push({
      pathname:  `/transfers/asset-transfer/${vin}`,
      state: {
        vehicle: asset[0]
      } 
    });
  };
  return (
    <Button
      label={t("general.transfer_asset")}
      icon="pi pi-chevron-right"
      iconPos="right"
      className="p-button p-button-secondary p-text-uppercase"
      onClick={handleAssetTransfer}
    />
  );
};

export default AssetTransferBtn;
