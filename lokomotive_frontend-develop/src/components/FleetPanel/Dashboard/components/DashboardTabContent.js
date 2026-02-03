import React from "react";
import { useTranslation } from "react-i18next";
import { faChartArea } from "@fortawesome/free-solid-svg-icons";
import ExecutivePanel from "../ExecutivePanel";
import ManagerPanel from "../ManagerPanel";
import PanelHeader from "../../../ShareComponents/helpers/PanelHeader";
import DashboardEditControls from "./DashboardEditControls";

/**
 * Dashboard Tab Content Component
 * Handles rendering of executive and manager dashboard tabs
 */
const DashboardTabContent = ({
  tabType,
  isMobile,
  isEdit,
  onToggleEdit,
  dashboardData,
  layoutData,
}) => {
  const { t } = useTranslation();

  const renderExecutiveTab = () => (
    <>
      {isMobile && (
        <PanelHeader icon={faChartArea} text={t("fleetPanel.page_title_mobile")} />
      )}
      <DashboardEditControls isEdit={isEdit} onToggleEdit={onToggleEdit} />
      <ExecutivePanel
        overallChartParams={dashboardData.overallChartParams}
        avgMaintenanceChartParams={dashboardData.avgMaintenanceChartParams}
        downtimeChartParams={dashboardData.downtimeChartParams}
        stackedClusteredChart={dashboardData.stackedClusteredChart}
        operationalCostParams={dashboardData.operationalCostParams}
        mapChartParams={dashboardData.mapChartParams}
        assetUtilChartParams={dashboardData.assetUtilChartParams}
        clusterChartParams={dashboardData.clusterChartParams}
        leaderboardChartParams={dashboardData.leaderboardChartParams}
        costPerProcessParams={dashboardData.costPerProcessParams}
        workOrderCompletionTimeParams={dashboardData.workOrderCompletionTimeParams}
        dataReady={dashboardData.executiveDataReady}
        errors={dashboardData.executiveErrors}
        dashboard_layout={layoutData.exec_layout}
        isEdit={isEdit}
      />
    </>
  );

  const renderManagerTab = () => (
    <>
      {isMobile && (
        <PanelHeader icon={faChartArea} text={t("fleetPanel.page_title_mobile")} />
      )}
      <DashboardEditControls isEdit={isEdit} onToggleEdit={onToggleEdit} />
      <ManagerPanel
        stackedClusteredChart={dashboardData.stackedClusteredChart}
        mapChartParams={dashboardData.mapChartParams}
        downtimeChartParams={dashboardData.downtimeChartParams}
        clusterChartParams={dashboardData.clusterChartParams}
        assetCheckParams={dashboardData.assetCheckParams}
        dataReady={dashboardData.managerDataReady}
        errors={dashboardData.managerErrors}
        dashboard_layout={layoutData.mngr_layout}
        isEdit={isEdit}
      />
    </>
  );

  if (tabType === "executive") {
    return renderExecutiveTab();
  }

  if (tabType === "manager") {
    return renderManagerTab();
  }

  return null;
};

export default DashboardTabContent;
