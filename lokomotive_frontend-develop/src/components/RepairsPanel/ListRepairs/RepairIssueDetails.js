import React, { useState, useEffect } from "react";
import axios from "axios";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import ShowMore from "../../ShareComponents/ShowMore";
import { useTranslation } from "react-i18next";
import IssueTypeBadge from "../../ShareComponents/helpers/IssueTypeBadge";
import { Table } from "../../ShareComponents/Table";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/ShareComponents/Table/table.scss";

const RepairIssueDetails = ({ repair_id }) => {
  const { t } = useTranslation();
  const [issueList, setIssueList] = useState([]);
  const [issuesDataReady, setIssuesDataReady] = useState(false);

  useEffect(() => {
    setIssueList([]);
    setIssuesDataReady(false);
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Issues/Get/Repair/ID/${repair_id}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        setIssueList(response.data);
        setIssuesDataReady(true);
      })
      .catch((error) => {
        setIssuesDataReady(true);
        ConsoleHelper(error);
      });
    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [repair_id]);

  //Preparing table data
  let repairIssueTableHeaders = [
    { header: t("general.id"), colFilter: { field: "custom_id" } },
    { header: t("general.issue_title"), colFilter: { field: "issue_title" } },
    {
      header: t("general.issue_type"),
      colFilter: { field: "issue_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.issue_result"),
      colFilter: { field: "issue_result", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.created_by"),
      colFilter: { field: "created_by", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.modified_by"),
      colFilter: { field: "modified_by", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.issue_details"),
      colFilter: { field: "issue_details" },
    },
  ];

  let repairIssueTableData = issueList.map((issue) => {
    return {
      id: issue.id,
      dataPoint: issue,
      cells: [
        issue.custom_id,
        issue.issue_title,
        <IssueTypeBadge issueType={issue.issue_type} />,
        issue.issue_result,
        issue.created_by,
        issue.modified_by,
        <ShowMore text={issue.issue_details} />,
      ],
    };
  });

  return (
    <div className="p-p-3">
      <h4 className="text-uppercase text-white">{t("repairIssueDetails.repair_issue_details")}</h4>
      <div className="darkTable">
        <Table 
          dataReady={issuesDataReady}
          tableHeaders={repairIssueTableHeaders} 
          tableData={repairIssueTableData} 
        />
      </div>
    </div>
  );
};

export default RepairIssueDetails;
