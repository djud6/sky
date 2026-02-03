import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../constants";
import { Table } from "../ShareComponents/Table";
import VINLink from "../ShareComponents/helpers/VINLink";
import ApprovalStatusBadge from "./ApprovalStatusBadge";
import ApprovalDetails from "./ApprovalDetails";

const CommonApprovalPanel = ({
  requests,
  selectedRequest,
  setSelectedRequest,
  dataReady,
  setDataReady,
  approvable,
}) => {
  const { t } = useTranslation();
  const [mobileDetails, setMobileDetails] = useState(false);
  const [forceUpdateTable, setForceUpdateTable] = useState(Date.now);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (selectedRequest) {
      setMobileDetails(true);
    }
  }, [selectedRequest]);

  useEffect(() => {
    setSelectedRequest(null);
    setForceUpdateTable(Date.now);
  }, [setSelectedRequest]);

  if (!requests) return null;

  let TableHeaders = [
    {
      header: t("general.vin"),
      colFilter: { field: "VIN" },
    },
    {
      header: t("general.title"),
      colFilter: { field: "title" },
    },
    {
      header: t("approvalDetails.request_type"),
      colFilter: { field: "request_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.asset_type"),
      colFilter: { field: "asset_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.location"),
      colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.approval_status"),
      colFilter: { field: "is_approved", filterOptions: { filterAs: "dropdown" } },
    },
  ];

  const decideRequestType = (request) => {
    let requestType = t("general.not_applicable");

    if (request.maintenance_request) {
      requestType = t("approvalPanel.maintenance_request_type");
    } else if (request.repair_request) {
      requestType = t("approvalPanel.repair_request_type");
    } else if (request.asset_transfer_request) {
      requestType = t("approvalPanel.asset_transfer_request_type");
    } else if (request.asset_request) {
      requestType = t("approvalPanel.asset_request_type");
    } else if (request.disposal_request) {
      requestType = t("approvalPanel.disposal_request_type");
    }

    return requestType;
  };

  let TableData = requests.map((request) => {
    request["request_type"] = decideRequestType(request);
    return {
      id: request.approval_id,
      dataPoint: request,
      cells: [
        //TODO need to adjust cell based on api response
        request.VIN ? <VINLink vin={request.VIN} /> : t("general.not_applicable"),
        request.title || t("general.not_applicable"),
        request.request_type || t("general.not_applicable"),
        request.asset_type || t("general.not_applicable"),
        request.current_location || t("general.not_applicable"),
        <ApprovalStatusBadge isApproved={request.is_approved} />,
      ],
    };
  });

  return (
    <React.Fragment>
      {isMobile ? (
        <React.Fragment>
          {selectedRequest && mobileDetails ? (
            <div className="p-mb-5">
              <ApprovalDetails
                selectedRequest={selectedRequest}
                setSelectedRequest={setSelectedRequest}
                setDataReady={setDataReady}
                withApproval={approvable}
                setMobileDetails={setMobileDetails}
              />
            </div>
          ) : (
            <div className="p-mb-5">
              <Table
                key={forceUpdateTable}
                dataReady={dataReady}
                tableHeaders={TableHeaders}
                tableData={TableData}
                onSelectionChange={(request) => setSelectedRequest(request)}
                hasSelection
                timeOrder={false}
              />
            </div>
          )}
        </React.Fragment>
      ) : (
        <React.Fragment>
          <Table
            key={forceUpdateTable}
            dataReady={dataReady}
            tableHeaders={TableHeaders}
            tableData={TableData}
            onSelectionChange={(request) => setSelectedRequest(request)}
            hasSelection
            timeOrder={false}
          />
          {selectedRequest && !Array.isArray(selectedRequest) && (
            <ApprovalDetails
              selectedRequest={selectedRequest}
              setSelectedRequest={setSelectedRequest}
              setDataReady={setDataReady}
              withApproval={approvable}
            />
          )}
        </React.Fragment>
      )}
    </React.Fragment>
  );
};

export default CommonApprovalPanel;
