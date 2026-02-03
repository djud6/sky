import { useRequestedData } from "../../../../hooks/dataDetcher";
import { useTranslation } from "react-i18next";
import moment from "moment";
import ConsoleHelper from "../../../../helpers/ConsoleHelper";

/**
 * Custom hook to manage all dashboard data fetching and processing
 * Separates data concerns from UI logic
 */
export const useDashboardData = () => {
  const { t } = useTranslation();

  // API calls
  const [dataReady1, dataArray1, error1] = useRequestedData("api/v1/Chart/Get/Status/Breakdown");
  const [dataReady2, dataArray2, error2] = useRequestedData("api/v1/Chart/Get/Location/Maintenance/Downtime/Average");
  const [dataReady3, dataArray3, error3] = useRequestedData("api/v1/Accident/Downtime/Fleet");
  const [dataReady4, dataArray4, error4] = useRequestedData("api/v1/Chart/Get/Process/Breakdown");
  const [dataReady5, dataArray5, error5] = useRequestedData("api/v1/Chart/Get/Location/Count/Operators/Assets");
  const [dataReady6, dataArray6, error6] = useRequestedData("api/v1/Chart/Get/Location/AssetTypes");
  const [dataReady7, dataArray7, error7] = useRequestedData("api/v1/Chart/Get/Asset/Performance/Leaderboard");
  const [dataReady8, dataArray8, error8] = useRequestedData("api/v1/Chart/Fleet/Usage");
  const [dataReady9, dataArray9, error9] = useRequestedData("/api/v1/Chart/Get/Operational/Cost");
  const [dataReady10, dataArray10, error10] = useRequestedData("/api/v1/Chart/Get/dailyChecksAndAssets");
  const [dataReady11, dataArray11, error11] = useRequestedData("api/v1/Chart/Get/ProcessCostByLocation");
  const [dataReady12, dataArray12, error12] = useRequestedData("api/v1/Chart/Get/WorkOrderCompletionTime");

  // Process overall chart data
  const processOverallChartData = () => {
    if (!dataReady1 || error1) {
      if (error1) ConsoleHelper("errors:", error1);
      return null;
    }

    const overviewData = dataArray1 || null;
    if (!overviewData) return null;

    const denominator = 
      overviewData.active_num +
      overviewData.incident_num +
      overviewData.repairs_num +
      overviewData.maintenance_num;

    return [
      {
        data: (overviewData.maintenance_num / denominator) * 100,
        label: t("fleetPanel.maintenance"),
        full: 100,
      },
      {
        data: (overviewData.repairs_num / denominator) * 100,
        label: t("fleetPanel.repairs"),
        full: 100,
      },
      {
        data: (overviewData.incident_num / denominator) * 100,
        label: t("fleetPanel.incidents"),
        full: 100,
      },
      {
        data: (overviewData.active_num / denominator) * 100,
        label: t("fleetPanel.active_assets"),
        full: 100,
      },
    ];
  };

  // Process downtime chart data
  const processDowntimeChartData = () => {
    if (!dataReady3 || error3) {
      if (error3) ConsoleHelper("errors:", error3);
      return null;
    }

    const downtimeData = dataArray3 || null;
    if (!downtimeData) return null;

    const denominator = downtimeData.non_preventable_hours + downtimeData.preventable_hours;
    return [
      {
        data: (downtimeData.non_preventable_hours / denominator) * 100,
        label: t("downTime.non_preventable_hours"),
        full: 100,
      },
      {
        data: (downtimeData.preventable_hours / denominator) * 100,
        label: t("downTime.preventable_hours"),
        full: 100,
      },
    ];
  };

  // Process asset utilization data
  const processAssetUtilData = () => {
    if (!dataReady8 || error8) {
      if (error8) ConsoleHelper("errors:", error8);
      return [];
    }

    const assetUtilChartParams = [];
    if (dataArray8["Mileage"] && dataArray8["Mileage"][1]["daily_averages"]) {
      dataArray8["Mileage"][1]["daily_averages"].forEach((datapoint) => {
        assetUtilChartParams.push({
          date: moment(datapoint.date).toISOString(),
          mileage: datapoint.daily_average_per_asset?.toFixed(2) || 0,
          average_mileage_label:
            "Yearly average: " + dataArray8["Mileage"][0]["yearly_average_per_asset"].toFixed(2),
          hours: 0.0,
          average_hours_label:
            "Yearly average: " + dataArray8["Hours"][0]["yearly_average_per_asset"].toFixed(2),
        });
      });
    }
    return assetUtilChartParams;
  };

  // Process errors for logging
  const processErrors = () => {
    const errors = [error1, error2, error3, error4, error5, error6, error7, error8, error9, error10, error11, error12];
    errors.forEach((error, index) => {
      if (error) {
        ConsoleHelper(`Error in data source ${index + 1}:`, error);
      }
    });
  };

  // Call error processing
  processErrors();

  return {
    // Processed data
    overallChartParams: processOverallChartData(),
    avgMaintenanceChartParams: dataReady2 && !error2 ? dataArray2 : null,
    downtimeChartParams: processDowntimeChartData(),
    stackedClusteredChart: dataReady4 && !error4 ? dataArray4 : null,
    mapChartParams: dataReady5 && !error5 ? dataArray5 : null,
    clusterChartParams: dataReady6 && !error6 ? dataArray6 : null,
    leaderboardChartParams: dataReady7 && !error7 ? dataArray7 : null,
    assetUtilChartParams: processAssetUtilData(),
    operationalCostParams: dataReady9 && !error9 ? dataArray9 : null,
    assetCheckParams: dataReady10 && !error10 ? dataArray10 : null,
    costPerProcessParams: dataReady11 && !error11 ? dataArray11 : null,
    workOrderCompletionTimeParams: dataReady12 && !error12 ? dataArray12 : null,

    // Data ready states for executive panel
    executiveDataReady: [
      dataReady1, dataReady2, dataReady3, dataReady4, dataReady5,
      dataReady8, dataReady6, dataReady7, dataReady9, dataReady11, dataReady12
    ],
    
    // Data ready states for manager panel
    managerDataReady: [dataReady5, dataReady3, dataReady4, dataReady6, dataReady10],

    // Error states for executive panel
    executiveErrors: [
      error1, error2, error3, error4, error5,
      error8, error6, error7, error9, error11, error12
    ],

    // Error states for manager panel
    managerErrors: [error5, error3, error4, error6, error10],
  };
};
