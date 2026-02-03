import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import { TabView, TabPanel } from "primereact/tabview";
import { faWrench } from "@fortawesome/free-solid-svg-icons";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import BreakDownChartCard from "../../ShareComponents/ChartCard/BreakdownChartCard";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import CommonRepairsPanel from "./CommonRepairsPanel";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import RepairDetailsMore from "./RepairDetailsMore";
import RepairDetailsMoreMobile from "./RepairDetailsMoreMobile";
import { useHistory } from "react-router-dom";
import { persistSetTab } from "../../../helpers/helperFunctions";
import { persistGetTab } from "../../../helpers/helperFunctions";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";

const RepairsPanel = () => {
  const [dataReady, setDataReady] = useState(false);
  const [repairRequests, setRepairRequests] = useState([]);
  const [completeRepairRequests, setCompleteRepairRequests] = useState([]);
  const [selectedRepair, setSelectedRepair] = useState(null);
  const [moreDetails, setMoreDetails] = useState(false);
  const [detailsSection, setDetailsSection] = useState(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [showChart, setShowChart] = useState(true);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const { t } = useTranslation();

  const history = useHistory();

  useEffect(() => {
    persistGetTab(setActiveIndex);
  }, []);

  useEffect(() => {
    setSelectedRepair(null);
  }, [activeIndex]);

  useEffect(() => {
    setSelectedRepair(null);
    if (!!!dataReady) {
      const cancelTokenSource = axios.CancelToken.source();
      let incompleteRepairsList = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Repair/List`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });
      let completeRepairsList = axios.get(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Complete/List`,
        {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        }
      );
      axios
        .all([incompleteRepairsList, completeRepairsList])
        .then(
          axios.spread((...responses) => {
            const repairs = responses[0].data;
            const completeRepairs = responses[1].data;
            for (var i in repairs) {
              if (repairs[i].is_urgent) repairs[i].is_urgent = "Yes";
              else repairs[i].is_urgent = "No";

              if (repairs[i].in_house) {
                repairs[i].vendor_name = "In-house Repair";
              } else if (!repairs[i].in_house && !repairs[i].vendor_name) {
                if (repairs[i].vendor_email && !["", "NA"].includes(repairs[i].vendor_email)) {
                  repairs[i].vendor_name = repairs[i].vendor_email;
                }
              }
            }
            for (var y in completeRepairs) {
              if (completeRepairs[y].in_house) {
                completeRepairs[y].vendor_name = "In-house Repair";
              } else if (!completeRepairs[y].in_house && !completeRepairs[y].vendor_name) {
                if (
                  completeRepairs[y].vendor_email &&
                  !["", "NA"].includes(completeRepairs[y].vendor_email)
                ) {
                  completeRepairs[y].vendor_name = completeRepairs[y].vendor_email;
                }
              }
            }
            setRepairRequests(repairs);
            setCompleteRepairRequests(completeRepairs);
            setDataReady(true);
          })
        )
        .catch((error) => {
          setDataReady(true);
          ConsoleHelper(error);
        });

      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
  }, [dataReady]);

  let beginningOfYearDate = new Date();
  beginningOfYearDate.setMonth(0);
  beginningOfYearDate.setDate(1);
  beginningOfYearDate.setHours(0, 0, 0, 0);

  const activeCountOneYear = repairRequests.filter(
    (repair) => (new Date(beginningOfYearDate) < new Date(repair.date_created))
  ).length;
  const closedCountOneYear = completeRepairRequests.filter(
    (repair) => (new Date(beginningOfYearDate) < new Date(repair.date_created))
  ).length;

  let repairData = [
    {
      data: (activeCountOneYear / (activeCountOneYear + closedCountOneYear)) * 100,
      label: t("repairsPanelIndex.tabTitles_active").toUpperCase(),
      full: 100,
    },
    {
      data: (closedCountOneYear / (activeCountOneYear + closedCountOneYear)) * 100,
      label: t("repairsPanelIndex.tabTitles_closed").toUpperCase(),
      full: 100,
    },
  ];

  const scheduledCountOneYear = repairRequests.filter(
    (repair) => (repair.status === "schedule" && new Date(beginningOfYearDate) < new Date(repair.date_created))
  ).length;
  const waitingOnPartsCountOneYear = repairRequests.filter(
    (repair) => (repair.status === "waiting on parts" && new Date(beginningOfYearDate) < new Date(repair.date_created))
  ).length;
  const underRepairCountOneYear = repairRequests.filter(
    (repair) => (repair.status === "under repair" && new Date(beginningOfYearDate) < new Date(repair.date_created))
  ).length;
  const waitingForPickupCountOneYear = repairRequests.filter(
    (repair) => (repair.status === "waiting for pickup" && new Date(beginningOfYearDate) < new Date(repair.date_created))
  ).length;
  let totalOneYearCount = scheduledCountOneYear + waitingOnPartsCountOneYear + underRepairCountOneYear + waitingForPickupCountOneYear;

  let activeRepairDataOneYear = [
    {
      data: scheduledCountOneYear / totalOneYearCount * 100,
      label: t("repairsPanelIndex.tabTitles_scheduled").toUpperCase(),
      full: 100,
    },
    {
      data: waitingOnPartsCountOneYear / totalOneYearCount * 100,
      label: t("repairsPanelIndex.tabTitles_waiting_on_parts").toUpperCase(),
      full: 100,
    },
    {
      data: underRepairCountOneYear / totalOneYearCount * 100,
      label: t("repairsPanelIndex.tabTitles_under_repair").toUpperCase(),
      full: 100,
    },
    {
      data: waitingForPickupCountOneYear / totalOneYearCount * 100,
      label: t("repairsPanelIndex.tabTitles_waiting_for_pickup").toUpperCase(),
      full: 100,
    },
  ];

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["List Repairs", "Repair Request"]}
          activeTab={"List Repairs"}
          urls={["/repairs", "/repairs/request"]}
        />
      )}
      <PanelHeader icon={faWrench} text={t("repairsPanelIndex.repairs")} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["List Repairs", "Repair Request"]}
          activeTab={"List Repairs"}
          urls={["/repairs", "/repairs/request"]}
        />
      )}
      {moreDetails ? (
        isMobile ? (
          <RepairDetailsMoreMobile
            repair={selectedRepair}
            detailsSection={detailsSection}
            setMoreDetails={setMoreDetails}
            setDataReady={setDataReady}
          />
        ) : (
          <RepairDetailsMore
            repair={selectedRepair}
            setMoreDetails={setMoreDetails}
            setDataReady={setDataReady}
          />
        )
      ) : (
        <React.Fragment>
          {showChart &&
            (dataReady ? (
              <div className={`${isMobile ? "p-mb-4" : "p-mt-5"}`}>
                <BreakDownChartCard
                  chartParams={repairData}
                  title={t("repairsPanelIndex.repairs_title")}
                  innerRadius={50}
                  isMobile={isMobile}
                  size={isMobile ? "300px" : "400px"}
                  oneYearTimePeriod={true}
                />
                <BreakDownChartCard
                  chartParams={activeRepairDataOneYear}
                  title={t("repairsPanelIndex.repairs_title")}
                  innerRadius={30}
                  isMobile={isMobile}
                  size={isMobile ? "300px" : "400px"}
                  oneYearTimePeriod={true}
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
            <TabPanel header={t("repairsPanelIndex.tabTitles_in_progress").toUpperCase()}>
              <CommonRepairsPanel
                category="inProgress"
                repairs={repairRequests}
                selectedRepair={selectedRepair}
                setSelectedRepair={setSelectedRepair}
                dataReady={dataReady}
                setMoreDetails={setMoreDetails}
                setDetailsSection={setDetailsSection}
                setShowChart={setShowChart}
                setRepairRequests={setRepairRequests}
                setDataReady={setDataReady}
                tab={activeIndex}
              />
            </TabPanel>
            <TabPanel header={t("repairsPanelIndex.tabTitles_completed").toUpperCase()}>
              <CommonRepairsPanel
                category="completed"
                repairs={completeRepairRequests}
                selectedRepair={selectedRepair}
                setSelectedRepair={setSelectedRepair}
                dataReady={dataReady}
                setMoreDetails={setMoreDetails}
                setDetailsSection={setDetailsSection}
                setShowChart={setShowChart}
                setRepairRequests={setCompleteRepairRequests}
                setDataReady={setDataReady}
                tab={activeIndex}
              />
            </TabPanel>
          </TabView>
        </React.Fragment>
      )}
    </div>
  );
};

export default RepairsPanel;
