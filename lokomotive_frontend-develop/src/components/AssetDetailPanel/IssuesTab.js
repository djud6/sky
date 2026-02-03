import React, { useEffect, useState } from "react";
import axios from "axios";
import moment from "moment";
import { useMediaQuery } from "react-responsive";
import { useDispatch } from "react-redux";
import { getAuthHeader } from "../../helpers/Authorization";
import * as Constants from "../../constants";
import Table from "../ShareComponents/Table/Table";
import ShowMore from "../ShareComponents/ShowMore";
import IssueDetails from "../IssuesPanel/UnresolvedIssues/IssueDetails";
import { useTranslation } from "react-i18next";
import IssueTypeBadge from "../ShareComponents/helpers/IssueTypeBadge";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import { UPDATE_ISSUES } from "../../redux/types/issueTypes";
import "../../styles/ShareComponents/Table/table.scss";

const IssuesTab = ({ vin, mobileDetails, setMobileDetails }) => {
  const { t } = useTranslation();
  const [issues, setIssues] = useState([]);
  const [dataReady, setDataReady] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const dispatch = useDispatch();

  useEffect(() => {
    if (!dataReady) {
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Issues/VIN/${vin}`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          const issues = response.data;
          for (var i in issues) {
            issues[i].issue_created = moment(issues[i].issue_created).format("YYYY-MM-DD");
            issues[i].issue_updated = moment(issues[i].issue_updated).format("YYYY-MM-DD");
            if (!issues[i].repair_work_order)
              issues[i].repair_work_order = t("general.not_applicable");
          }
          setIssues(issues);
          dispatch({ type: UPDATE_ISSUES, data: issues });
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vin, dataReady]);

  useEffect(() => {
    if (selectedIssue && isMobile) setMobileDetails(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedIssue]);

  let tableHeaders = [
    { header: t("general.id"), colFilter: { field: "custom_id" } },
    { header: t("general.issue_title"), colFilter: { field: "issue_title" } },
    {
      header: t("general.issue_type"),
      colFilter: { field: "issue_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.created"),
      colFilter: {
        field: "issue_created",
        filterOptions: { filterAs: "date", dateFormat: "YYYY-MM-DD" },
      },
    },
    {
      header: t("assetDetailPanel.last_update"),
      colFilter: {
        field: "issue_updated",
        filterOptions: { filterAs: "date", dateFormat: "YYYY-MM-DD" },
      },
    },
  ];

  let tableData = null;

  if (!!issues) {
    tableData = issues.map((issue) => {
      return {
        id: issue.issue_id,
        dataPoint: issue,
        cells: [
          issue.custom_id,
          <ShowMore text={issue.issue_title} excerpt="10" />,
          <IssueTypeBadge issueType={issue.issue_type} />,
          issue.issue_created,
          issue.issue_updated,
        ],
      };
    });
  }

  return (
    <div className={`${!isMobile ? "p-mt-5" : "p-mt-3"}`}>
      {isMobile ? (
        <React.Fragment>
          {selectedIssue && mobileDetails ? (
            <IssueDetails
              issue={selectedIssue}
              setSelectedIssue={setSelectedIssue}
              setDataReady={setDataReady}
              setMobileDetails={setMobileDetails}
              setIssues={setIssues}
              disableButtons
            />
          ) : (
            <div className="p-mb-5">
              <h5 className="title">
                {t("assetDetailPanel.issue_history")} for {vin}
              </h5>
              <div className="darkTable section-table">
                <Table
                  tableHeaders={tableHeaders}
                  tableData={tableData}
                  dataReady={dataReady}
                  onSelectionChange={(issue) => setSelectedIssue(issue)}
                  hasSelection
                  rows={5}
                />
              </div>
            </div>
          )}
        </React.Fragment>
      ) : (
        <React.Fragment>
          <h5 className="p-mb-3">{t("assetDetailPanel.issue_history")}</h5>
          <div className="darkTable section-table">
            <Table
              tableHeaders={tableHeaders}
              tableData={tableData}
              dataReady={dataReady}
              onSelectionChange={(issue) => setSelectedIssue(issue)}
              hasSelection
              rows={5}
            />
          </div>
          {selectedIssue && (
            <IssueDetails
              issue={selectedIssue}
              setSelectedIssue={setSelectedIssue}
              setDataReady={setDataReady}
              setIssues={setIssues}
              disableButtons
            />
          )}
        </React.Fragment>
      )}
    </div>
  );
};

export default IssuesTab;
