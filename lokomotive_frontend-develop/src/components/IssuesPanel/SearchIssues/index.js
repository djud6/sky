import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { useDispatch } from "react-redux";
import { useHistory } from "react-router-dom";
import * as Constants from "../../../constants";
import { faSearch } from "@fortawesome/free-solid-svg-icons";
import { TabView, TabPanel } from "primereact/tabview";
import { getAuthHeader, getRolePermissions } from "../../../helpers/Authorization";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import CommonIssuesPanel from "../UnresolvedIssues/CommonIssuesPanel";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import { UPDATE_ISSUES } from "../../../redux/types/issueTypes";
import { persistSetTab } from "../../../helpers/helperFunctions";
import { persistGetTab } from "../../../helpers/helperFunctions";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";

const SearchIssuesPanel = () => {
  const { t } = useTranslation();
  const history = useHistory();
  const [isOperator, setIsOperator] = useState(false);
  const [activeVehicle, setActiveVehicle] = useState(null);
  const [issues, setVehicleIssues] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [dataReady, setDataReady] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const dispatch = useDispatch();

  useEffect(() => {
    const rolePermissions = getRolePermissions();
    if (rolePermissions.role.toLowerCase() === "operator") setIsOperator(true);
  }, []);

  useEffect(() => {
    window.history.replaceState(null, "", window.location.pathname);
    persistGetTab(setActiveIndex);
  }, []);

  useEffect(() => {
    setDataReady(false);
    setSelectedIssue(null);
    setVehicleIssues(null);
    if (activeVehicle) {
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Issues/VIN/${activeVehicle.VIN}`, getAuthHeader())
        .then((res) => {
          let issues;
          if (res.data.length === 0) {
            issues = [];
          } else {
            issues = res.data;
          }
          setVehicleIssues(issues);
          dispatch({ type: UPDATE_ISSUES, data: issues });
          setDataReady(true);
        })
        .catch((err) => {
          ConsoleHelper("Error grabbing issues. SearchIssuesPanel.js", err);
          setVehicleIssues(null);
          dispatch({ type: UPDATE_ISSUES, data: [] });
          setDataReady(true);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    // eslint-disable-next-line
  }, [activeVehicle]);

  useEffect(() => {
    if (activeVehicle && !dataReady) {
      setSelectedIssue(null);
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Issues/VIN/${activeVehicle.VIN}`, getAuthHeader())
        .then((res) => {
          let issues;
          if (res.data.length === 0) {
            issues = [];
          } else {
            issues = res.data;
          }
          setVehicleIssues(issues);
          dispatch({ type: UPDATE_ISSUES, data: issues });
          setDataReady(true);
        })
        .catch((err) => {
          ConsoleHelper("Error grabbing issues. SearchIssuesPanel.js", err);
          setVehicleIssues(null);
          dispatch({ type: UPDATE_ISSUES, data: [] });
          setDataReady(true);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataReady]);

  const renderResults = () => {
    const resolvedIssues = issues.filter((issue) => issue.is_resolved);
    const unresolvedIssuess = issues.filter((issue) => !issue.is_resolved);

    return (
      <div>
        <TabView
          className={`darkSubTab darkTable ${isMobile ? "" : "p-mt-5"}`}
          activeIndex={activeIndex}
          onTabChange={(e) => {
            persistSetTab(e, history);
            setActiveIndex(e.index);
          }}
        >
          <TabPanel header={t("issuesPanelIndex.unresolved_issues").toUpperCase()}>
            <CommonIssuesPanel
              issues={unresolvedIssuess}
              setIssues={setVehicleIssues}
              selectedIssue={selectedIssue}
              setSelectedIssue={setSelectedIssue}
              dataReady={dataReady}
              setDataReady={setDataReady}
              issuePanel={"search"}
              tab={activeIndex}
            />
          </TabPanel>
          <TabPanel header={t("issuesPanelIndex.resolved_issues").toUpperCase()}>
            <CommonIssuesPanel
              issues={resolvedIssues}
              selectedIssue={selectedIssue}
              setSelectedIssue={setSelectedIssue}
              dataReady={dataReady}
              setDataReady={setDataReady}
              issuePanel={"search"}
              tab={activeIndex}
            />
          </TabPanel>
        </TabView>
      </div>
    );
  };

  return (
    <div>
      {isMobile && !isOperator && (
        <QuickAccessTabs
          tabs={["Reports", "Search", "New Issue"]}
          activeTab={"Search"}
          urls={["/issues", "/issues/search", "/issues/new"]}
        />
      )}
      {isMobile && isOperator && (
        <QuickAccessTabs
          tabs={["Search Issues", "New Issue"]}
          activeTab={"Search Issues"}
          urls={["/issues/search", "/issues/new"]}
        />
      )}
      <PanelHeader icon={faSearch} text={t("searchIssuesPanel.search_issues")} />
      {!isMobile && !isOperator && (
        <QuickAccessTabs
          tabs={["Issue Reports", "Search Issues", "Report New Issue"]}
          activeTab={"Search Issues"}
          urls={["/issues", "/issues/search", "/issues/new"]}
        />
      )}
      {!isMobile && isOperator && (
        <QuickAccessTabs
          tabs={["Search Issues", "Report New Issue"]}
          activeTab={"Search Issues"}
          urls={["/issues/search", "/issues/new"]}
        />
      )}
      <div className={`${isMobile ? "p-pb-4" : "p-mt-5"}`}>
        <VINSearch
          onVehicleSelected={(vehicle) => {
            setActiveVehicle(vehicle);
          }}
        />
      </div>
      {activeVehicle && issues && renderResults()}
    </div>
  );
};

export default SearchIssuesPanel;
