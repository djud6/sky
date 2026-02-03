import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { capitalize } from "../../../helpers/helperFunctions";
import { Table } from "../../ShareComponents/Table";
import TransferDetails from "./TransferDetails";
import VINLink from "../../ShareComponents/helpers/VINLink";

const CommonTransferPanel = ({
  transfers,
  setTransfers,
  selectedTransfer,
  setSelectedTransfer,
  dataReady,
  tab,
}) => {
  const { t } = useTranslation();
  const [forceUpdateTable, setForceUpdateTable] = useState(Date.now);
  const [mobileDetails, setMobileDetails] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (selectedTransfer) {
      setMobileDetails(true);
    }
  }, [selectedTransfer]);

  useEffect(() => {
    setSelectedTransfer(null);
    setForceUpdateTable(Date.now);
  }, [setSelectedTransfer]);

  if (!transfers) return null;

  let tableHeaders = [
    { header: t("general.id"), colFilter: { field: "custom_id" } },
    { header: t("general.vin"), colFilter: { field: "VIN" } },
    {
      header: t("general.business_unit"),
      colFilter: { field: "business_unit", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.current_location"),
      colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.destination_location"),
      colFilter: { field: "destination_location", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.status"),
      colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
    },
  ];

  let tableData = transfers.map((transfer) => {
    return {
      id: transfer.asset_transfer_id,
      dataPoint: transfer,
      cells: [
        transfer.custom_id,
        <VINLink vin={transfer.VIN} />,
        transfer.business_unit,
        transfer.current_location,
        transfer.destination_location,
        capitalize(transfer.status),
      ],
    };
  });

  return (
    <React.Fragment>
      {isMobile ? (
        <React.Fragment>
          {selectedTransfer && mobileDetails ? (
            <TransferDetails
              transfer={selectedTransfer}
              setTransfers={setTransfers}
              setSelectedTransfer={setSelectedTransfer}
              setMobileDetails={setMobileDetails}
            />
          ) : (
            <Table
              key={forceUpdateTable}
              dataReady={dataReady}
              tableHeaders={tableHeaders}
              tableData={tableData}
              onSelectionChange={(transfer) => setSelectedTransfer(transfer)}
              hasSelection
              tab={tab}
            />
          )}
        </React.Fragment>
      ) : (
        <React.Fragment>
          <Table
            key={forceUpdateTable}
            dataReady={dataReady}
            tableHeaders={tableHeaders}
            tableData={tableData}
            onSelectionChange={(transfer) => setSelectedTransfer(transfer)}
            hasSelection
            tab={tab}
          />
          {selectedTransfer && (
            <TransferDetails
              transfer={selectedTransfer}
              setTransfers={setTransfers}
              setSelectedTransfer={setSelectedTransfer}
              setMobileDetails={setMobileDetails}
            />
          )}
        </React.Fragment>
      )}
    </React.Fragment>
  );
};

export default CommonTransferPanel;
