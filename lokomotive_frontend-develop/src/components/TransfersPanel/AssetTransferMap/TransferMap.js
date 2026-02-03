import React, { useState, useEffect } from "react";
import RoutesMapCard from "./RoutesMapCard";
import { SelectButton } from "primereact/selectbutton";
import { useTranslation } from "react-i18next";
import legendImgLg from "../../../images/exceptra/map_legend_lg.png";
import legendImgSm from "../../../images/exceptra/map_legend_sm.png";
import "../../../styles/TransferPanel/AssetTransferMap/assetTransferMap.scss";

const TransferMap = ({ originLocs, destinationLocs }) => {
  const { t } = useTranslation();
  let [originLocations, setOriginLocations] = useState(originLocs.awaitingTransfer);
  let [destinationLocations, setDestinationLocations] = useState(destinationLocs.awaitingTransfer);
  let [selectedTransfer, setSelectedTransfer] = useState(t("assetTransferMap.awaiting_approval"));
  const options = [
    t("assetTransferMap.awaiting_approval"),
    t("assetTransferMap.awaiting_transfer"),
    t("assetTransferMap.in_transit"),
  ];

  useEffect(() => {
    if (selectedTransfer === t("assetTransferMap.awaiting_approval")) {
      setOriginLocations(originLocs.awaitingApproval);
      setDestinationLocations(destinationLocs.awaitingApproval);
    } else if (selectedTransfer === t("assetTransferMap.awaiting_transfer")) {
      setOriginLocations(originLocs.awaitingTransfer);
      setDestinationLocations(destinationLocs.awaitingTransfer);
    } else {
      setOriginLocations(originLocs.inTransit);
      setDestinationLocations(destinationLocs.inTransit);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTransfer]);

  return (
    <div>
      <div className="w-100 p-mb-3 p-d-flex p-jc-end transfer-map-header">
        <SelectButton
          value={selectedTransfer}
          options={options}
          onChange={(e) => setSelectedTransfer(e.value)}
        />
      </div>
      <div className="p-px-5 transfer-map-card">
        {originLocations.length !== 0 && destinationLocations.length !== 0 ? (
          <RoutesMapCard
            transferType={selectedTransfer}
            originLocations={originLocations}
            destinationLocations={destinationLocations}
          />
        ) : (
          <div
            className="p-d-flex p-jc-center p-ai-center bg-transparent"
            style={{
              backgroundImage: `url(${require("../../../images/background/map.jpg")})`,
              width: "100%",
              height: "600px",
            }}
          >
            <div className="p-d-flex p-flex-column p-jc-center p-ai-center">
              <i className="pi pi-map-marker text-white" style={{ fontSize: "3em" }} />
              <h3 className="p-mt-3 text-white">
                {t("assetTransferMap.no_data", { progress: selectedTransfer })}
              </h3>
            </div>
          </div>
        )}
        <div className="p-d-flex p-jc-center p-flex-wrap p-mt-4">
          <div className="p-d-flex p-jc-center p-ai-center p-mx-1 p-my-2">
            <img src={legendImgLg} alt="legendImage-large" />
            <div className="p-mx-2 text-white">{t("assetTransferMap.legend_large_text")}</div>
          </div>
          <div className="p-d-flex p-jc-center p-ai-center p-mx-1 p-my-2">
            <img src={legendImgSm} alt="legendImage-small" />
            <div className="p-mx-2 text-white">{t("assetTransferMap.legend_small_text")}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TransferMap;
