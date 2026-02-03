import React, { useEffect, useState } from "react";
import axios from "axios";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { getAuthHeader } from "../../helpers/Authorization";
import * as Constants from "../../constants";
import { capitalize } from "../../helpers/helperFunctions";
import ShowMore from "../ShareComponents/ShowMore";
import Table from "../ShareComponents/Table/Table";
import RepairDetails from "../RepairsPanel/ListRepairs/RepairDetails";
import RepairDetailsMore from "../RepairsPanel/ListRepairs/RepairDetailsMore";
import ConsoleHelper from "../../helpers/ConsoleHelper";

const RepairsTab = ({ vin, mobileDetails, setMobileDetails }) => {
  const { t } = useTranslation();
  const [repairs, setRepairs] = useState([]);
  const [dataReady, setDataReady] = useState(false);
  const [moreDetails, setMoreDetails] = useState(false);
  const [selectedRepair, setSelectedRepair] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (!dataReady) {
      setRepairs([]);
      setSelectedRepair(null);
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Repair/VIN/${vin}`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          setRepairs(response.data);
          setDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
  }, [vin, dataReady]); // @TODO: Please check. Im not sure if this is the right business logic. This effect will only run if the vin changes.

  useEffect(() => {
    if (selectedRepair && isMobile) setMobileDetails(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedRepair]);

  let tableHeaders = [
    {
      header: t("general.id"),
      colFilter: { field: "work_order" },
    },
    {
      header: t("assetDetailPanel.asset_downtime"),
      colFilter: { field: "down_time" },
    },
    {
      header: t("general.description"),
      colFilter: { field: "description" },
    },
    {
      header: t("general.status"),
      colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("assetDetailPanel.date_created"),
      colFilter: {
        field: "date_created",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
    {
      header: t("assetDetailPanel.date_updated"),
      colFilter: {
        field: "date_modified",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
  ];

  let tableData = null;

  if (!!repairs) {
    tableData = repairs.map((repair) => {
      return {
        id: repair.repair_id,
        dataPoint: repair,
        cells: [
          repair.work_order,
          `${repair.down_time} days`,
          <ShowMore text={repair.description} excerpt={20} />,
          capitalize(repair.status),
          moment(repair.date_created).format("YYYY-MM-DD"),
          moment(repair.date_modified).format("YYYY-MM-DD"),
        ],
      };
    });
  }

  return (
    <div className={`${!isMobile ? "p-mt-5" : "p-mt-3"}`}>
      {isMobile ? (
        <React.Fragment>
          {selectedRepair && mobileDetails ? (
            <RepairDetails
              repair={selectedRepair}
              setSelectedRepair={setSelectedRepair}
              setDataReady={setDataReady}
              setMobileDetails={setMobileDetails}
              disableButtons
            />
          ) : (
            <div className="p-mb-5">
              <h5 className="p-mb-3">
                {t("assetDetailPanel.repair_history")} for {vin}
              </h5>
              <div className="darkTable section-table">
                <Table
                  tableHeaders={tableHeaders}
                  tableData={tableData}
                  dataReady={dataReady}
                  onSelectionChange={(repair) => setSelectedRepair(repair)}
                  hasSelection
                  rows={5}
                />
              </div>
            </div>
          )}
        </React.Fragment>
      ) : (
        <React.Fragment>
          {moreDetails ? (
            <div className="view-more-details">
              <RepairDetailsMore
                repair={selectedRepair}
                setMoreDetails={setMoreDetails}
                setDataReady={setDataReady}
              />
            </div>
          ) : (
            <React.Fragment>
              <React.Fragment>
                <h5 className="p-mb-3">{t("assetDetailPanel.repair_history")}</h5>
                <div className="darkTable section-table">
                  <Table
                    tableHeaders={tableHeaders}
                    tableData={tableData}
                    dataReady={dataReady}
                    onSelectionChange={(repair) => setSelectedRepair(repair)}
                    hasSelection
                    rows={5}
                  />
                </div>
              </React.Fragment>
              {selectedRepair && (
                <RepairDetails
                  repair={selectedRepair}
                  setSelectedRepair={setSelectedRepair}
                  setDataReady={setDataReady}
                  setMoreDetails={setMoreDetails}
                  disableButtons
                />
              )}
            </React.Fragment>
          )}
        </React.Fragment>
      )}
    </div>
  );
};

export default RepairsTab;
