import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import { TabView, TabPanel } from "primereact/tabview";
import { faOilCan } from "@fortawesome/free-solid-svg-icons";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import CommomMaintenancePanel from "./CommomMaintenancePanel";
import MaintenanceDetailsMore from "./MaintenanceDetailsMore";
import MaintenanceDetailsMoreMobile from "./MaintenanceDetailsMoreMobile";
import AvgMaintennaceCostChartCard from "../../ShareComponents/ChartCard/AvgMaintenanceCostChartCard";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import { useHistory } from "react-router-dom";
import { persistSetTab } from "../../../helpers/helperFunctions";
import { persistGetTab } from "../../../helpers/helperFunctions";
import MaintenceCostChartCard from "../../ShareComponents/ChartCard/MaintenceCostChartCard";
import { useRequestedData } from "../../../hooks/dataDetcher";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";

const MaintenanceStatusPanel = () => {
  const [dataReady, setDataReady] = useState(false);
  const [outstandingMaintenance, setOutstandingMaintenance] = useState([]);
  const [completedMaintenance, setCompletedMaintenance] = useState([]);
  const [selectedMaintenance, setSelectedMaintenance] = useState(null);
  const [moreDetails, setMoreDetails] = useState(false);
  const [detailsSection, setDetailsSection] = useState(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [avgMaintenanceCostChartParams, setAvgMaintenanceCostChartParams] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const { t } = useTranslation();

  const history = useHistory();

  const dataReady2 = [];
  let url = "api/v1/Assets/AverageMaintenanceCostPerUnit/2022-01-01:2022-02-01";
  let [data, dataArray, error] = useRequestedData(url);
  if (data) {
    if (error) {
      ConsoleHelper("errors:", error);
    }
     dataReady2.push(dataArray.average_cost_per_mileage);
  }
  url = "api/v1/Assets/AverageMaintenanceCostPerUnit/2022-02-01:2022-03-01";
  [data, dataArray, error] = useRequestedData(url);
  if (data) {
    if (error) {
      ConsoleHelper("errors:", error);
    }
     dataReady2.push(dataArray.average_cost_per_mileage);
  }
  url = "api/v1/Assets/AverageMaintenanceCostPerUnit/2022-03-01:2022-04-01";
  [data, dataArray, error] = useRequestedData(url);
  if (data) {
    if (error) {
      ConsoleHelper("errors:", error);
    }
     dataReady2.push(dataArray.average_cost_per_mileage);
  }
  url = "api/v1/Assets/AverageMaintenanceCostPerUnit/2022-04-01:2022-05-01";
  [data, dataArray, error] = useRequestedData(url);
  if (data) {
    if (error) {
      ConsoleHelper("errors:", error);
    }
     dataReady2.push(dataArray.average_cost_per_mileage);
  }
  url = "api/v1/Assets/AverageMaintenanceCostPerUnit/2022-05-01:2022-06-01";
  [data, dataArray, error] = useRequestedData(url);
  if (data) {
    if (error) {
      ConsoleHelper("errors:", error);
    }
     dataReady2.push(dataArray.average_cost_per_mileage);
  }
  url = "api/v1/Assets/AverageMaintenanceCostPerUnit/2022-06-01:2022-07-01";
  [data, dataArray, error] = useRequestedData(url);
  if (data) {
    if (error) {
      ConsoleHelper("errors:", error);
    }
     dataReady2.push(dataArray.average_cost_per_mileage);
  }
 //console.log("hhhh", dataReady2);
  const datas = [];
  for(let i = 1; i<=6; i++){
    datas.push({
      "month": i.toString(),
      "maintenance_cost": dataReady2[i-1],
    });
  }
  //console.log("hhhhhhh", datas);
  
  useEffect(() => {
    setSelectedMaintenance(null);
  }, [activeIndex]);

  useEffect(() => {
    persistGetTab(setActiveIndex);
  }, []);

  useEffect(() => {
    if (!!!dataReady) {
      setOutstandingMaintenance([]);
      setCompletedMaintenance([]);
      setSelectedMaintenance(null);
      setAvgMaintenanceCostChartParams(null);
      const cancelTokenSource = axios.CancelToken.source();
      let ongoingM = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/List`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });
      let completedM = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Completed/List`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });
      let averageMCost = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/AverageMaintenanceCost`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });
      axios
        .all([ongoingM, completedM, averageMCost])
        .then(
          axios.spread((...responses) => {
            const maintenance = responses[0].data;
            const completeMaintenance = responses[1].data;
            const averageMaintenanceCost = responses[2].data;
            for (var i in maintenance) {
              if (maintenance[i].in_house) {
                maintenance[i].vendor_name = "In-house Maintenance";
              } else if (!maintenance[i].in_house && !maintenance[i].vendor_name) {
                if (
                  maintenance[i].vendor_email &&
                  !["", "NA"].includes(maintenance[i].vendor_email)
                ) {
                  maintenance[i].vendor_name = maintenance[i].vendor_email;
                }
              }
            }
            for (var y in completeMaintenance) {
              if (completeMaintenance[y].in_house) {
                completeMaintenance[y].vendor_name = "In-house Maintenance";
              } else if (!completeMaintenance[y].in_house && !completeMaintenance[y].vendor_name) {
                if (
                  completeMaintenance[y].vendor_email &&
                  !["", "NA"].includes(completeMaintenance[y].vendor_email)
                ) {
                  completeMaintenance[y].vendor_name = completeMaintenance[y].vendor_email;
                }
              }
            }
            setOutstandingMaintenance(maintenance);
            setCompletedMaintenance(completeMaintenance);
            setAvgMaintenanceCostChartParams(averageMaintenanceCost);
            setDataReady(true);
          })
        )
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
  }, [dataReady]);

  if (!outstandingMaintenance) return null;

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["Status", "Schedule", "Forecast", "Lookup"]}
          activeTab={"Status"}
          urls={[
            "/maintenance",
            "/maintenance/schedule",
            "/maintenance/forecast",
            "/maintenance/lookup",
          ]}
        />
      )}
      <PanelHeader icon={faOilCan} text={t("maintenancePanelIndex.page_title")} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Status", "Schedule", "Forecast", "Lookup"]}
          activeTab={"Status"}
          urls={[
            "/maintenance",
            "/maintenance/schedule",
            "/maintenance/forecast",
            "/maintenance/lookup",
          ]}
        />
      )}
      {moreDetails ? (
        isMobile ? (
          <MaintenanceDetailsMoreMobile
            maintenance={selectedMaintenance}
            detailsSection={detailsSection}
            setMoreDetails={setMoreDetails}
            setDataReady={setDataReady}
          />
        ) : (
          <MaintenanceDetailsMore
            maintenance={selectedMaintenance}
            setMoreDetails={setMoreDetails}
            setDataReady={setDataReady}
          />
        )
      ) : (
        <React.Fragment>
          {dataReady ? (
            <div className={`${isMobile ? "p-mb-4" : "p-mt-5"}`}>
              <AvgMaintennaceCostChartCard
                chartParams={avgMaintenanceCostChartParams}
                dataReady={dataReady}
                height={isMobile ? "300px" : "350px"}
              />
            </div>
          ) : (
            <div className={`${isMobile ? "p-mb-3" : "p-mt-3 p-mb-3"}`}>
              <FullWidthSkeleton height={isMobile ? "300px" : "350px"} />
            </div>
          )}
           {dataReady ? (
            <div className={`${isMobile ? "p-mb-4" : "p-mt-5"}`}>
              <MaintenceCostChartCard
                 dataReady={datas}
                 error={error}
              /> 
            </div>
          ) : (
            <div className={`${isMobile ? "p-mb-3" : "p-mt-3 p-mb-3"}`}>
              <FullWidthSkeleton height={isMobile ? "300px" : "350px"} />
            </div>
          )}
          <TabView
            className={`darkSubTab darkTable ${isMobile ? "" : "p-mt-5"}`}
            activeIndex={activeIndex}
            onTabChange={(e) => {
              persistSetTab(e, history);
              setActiveIndex(e.index);
            }}
          >
            <TabPanel header={t("maintenancePanelIndex.outstanding_maintenance").toUpperCase()}>
              <CommomMaintenancePanel
                category={"outstanding"}
                maintenances={outstandingMaintenance}
                selectedMaintenance={selectedMaintenance}
                setSelectedMaintenance={setSelectedMaintenance}
                dataReady={dataReady}
                setMoreDetails={setMoreDetails}
                setDetailsSection={setDetailsSection}
                setMaintenances={setOutstandingMaintenance}
                setDataReady={setDataReady}
                maintenanceType={"Outstanding"}
                tab={activeIndex}
              />
            </TabPanel>
            <TabPanel header={t("maintenancePanelIndex.completed_maintenance").toUpperCase()}>
              <CommomMaintenancePanel
                category={"completed"}
                maintenances={completedMaintenance}
                selectedMaintenance={selectedMaintenance}
                setSelectedMaintenance={setSelectedMaintenance}
                dataReady={dataReady}
                setMoreDetails={setMoreDetails}
                setDetailsSection={setDetailsSection}
                setMaintenances={setCompletedMaintenance}
                setDataReady={setDataReady}
                maintenanceType={"Completed"}
                tab={activeIndex}
              />
            </TabPanel>
          </TabView>
        </React.Fragment>

      )}
    </div>
  );
};

export default MaintenanceStatusPanel;
