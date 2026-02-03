import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { TabView, TabPanel } from "primereact/tabview";
import { Button } from "primereact/button";
import { faCalendarPlus, faList } from "@fortawesome/free-solid-svg-icons";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import MaintenanceRules from "./MaintenanceRules";
import MaintenanceRulesMobile from "./MaintenanceRulesMobile";
import ForecastedMaintenance from "./ForecastedMaintenance";
import ForecastedMaintenanceMobile from "./ForecastedMaintenanceMobile";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";
import "../../../styles/MaintenancePanel/MaintenanceForecast/MaintenanceForecastMobile.scss";

const MaintenanceForecastPanel = () => {
  const { t } = useTranslation();
  const [dataReady, setDataReady] = useState(false);
  const [maintenanceList, setMaintenanceList] = useState(null);
  const [mobilePage, setMobilePage] = useState("main");
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  // Getting inspection types
  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Inspection/List`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        setDataReady(true);
        setMaintenanceList(response.data);
      })
      .catch((error) => {
        ConsoleHelper(error);
      });
    return () => {
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, []);

  return (
    <React.Fragment>
      {!isMobile ? (
        <div>
          <PanelHeader
            icon={faCalendarPlus}
            text={t("maintenanceForecastPanel.maintenance_forecast")}
          />
          <QuickAccessTabs
            tabs={["Status", "Schedule", "Forecast", "Lookup"]}
            activeTab={"Forecast"}
            urls={[
              "/maintenance",
              "/maintenance/schedule",
              "/maintenance/forecast",
              "/maintenance/lookup",
            ]}
          />
          <TabView className="darkSubTab p-mt-5">
            <TabPanel header={t("maintenanceForecastPanel.preventative_maintenance").toUpperCase()}>
              <MaintenanceRules maintenanceTypes={maintenanceList} />
            </TabPanel>
            <TabPanel header={t("maintenanceForecastPanel.recommended_maintenance").toUpperCase()}>
              <ForecastedMaintenance maintenanceList={maintenanceList} dataReady={dataReady} />
            </TabPanel>
          </TabView>
        </div>
      ) : (
        <div className="forecast-mobile">
          {mobilePage === "main" && (
            <div className="main-tab">
              <QuickAccessTabs
                tabs={["Status", "Schedule", "Forecast", "Lookup"]}
                activeTab={"Forecast"}
                urls={[
                  "/maintenance",
                  "/maintenance/schedule",
                  "/maintenance/forecast",
                  "/maintenance/lookup",
                ]}
              />
              <PanelHeader
                icon={faCalendarPlus}
                text={t("maintenanceForecastPanel.maintenance_forecast")}
              />
              <div className="sub-tabpanel-btns p-d-flex p-flex-column">
                <Button
                  label="Maintenance Rules"
                  icon="pi pi-angle-right"
                  iconPos="right"
                  onClick={() => setMobilePage("rules")}
                />
                <Button
                  label="Forecasted Maintenance"
                  icon="pi pi-angle-right"
                  iconPos="right"
                  onClick={() => setMobilePage("forecasts")}
                />
              </div>
            </div>
          )}
          {mobilePage === "rules" && (
            <div>
              <PanelHeader
                icon={faList}
                text={t("maintenanceForecastPanel.preventative_maintenance")}
              />
              <MaintenanceRulesMobile
                setMobilePage={setMobilePage}
                maintenanceTypes={maintenanceList}
              />
            </div>
          )}
          {mobilePage === "forecasts" && (
            <div>
              <PanelHeader
                icon={faCalendarPlus}
                text={t("maintenanceForecastPanel.recommended_maintenance")}
              />
              <ForecastedMaintenanceMobile
                setMobilePage={setMobilePage}
                maintenanceList={maintenanceList}
                dataReady={dataReady}
              />
            </div>
          )}
        </div>
      )}
    </React.Fragment>
  );
};

export default MaintenanceForecastPanel;
