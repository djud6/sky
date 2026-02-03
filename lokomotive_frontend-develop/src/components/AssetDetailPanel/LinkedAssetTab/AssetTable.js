import React, { useEffect } from "react";
import { useTranslation } from "react-i18next";
import * as Constants from "../../../constants";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import Table from "../../ShareComponents/Table/Table";
import VINSearch from "../../ShareComponents/helpers/VINSearch";

const AssetTable = ({ selectedAssets, setSelectedAssets, relation }) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (relation) {
      if (relation === t("motherChildAsset.parent") && selectedAssets.length > 1) {
        setSelectedAssets([selectedAssets[selectedAssets.length - 1]]);
      }
    }
    // eslint-disable-next-line
  }, [relation]);

  let tableHeaders = [
    t("general.vin"),
    t("general.asset_type"),
    t("general.business_unit"),
    t("general.status"),
    t("general.location"),
  ];

  let tableData = selectedAssets.map((asset) => {
    return {
      id: asset.VIN,
      dataPoint: asset,
      cells: [
        <div key={asset.VIN} className="p-d-flex p-ai-center">
          <Button
            icon="pi pi-times-circle"
            className="p-button-rounded p-button-danger p-button-text p-mr-2"
            onClick={() => {
              let filtered = selectedAssets.filter((item) => item.VIN !== asset.VIN);
              setSelectedAssets(filtered);
            }}
          />
          <div className="text-break">{asset.VIN}</div>
        </div>,
        asset.asset_type,
        asset.businessUnit,
        asset.status,
        asset.current_location,
      ],
    };
  });

  return (
    <React.Fragment>
      <div className="input-container">
        <VINSearch
          labelText={t("maintenanceSchedulePanel.add_new_asset")}
          onVehicleSelected={(v) => {
            if (!Array.isArray(v) && v != null) {
              if (!selectedAssets.some((el) => el.VIN === v.VIN)) {
                if (!relation) setSelectedAssets([...selectedAssets, v]);
                else if (relation === t("motherChildAsset.child"))
                  setSelectedAssets([...selectedAssets, v]);
                else if (relation === t("motherChildAsset.parent")) setSelectedAssets([v]);
              }
            }
          }}
          key={JSON.stringify(selectedAssets)}
        />
      </div>
      {selectedAssets.length > 0 && (
        <div className={`p-mx-3 darkTable ${isMobile ? "p-mt-5" : ""}`}>
          <Table
            dataReady
            tableHeaders={tableHeaders}
            tableData={tableData}
            rows={isMobile ? 2 : 3}
            globalSearch={false}
          />
        </div>
      )}
    </React.Fragment>
  );
};

export default AssetTable;
