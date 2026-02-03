import React, { useEffect, useState } from "react";
import axios from "axios";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { getAuthHeader } from "../../helpers/Authorization";
import * as Constants from "../../constants";
import { capitalize } from "../../helpers/helperFunctions";
import Table from "../ShareComponents/Table/Table";
import MaintenanceDetails from "../MaintenancePanel/MaintenanceStatus/MaintenanceDetails";
import MaintenanceDetailsMore from "../MaintenancePanel/MaintenanceStatus/MaintenanceDetailsMore";
import ConsoleHelper from "../../helpers/ConsoleHelper";

const MaintenanceTab = ({ vin, mobileDetails, setMobileDetails }) => {
  const { t } = useTranslation();
  const [maintenances, setMaintenances] = useState([]);
  const [dataReady, setDataReady] = useState(false);
  const [moreDetails, setMoreDetails] = useState(false);
  const [selectedMaintenance, setSelectedMaintenance] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (!dataReady) {
      const cancelTokenSource = axios.CancelToken.source();
      setSelectedMaintenance(null);
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/VIN/${vin}`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          const maintenance = response.data;
          for (var i in maintenance) {
            if (maintenance[i].in_house) {
              maintenance[i].vendor_name = "In-house Maintenance";
            } else if (!maintenance[i].in_house && !maintenance[i].vendor_name) {
              maintenance[i].vendor_name = maintenance[i].vendor_email;
            }
          }
          setMaintenances(maintenance);
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
  }, [vin, dataReady]);

  useEffect(() => {
    if (selectedMaintenance && isMobile) setMobileDetails(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedMaintenance]);

  let tableHeaders = [
    {
      header: t("general.id"),
      colFilter: { field: "work_order" },
    },
    {
      header: t("general.inspection_type"),
      colFilter: { field: "inspection_type", filterOptions: { filterAs: "dropdown" } },
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
        field: "date_updated",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
    {
      header: t("assetDetailPanel.assigned_vendor"),
      colFilter: { field: "vendor_name", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.status"),
      colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
    },
  ];

  let tableData = null;

  if (!!maintenances) {
    tableData = maintenances.map((maintenance) => {
      return {
        id: maintenance.maintenance_id,
        dataPoint: maintenance,
        cells: [
          maintenance.work_order,
          maintenance.inspection_type,
          moment(maintenance.date_created).format("YYYY-MM-DD"),
          moment(maintenance.date_updated).format("YYYY-MM-DD"),
          maintenance.vendor_name,
          capitalize(maintenance.status),
        ],
      };
    });
  }

  return (
    <div className={`${!isMobile ? "p-mt-5" : "p-mt-3"}`}>
      {isMobile ? (
        <React.Fragment>
          {selectedMaintenance && mobileDetails ? (
            <MaintenanceDetails
              maintenance={selectedMaintenance}
              setSelectedMaintenance={setSelectedMaintenance}
              setDataReady={setDataReady}
              setMobileDetails={setMobileDetails}
              disableButtons
            />
          ) : (
            <div className="p-mb-5">
              <h5 className="p-mb-3">
                {t("assetDetailPanel.maintenance_history")} for {vin}
              </h5>
              <div className="darkTable section-table">
                <Table
                  tableHeaders={tableHeaders}
                  tableData={tableData}
                  dataReady={dataReady}
                  onSelectionChange={(item) => setSelectedMaintenance(item)}
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
              <MaintenanceDetailsMore
                maintenance={selectedMaintenance}
                setMoreDetails={setMoreDetails}
                setDataReady={setDataReady}
              />
            </div>
          ) : (
            <React.Fragment>
              <React.Fragment>
                <h5 className="p-mb-3">{t("assetDetailPanel.maintenance_history")}</h5>
                <div className="darkTable section-table">
                  <Table
                    tableHeaders={tableHeaders}
                    tableData={tableData}
                    dataReady={dataReady}
                    onSelectionChange={(item) => setSelectedMaintenance(item)}
                    hasSelection
                    rows={5}
                  />
                </div>
              </React.Fragment>
              {selectedMaintenance && (
                <MaintenanceDetails
                  maintenance={selectedMaintenance}
                  setSelectedMaintenance={setSelectedMaintenance}
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

export default MaintenanceTab;
