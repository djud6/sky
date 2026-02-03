import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { Table } from "../../ShareComponents/Table";
import VINLink from "../../ShareComponents/helpers/VINLink";
import IssueTypeBadge from "../../ShareComponents/helpers/IssueTypeBadge";
import IssueDetails from "./IssueDetails";

const CommonIssuesPanel = ({
  issues,
  setIssues,
  selectedIssue,
  setSelectedIssue,
  dataReady,
  setShowChart,
  issuePanel,
  tab,
}) => {
  const { t } = useTranslation();
  const [mobileDetails, setMobileDetails] = useState(false);
  const [forceUpdateTable, setForceUpdateTable] = useState(Date.now);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (setShowChart) {
      isMobile ? setShowChart(!mobileDetails) : setShowChart(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mobileDetails, isMobile]);

  useEffect(() => {
    if (selectedIssue) {
      setMobileDetails(true);
    }
  }, [selectedIssue]);

  useEffect(() => {
    setSelectedIssue(null);
    setForceUpdateTable(Date.now);
  }, [setSelectedIssue]);

  if (!issues) return null;

  let issueTableHeaders = [
    { header: t("general.id"), colFilter: { field: "custom_id" } },
    { header: t("general.vin"), colFilter: { field: "VIN" } },
    {
      header: t("general.asset_type"),
      colFilter: { field: "asset_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.location"),
      colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.issue_type"),
      colFilter: { field: "issue_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.issue_title"),
      colFilter: { field: "issue_title" },
    },
    {
      header: t("issueDetails.linked_repair"),
      colFilter: { field: "repair_work_order" },
    },
  ];

  let issueTableData = issues.map((issue) => {
    return {
      id: issue.issue_id,
      dataPoint: issue,
      cells: [
        issue.custom_id,
        <VINLink vin={issue.VIN} />,
        issue.asset_type,
        issue.current_location,
        <IssueTypeBadge issueType={issue.issue_type} />,
        issue.issue_title,
        issue.repair_work_order,
      ],
    };
  });

  return (
    <React.Fragment>
      {isMobile ? (
        <React.Fragment>
          {selectedIssue && mobileDetails ? (
            <IssueDetails
              issue={selectedIssue}
              setSelectedIssue={setSelectedIssue}
              setMobileDetails={setMobileDetails}
              setIssues={setIssues}
              issuePanel={issuePanel}
            />
          ) : (
            <div className="p-mb-5">
              <Table
                key={forceUpdateTable}
                dataReady={dataReady}
                tableHeaders={issueTableHeaders}
                tableData={issueTableData}
                onSelectionChange={(issue) => setSelectedIssue(issue)}
                hasSelection
                tab={tab}
              />
            </div>
          )}
        </React.Fragment>
      ) : (
        <React.Fragment>
          <Table
            key={forceUpdateTable}
            dataReady={dataReady}
            tableHeaders={issueTableHeaders}
            tableData={issueTableData}
            onSelectionChange={(issue) => setSelectedIssue(issue)}
            hasSelection
            tab={tab}
          />
          {selectedIssue && (
            <IssueDetails
              issue={selectedIssue}
              setSelectedIssue={setSelectedIssue}
              setMobileDetails={setMobileDetails}
              setIssues={setIssues}
              issuePanel={issuePanel}
            />
          )}
        </React.Fragment>
      )}
    </React.Fragment>
  );
};

export default CommonIssuesPanel;
