import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import { TabView, TabPanel } from "primereact/tabview";
import { faCarCrash } from "@fortawesome/free-solid-svg-icons";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import BreakDownChartCard from "../../ShareComponents/ChartCard/BreakdownChartCard";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import CommonIncidentsPanel from "./CommonIncidentsPanel";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import colorVars from "../../../styles/variables.scss";
import { useHistory } from "react-router-dom";
import { persistSetTab } from "../../../helpers/helperFunctions";
import { persistGetTab } from "../../../helpers/helperFunctions";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";

const IncidentReportsPanel = () => {
  const [incidents, setIncidents] = useState([]);
  const [dataReady, setDataReady] = useState(false);
  const [selectedUnresolvedIncident, setSelectedUnresolvedIncident] = useState(null);
  const [selectedResolvedIncident, setSelectedResolvedIncident] = useState(null);
  const [showChart, setShowChart] = useState(true);
  const [activeIndex, setActiveIndex] = useState(0);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const { t } = useTranslation();

  const history = useHistory();

  useEffect(() => {
    persistGetTab(setActiveIndex);
  }, []);

  useEffect(() => {
    if (!dataReady) {
      const cancelTokenSource = axios.CancelToken.source();
      setSelectedUnresolvedIncident(null);
      setSelectedResolvedIncident(null);

      axios
        .post(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Accident/List/Date`,
          { start_date: "1900-01-01", end_date: "2099-12-31" },
          { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
        )
        .then((response) => {
          setIncidents(response.data);
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
  }, [dataReady]);

  let resolvedIncidents = [];
  let unresolvedIncidents = [];
  let resolvedCount;
  let unresolvedCount;
  let incidentChartData = null;
  let threeMonthsDate = new Date();
  threeMonthsDate.setMonth(threeMonthsDate.getMonth() - 3);

  if (incidents) {
    unresolvedIncidents = incidents.filter((i) => {
      return !i.is_resolved;
    });
    unresolvedCount = unresolvedIncidents.filter(
      (incident) => new Date(threeMonthsDate) < new Date(incident.date_created)
    ).length;

    resolvedIncidents = incidents.filter((i) => {
      return i.is_resolved;
    });
    resolvedCount = resolvedIncidents.filter(
      (incident) => new Date(threeMonthsDate) < new Date(incident.date_created)
    ).length;

    if (incidents.length > 0) {
      incidentChartData = [
        {
          data: (unresolvedCount / (resolvedCount + unresolvedCount)) * 100,
          label: t("incidentsDetails.unresolved_incidents").toUpperCase(),
          color: colorVars.blue,
          full: 100,
        },
        {
          data: (resolvedCount / (resolvedCount + unresolvedCount)) * 100,
          label: t("incidentsDetails.resolved_incidents").toUpperCase(),
          color: colorVars.orange,
          full: 100,
        },
      ];
    }
  }

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["Incident Reports", "New Incident"]}
          activeTab={"Incident Reports"}
          urls={["/incidents", "/incidents/new"]}
        />
      )}
      <PanelHeader icon={faCarCrash} text={t("incidentsDetails.incident_reports")} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Incident Reports", "New Incident"]}
          activeTab={"Incident Reports"}
          urls={["/incidents", "/incidents/new"]}
        />
      )}

      {showChart &&
        (dataReady ? (
          <div className={`${isMobile ? "p-mb-4" : "p-mt-5"}`}>
            <BreakDownChartCard
              chartParams={incidentChartData}
              title={t("incidentsDetails.incident_title")}
              titleColor={colorVars.red}
              subTitle={t("incidentsDetails.incident_subtitle")}
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
        <TabPanel header={t("incidentsDetails.unresolved_incidents").toUpperCase()}>
          <CommonIncidentsPanel
            incidents={unresolvedIncidents}
            selectedIncident={selectedUnresolvedIncident}
            setSelectedIncident={setSelectedUnresolvedIncident}
            dataReady={dataReady}
            setDataReady={setDataReady}
            setShowChart={setShowChart}
            setIncidents={setIncidents}
            tab={activeIndex}
          />
        </TabPanel>
        <TabPanel header={t("incidentsDetails.resolved_incidents").toUpperCase()}>
          <CommonIncidentsPanel
            incidents={resolvedIncidents}
            selectedIncident={selectedResolvedIncident}
            setSelectedIncident={setSelectedResolvedIncident}
            dataReady={dataReady}
            setDataReady={setDataReady}
            setShowChart={setShowChart}
            setIncidents={setIncidents}
            tab={activeIndex}
          />
        </TabPanel>
      </TabView>
    </div>
  );
};

export default IncidentReportsPanel;
