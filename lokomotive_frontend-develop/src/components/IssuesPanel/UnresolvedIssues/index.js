import React, { useState, useEffect } from "react";
import axios from "axios";
import * as Constants from "../../../constants";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { useDispatch } from "react-redux";
import { TabView, TabPanel } from "primereact/tabview";
import colorVars from "../../../styles/variables.scss";
import { getAuthHeader } from "../../../helpers/Authorization";
import { faExclamationTriangle } from "@fortawesome/free-solid-svg-icons";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import BreakDownChartCard from "../../ShareComponents/ChartCard/BreakdownChartCard";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import CommonIssuesPanel from "./CommonIssuesPanel";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import { UPDATE_ISSUES } from "../../../redux/types/issueTypes";
import { useHistory } from "react-router-dom";
import { persistSetTab } from "../../../helpers/helperFunctions";
import { persistGetTab } from "../../../helpers/helperFunctions";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";

const UnresolvedIssuesPanel = () => {
  const dispatch = useDispatch();
  const { t } = useTranslation();
  const [issues, setIssues] = useState([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [dataReady, setDataReady] = useState(false);
  const [selectedUnresolvedIssue, setSelectedUnresolvedIssue] = useState(null);
  const [selectedResolvedIssue, setSelectedResolvedIssue] = useState(null);
  const [showChart, setShowChart] = useState(true);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const history = useHistory();

  useEffect(() => {
    persistGetTab(setActiveIndex);
  }, []);

  useEffect(() => {
    if (!dataReady) {
      const cancelTokenSource = axios.CancelToken.source();
      setSelectedUnresolvedIssue(null);
      setSelectedResolvedIssue(null);

      axios
        .post(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Issues/List/Type`,
          {},
          { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
        )
        .then((response) => {
          const issues = response.data;
          for (var i in issues) {
            if (!issues[i].repair_work_order)
              issues[i].repair_work_order = t("general.not_applicable");
          }
          setIssues(issues);
          setDataReady(true);
          dispatch({ type: UPDATE_ISSUES, data: response.data });
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataReady]);

  let resolvedIssues = [];
  let unresolvedIssues = [];
  let resolvedCount;
  let unresolvedCount;
  let issueChartData = null;
  let threeMonthsDate = new Date();
  threeMonthsDate.setMonth(threeMonthsDate.getMonth() - 3);

  if (issues != null && issues.length > 0) {
    unresolvedIssues = issues.filter((issue) => {
      return !issue.is_resolved;
    });
    unresolvedCount = unresolvedIssues.filter(
      (issue) => new Date(threeMonthsDate) < new Date(issue.issue_created)
    ).length;

    resolvedIssues = issues.filter((issue) => {
      return issue.is_resolved;
    });
    resolvedCount = resolvedIssues.filter(
      (issue) => new Date(threeMonthsDate) < new Date(issue.issue_created)
    ).length;

    issueChartData = [
      {
        data: (unresolvedCount / (unresolvedCount + resolvedCount)) * 100,
        label: t("issuesPanelIndex.unresolved_issues").toUpperCase(),
        color: colorVars.orange,
        full: 100,
      },
      {
        data: (resolvedCount / (unresolvedCount + resolvedCount)) * 100,
        label: t("issuesPanelIndex.resolved_issues").toUpperCase(),
        color: colorVars.blue,
        full: 100,
      },
    ];
  }

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["Reports", "Search", "New Issue"]}
          activeTab={"Reports"}
          urls={["/issues", "/issues/search", "/issues/new"]}
        />
      )}
      <PanelHeader icon={faExclamationTriangle} text="Issues" />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Issue Reports", "Search Issues", "Report New Issue"]}
          activeTab={"Issue Reports"}
          urls={["/issues", "/issues/search", "/issues/new"]}
        />
      )}
      {showChart &&
        (dataReady ? (
          <div className={`${isMobile ? "p-mb-4" : "p-mt-5"}`}>
            <BreakDownChartCard
              chartParams={issueChartData}
              title={t("issuesPanelIndex.issues")}
              titleColor={colorVars.red}
              subTitle={t("issuesPanelIndex.division_breakdown")}
              aspectRatio={2}
              innerRadius={50}
              isMobile={isMobile}
              size={isMobile ? "300px" : "350px"}
            />
          </div>
        ) : (
          <div className={`${isMobile ? "p-mb-3" : "p-mt-3 p-mb-3"}`}>
            <FullWidthSkeleton height={isMobile ? "300px" : "350px"} />
          </div>
        ))}
      <TabView
        className="darkSubTab darkTable"
        activeIndex={activeIndex}
        onTabChange={(e) => {
          persistSetTab(e, history);
          setActiveIndex(e.index);
        }}
      >
        <TabPanel header={t("issuesPanelIndex.unresolved_issues").toUpperCase()}>
          <CommonIssuesPanel
            issues={unresolvedIssues}
            setIssues={setIssues}
            selectedIssue={selectedUnresolvedIssue}
            setSelectedIssue={setSelectedUnresolvedIssue}
            dataReady={dataReady}
            setShowChart={setShowChart}
            issuePanel={"all"}
            tab={activeIndex}
          />
        </TabPanel>
        <TabPanel header={t("issuesPanelIndex.resolved_issues").toUpperCase()}>
          <CommonIssuesPanel
            issues={resolvedIssues}
            selectedIssue={selectedResolvedIssue}
            setSelectedIssue={setSelectedResolvedIssue}
            dataReady={dataReady}
            setShowChart={setShowChart}
            issuePanel={"all"}
            tab={activeIndex}
          />
        </TabPanel>
      </TabView>
    </div>
  );
};

export default UnresolvedIssuesPanel;
