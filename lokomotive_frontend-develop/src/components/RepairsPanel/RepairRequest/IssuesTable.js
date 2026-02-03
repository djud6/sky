import React from "react";
import * as Constants from "../../../constants";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import ShowMore from "../../ShareComponents/ShowMore";
import Table from "../../ShareComponents/Table/Table";
import GeneralBadge from "../../ShareComponents/GeneralBadge";
import IssueTypeBadge from "../../ShareComponents/helpers/IssueTypeBadge";

const IssuesTable = ({
  forceUpdateTable,
  issues,
  vehicle,
  dataReady,
  getSelectedRowsFromTable,
}) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const IssueTypeItemTemplate = (value) => {
    return <IssueTypeBadge issueType={value} />;
  };

  //Preparing table data
  let TableHeaders = [
    {
      header: t("general.location"),
      colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.issue_type"),
      colFilter: {
        field: "issue_type",
        filterOptions: {
          filterAs: "dropdown",
          valueTemplate: IssueTypeItemTemplate,
          itemTemplate: IssueTypeItemTemplate,
        },
      },
    },
    {
      header: t("general.issue_title"),
      colFilter: { field: "issue_title" },
    },
    {
      header: t("repairRequestPanel.accident_id"),
      colFilter: { field: "accident_id" },
    },
    {
      header: t("repairRequestPanel.accident_reported"),
      colFilter: { field: "incident_reported", filterOptions: { filterAs: "dropdown" } },
    },
  ];

  let TableData = issues.map((issue) => {
    return {
      id: issue.issue_id,
      dataPoint: issue,
      cells: [
        issue.current_location,
        <IssueTypeBadge issueType={issue.issue_type} />,
        <ShowMore text={issue.issue_title} />,
        issue.accident_id || t("general.not_applicable"),
        <GeneralBadge data={issue.incident_reported} />,
      ],
    };
  });

  return (
    <React.Fragment>
      <div className="repair-request-table">
        <p className="text-left p-mt-5 p-mb-3 p-ml-2">
          {t("repairRequestPanel.submit_repair_request_for_label", {
            vehicle_vin: vehicle.VIN,
          })}
        </p>
        <div className={`darkTable ${isMobile ? "p-mt-3" : ""}`}>
          <Table
            key={forceUpdateTable}
            dataReady={dataReady}
            tableHeaders={TableHeaders}
            tableData={TableData}
            hasSelection
            multipleSelection
            onSelectionChange={(dataFromTable) => getSelectedRowsFromTable(dataFromTable)}
            rows={isMobile ? 2 : 7}
            disableMobileDetail
            globalSearch={false}
          />
        </div>
      </div>
    </React.Fragment>
  );
};

export default IssuesTable;
