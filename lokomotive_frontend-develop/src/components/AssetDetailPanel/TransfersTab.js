import React, { useEffect, useState } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../constants";
import { getAuthHeader } from "../../helpers/Authorization";
import Table from "../ShareComponents/Table/Table";
import TransferDetails from "../TransfersPanel/TransferDetails";
import ConsoleHelper from "../../helpers/ConsoleHelper";

const TransfersTab = ({ vin, mobileDetails, setMobileDetails }) => {
  const { t } = useTranslation();
  const [transfers, setTransfers] = useState([]);
  const [dataReady, setDataReady] = useState(false);
  const [selectedTransfer, setSelectedTransfer] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Transfer/List`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        const temp_list = response.data.filter(
          (transfer) => transfer.VIN.toLowerCase() === vin.toLowerCase()
        );
        setTransfers(temp_list);
        setDataReady(true);
      })
      .catch((error) => {
        ConsoleHelper(error);
      });
    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [vin]);

  useEffect(() => {
    if (selectedTransfer && isMobile) setMobileDetails(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTransfer]);

  let tableHeaders = [
    {
      header: t("general.id"),
      colFilter: { field: "custom_id" },
    },
    {
      header: t("transfersSection.current_location"),
      colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("transfersSection.transfer_location"),
      colFilter: { field: "destination_location", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.created_by"),
      colFilter: { field: "created_by", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.status"),
      colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
    },
  ];

  let tableData = null;

  if (!!transfers) {
    tableData = transfers.map((transfer) => {
      return {
        id: transfer.asset_transfer_id,
        dataPoint: transfer,
        cells: [
          transfer.custom_id,
          transfer.current_location,
          transfer.destination_location,
          transfer.created_by,
          transfer.status,
        ],
      };
    });
  }

  return (
    <div className={`${!isMobile ? "p-mt-5" : "p-mt-3"}`}>
      {isMobile ? (
        <React.Fragment>
          {selectedTransfer && mobileDetails ? (
            <TransferDetails
              transfer={selectedTransfer}
              setSelectedTransfer={setSelectedTransfer}
              setMobileDetails={setMobileDetails}
            />
          ) : (
            <div className="p-mb-5">
              <h5 className="p-mb-3">
                {t("transfersSection.transfer_history")} for {vin}
              </h5>
              <div className="darkTable section-table">
                <Table
                  tableHeaders={tableHeaders}
                  tableData={tableData}
                  dataReady={dataReady}
                  onSelectionChange={(transfer) => setSelectedTransfer(transfer)}
                  hasSelection
                  rows={5}
                />
              </div>
            </div>
          )}
        </React.Fragment>
      ) : (
        <React.Fragment>
          <h5 className="p-mb-3">{t("transfersSection.transfer_history")}</h5>
          <div className="darkTable section-table">
            <Table
              tableHeaders={tableHeaders}
              tableData={tableData}
              dataReady={dataReady}
              onSelectionChange={(transfer) => setSelectedTransfer(transfer)}
              hasSelection
              rows={5}
            />
          </div>
          {selectedTransfer && (
            <TransferDetails
              transfer={selectedTransfer}
              setSelectedTransfer={setSelectedTransfer}
            />
          )}
        </React.Fragment>
      )}
    </div>
  );
};

export default TransfersTab;
