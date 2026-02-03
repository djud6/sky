import React, { useState, useEffect } from "react";
import axios from "axios";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { useTranslation } from "react-i18next";
import { getAuthHeader } from "../../../helpers/Authorization";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import Table from "../../ShareComponents/Table/Table";
import GeneralBadge from "../../ShareComponents/GeneralBadge";
import HistoryDetails from "./HistoryDetails";

const ChildrenHistory = ({ asset, setForceUpdate }) => {
  const { t } = useTranslation();
  const [dataReady, setDataReady] = useState(false);
  const [children, setChildren] = useState([]);
  const [selectedChild, setSelectedChild] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (!dataReady) {
      setChildren([]);
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Get/Child/History/${asset.VIN}`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((res) => {
          const allChildren = res.data;
          setChildren(allChildren);
          setDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
  }, [dataReady, asset]);

  let tableHeaders = [
    {
      header: t("general.vin"),
      colFilter: { field: "VIN" },
    },
    {
      header: "status",
      colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
    },
  ];

  let tableData = null;

  if (!!children) {
    tableData = children.map((child, index) => {
      const isActive = child.status.toLowerCase() === "active" ? true : false;
      return {
        id: child.VIN_id,
        dataPoint: child,
        cells: [
          child.VIN_id,
          <GeneralBadge
            data={child.status}
            colorTheme={isActive ? "badge-success" : "badge-danger"}
          />,
        ],
      };
    });
  }

  return (
    <div className={`linked-asset-container ${!isMobile ? "p-mt-5" : "p-mt-3"}`}>
      <div className="p-mb-5">
        <div className="section-table">
          {!selectedChild ? (
            <div className="darkTable">
              <Table
                tableHeaders={tableHeaders}
                tableData={tableData}
                dataReady={dataReady}
                globalSearch={false}
                rows={5}
                onSelectionChange={(child) => setSelectedChild(child)}
                hasSelection
              />
            </div>
          ) : (
            <HistoryDetails child={selectedChild} setSelectedChild={setSelectedChild} />
          )}
        </div>
      </div>
    </div>
  );
};

export default ChildrenHistory;
