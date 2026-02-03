import React, { useState, useEffect } from "react";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { Table } from "../../ShareComponents/Table";
import AssetOrderDetails from "./AssetOrderDetails";
import { capitalize } from "../../../helpers/helperFunctions";

const CommonAssetOrdersPanel = ({
  assetOrders,
  selectedAssetOrder,
  setSelectedAssetOrder,
  dataReady,
  setRequests,
  requestType,
  tab,
  setDataReady,
}) => {
  const { t } = useTranslation();
  const [mobileDetails, setMobileDetails] = useState(false);
  const [forceUpdateTable, setForceUpdateTable] = useState(Date.now);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (selectedAssetOrder) {
      setMobileDetails(true);
    }
  }, [selectedAssetOrder]);

  useEffect(() => {
    setSelectedAssetOrder(null);
    setForceUpdateTable(Date.now);
  }, [setSelectedAssetOrder]);

  if (!assetOrders) return null;

  let TableHeaders = [
    { header: t("general.id"), colFilter: { field: "custom_id" } },
    {
      header: t("general.asset_type"),
      colFilter: { field: "asset_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("assetOrderDetails.equipment_type_label"),
      colFilter: { field: "model_number", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.business_unit"),
      colFilter: { field: "business_unit", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.status"),
      colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.vendor"),
      colFilter: { field: "vendor_name", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("assetOrderDetails.date_required_label"),
      colFilter: {
        field: "date_required",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
  ];

  let TableData = assetOrders.map((assetOrder) => {
    assetOrder.vendor_name = assetOrder.vendor_name
      ? assetOrder.vendor_name
      : t("general.not_applicable");

    return {
      id: assetOrder.id,
      dataPoint: assetOrder,
      cells: [
        assetOrder.custom_id,
        assetOrder.asset_type,
        assetOrder.model_number,
        assetOrder.business_unit,
        capitalize(assetOrder.status),
        assetOrder.vendor_name,
        moment(assetOrder.date_required).format("YYYY-MM-DD"),
      ],
    };
  });

  return (
    <React.Fragment>
      {isMobile ? (
        <div className="p-mb-5">
          {selectedAssetOrder && mobileDetails ? (
            <AssetOrderDetails
              order={selectedAssetOrder}
              setSelectedOrder={setSelectedAssetOrder}
              setMobileDetails={setMobileDetails}
              setRequests={setRequests}
              requestType={requestType}
              setDataReady={setDataReady}
            />
          ) : (
            <Table
              key={forceUpdateTable}
              dataReady={dataReady}
              tableHeaders={TableHeaders}
              tableData={TableData}
              onSelectionChange={(assetOrder) => setSelectedAssetOrder(assetOrder)}
              hasSelection
              tab={tab}
            />
          )}
        </div>
      ) : (
        <React.Fragment>
          <Table
            key={forceUpdateTable}
            dataReady={dataReady}
            tableHeaders={TableHeaders}
            tableData={TableData}
            onSelectionChange={(assetOrder) => setSelectedAssetOrder(assetOrder)}
            hasSelection
            tab={tab}
          />
          {selectedAssetOrder && (
            <AssetOrderDetails
              order={selectedAssetOrder}
              setSelectedOrder={setSelectedAssetOrder}
              setMobileDetails={setMobileDetails}
              setRequests={setRequests}
              requestType={requestType}
              setDataReady={setDataReady}
            />
          )}
        </React.Fragment>
      )}
    </React.Fragment>
  );
};

export default CommonAssetOrdersPanel;
