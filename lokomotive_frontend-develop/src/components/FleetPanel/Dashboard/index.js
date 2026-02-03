import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import axios from "axios";
import moment from "moment";
import * as Constants from "../../../constants";
import { getAuthHeader, hasModulePermission } from "../../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { TabView, TabPanel } from "primereact/tabview";
import ExecutivePanel from "./ExecutivePanel";
import ManagerPanel from "./ManagerPanel";
import DashboardHeader from "./DashboardHeader";
import { faChartArea } from "@fortawesome/free-solid-svg-icons";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import { useRequestedData } from "../../../hooks/dataDetcher";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import ReactTooltip from "react-tooltip";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { UPDATE_LAYOUT } from "../../../redux/types/apiCallTypes";
import "../../../styles/ShareComponents/TabStyles/tabStyles.scss";
import "../../../../node_modules/react-grid-layout/css/styles.css";
import "../../../../node_modules/react-resizable/css/styles.css";
import "../../../styles/FleetPanel/dashboard.scss";
import "../../../styles/tooltipStyles.scss";
import "../../../styles/ShareComponents/TabStyles/cornerTab.scss";
import { generalErrorAlert } from "../../ShareComponents/CommonAlert";

const FleetPanel = () => {
  const { t } = useTranslation();
  const [activeIndex, setActiveIndex] = useState(0);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const dispatch = useDispatch();
  const { userInfo } = useSelector((state) => state.apiCallData);
  const [isEdit, setIsEdit] = useState(false);
  const [exec_layout, setExecLayout] = useState(null);
  const [mngr_layout, setManagerLayout] = useState(null);

  useEffect(() => {
    const authHeader = getAuthHeader();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Info`, authHeader)
      .then((res) => {
        if (res.data.user_config.dashboard_layout) {
          let payload = res.data.user_config.dashboard_layout.replace(/'/g, '"');
          payload = payload.replace(/False/g, "false");
          payload = payload.replace(/None/g, "null");
          payload = JSON.parse(payload);
          setExecLayout(payload.exec_layout);
          setManagerLayout(payload.mngr_layout);
        }
      })
      .catch((reason) => {
        ConsoleHelper(reason);
        // generalErrorAlert('Oops, some thing went wrong while loading');
      });
  }, []);

  const userInformation = {
    first_name: userInfo.user.first_name,
    role: userInfo.detailed_user.role_permissions.role,
  };

  const saveLayout = () => {
    const exec_layout = JSON.parse(window.localStorage.getItem("exec_layout"));
    const mngr_layout = JSON.parse(window.localStorage.getItem("mngr_layout"));
    if (exec_layout.xs[4].h > 4.5) {
      exec_layout.xs[4].h = 4.5;
      exec_layout.xxs[4].h = 4.5;
    }
    if (exec_layout.xs[5].h > 4.5) {
      exec_layout.xs[5].h = 4.5;
      exec_layout.xxs[5].h = 4.5;
    }
    if (mngr_layout.xs[0].h > 4.5) {
      mngr_layout.xs[0].h = 4.5;
      mngr_layout.xxs[0].h = 4.5;
    }
    const headers = getAuthHeader();
    headers.headers["Content-Type"] = "application/json";
    const data = {
      dashboard_layout: {
        exec_layout: exec_layout,
        mngr_layout: mngr_layout,
      },
    };
    dispatch({ type: UPDATE_LAYOUT, payload: data });
    const requestConfig = {
      method: "post",
      url: `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Update/Configuration`,
      ...headers,
      data: data,
    };
    axios(requestConfig)
      .then((response) => {
        return response.data;
      })
      .catch((error) => {
        ConsoleHelper(error);
      });
  };

  let overallChartParams;
  let mapChartParams;
  let downtimeChartParams;
  let avgMaintenanceChartParams;
  let assetUtilChartParams = [];
  let clusterChartParams;
  let leaderboardChartParams;
  let stackedClusteredChart;
  let operationalCostParams;
  let assetCheckParams;
  let costPerProcessParams;
  let workOrderCompletionTimeParams;

  const url1 = "api/v1/Chart/Get/Status/Breakdown";
  const [dataReady1, dataArray1, error1] = useRequestedData(url1);
  if (dataReady1) {
    if (error1) {
      ConsoleHelper("errors:", error1);
    }
    const overviewData = !!dataArray1 ? dataArray1 : null;
    const denominator =
      overviewData.active_num +
      overviewData.incident_num +
      overviewData.repairs_num +
      overviewData.maintenance_num;
    overallChartParams = [
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
  }

  const url2 = "api/v1/Chart/Get/Location/Maintenance/Downtime/Average";
  const [dataReady2, dataArray2, error2] = useRequestedData(url2);
  if (dataReady2) {
    if (error2) {
      ConsoleHelper("errors:", error2);
    }
    avgMaintenanceChartParams = dataArray2;
  }

  const url3 = "api/v1/Accident/Downtime/Fleet";
  const [dataReady3, dataArray3, error3] = useRequestedData(url3);
  if (dataReady3) {
    if (error3) {
      ConsoleHelper("errors:", error3);
    }
    const downtimeData = !!dataArray3 ? dataArray3 : null;
    const denominator = downtimeData.non_preventable_hours + downtimeData.preventable_hours;
    downtimeChartParams = [
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
  }

  const url4 = "api/v1/Chart/Get/Process/Breakdown";
  const [dataReady4, dataArray4, error4] = useRequestedData(url4);
  if (dataReady4) {
    if (error4) {
      ConsoleHelper("errors:", error4);
    }
    stackedClusteredChart = dataArray4;
  }

  const url5 = "api/v1/Chart/Get/Location/Count/Operators/Assets";
  const [dataReady5, dataArray5, error5] = useRequestedData(url5);
  if (dataReady5) {
    if (error5) {
      ConsoleHelper("errors:", error5);
    }
    mapChartParams = dataArray5;
  }

  const url6 = "api/v1/Chart/Get/Location/AssetTypes";
  const [dataReady6, dataArray6, error6] = useRequestedData(url6);
  if (dataReady6) {
    if (error6) {
      ConsoleHelper("errors:", error6);
    }
    clusterChartParams = dataArray6;
  }

  const url7 = "api/v1/Chart/Get/Asset/Performance/Leaderboard";
  const [dataReady7, dataArray7, error7] = useRequestedData(url7);
  if (dataReady7) {
    if (error7) {
      ConsoleHelper("errors:", error7);
    }
    leaderboardChartParams = dataArray7;
  }

  const url8 = "api/v1/Chart/Fleet/Usage";
  const [dataReady8, dataArray8, error8] = useRequestedData(url8);
  if (dataReady8) {
    if (error8) {
      ConsoleHelper("errors:", error8);
    }
    dataArray8["Mileage"] &&
      dataArray8["Mileage"][1]["daily_averages"].forEach((datapoint, index) => {
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

  const url9 = "/api/v1/Chart/Get/Operational/Cost";
  const [dataReady9, dataArray9, error9] = useRequestedData(url9);
  if (dataReady9) {
    if (error9) {
      ConsoleHelper("errors:", error9);
    }
    operationalCostParams = dataArray9;
  }

  const url10 = "/api/v1/Chart/Get/dailyChecksAndAssets";
  const [dataReady10, dataArray10, error10] = useRequestedData(url10);
  if (dataReady10) {
    if (error10) {
      ConsoleHelper("errors:", error10);
    }
    assetCheckParams = dataArray10;
  }

  const url11 = "api/v1/Chart/Get/ProcessCostByLocation";
  const [dataReady11, dataArray11, error11] = useRequestedData(url11);
  if (dataReady11) {
    if (error11) {
      ConsoleHelper("errors:", error11);
    }
    costPerProcessParams = dataArray11;
  }

  const url12 = "api/v1/Chart/Get/WorkOrderCompletionTime";
  const [dataReady12, dataArray12, error12] = useRequestedData(url12);
  if (dataReady12) {
    if (error12) {
      ConsoleHelper("errors:", error12);
    }
  }
  workOrderCompletionTimeParams = dataArray12;

  return (
    <div>
      {!isMobile && <DashboardHeader userInfo={userInformation} />}
      {hasModulePermission("fleet_at_a_glance_executive") ? (
        <TabView
          renderActiveOnly={false}
          activeIndex={activeIndex}
          className="custom-tab-corner"
          onTabChange={(e) => {
            setActiveIndex(e.index);
            dispatch({ type: CTRL_AUDIO_PLAY, payload: "main_tab" });
          }}
        >
          <TabPanel header={t("fleetPanel.executive_overview").toUpperCase()}>
            {isMobile && (
              <PanelHeader icon={faChartArea} text={t("fleetPanel.page_title_mobile")} />
            )}
            <div className="row">
              <div
                onClick={() => {
                  setIsEdit((x) => !x);
                  isEdit && saveLayout();
                }}
                data-tip={`${isEdit ? "Save" : "Edit"} your dashboard layout`}
                className={`edit-dashboard ${isEdit ? "save-layout-icon" : "edit-layout-icon"}`}
              />
              <label className="form-tooltip">
                <ReactTooltip place="left" />
              </label>
            </div>
            <ExecutivePanel
              overallChartParams={overallChartParams}
              avgMaintenanceChartParams={avgMaintenanceChartParams}
              downtimeChartParams={downtimeChartParams}
              stackedClusteredChart={stackedClusteredChart}
              operationalCostParams={operationalCostParams}
              mapChartParams={mapChartParams}
              assetUtilChartParams={assetUtilChartParams}
              clusterChartParams={clusterChartParams}
              leaderboardChartParams={leaderboardChartParams}
              costPerProcessParams={costPerProcessParams}
              workOrderCompletionTimeParams={workOrderCompletionTimeParams}
              dataReady={[
                dataReady1,
                dataReady2,
                dataReady3,
                dataReady4,
                dataReady5,
                dataReady8,
                dataReady6,
                dataReady7,
                dataReady9,
                dataReady11,
                dataReady12,
              ]}
              errors={[
                error1,
                error2,
                error3,
                error4,
                error5,
                error8,
                error6,
                error7,
                error9,
                error11,
                error12,
              ]}
              dashboard_layout={exec_layout}
              isEdit={isEdit}
            />
          </TabPanel>
          <TabPanel header={t("fleetPanel.manager_overview").toUpperCase()}>
            {isMobile && (
              <PanelHeader icon={faChartArea} text={t("fleetPanel.page_title_mobile")} />
            )}
            <div className="row">
              <div
                onClick={() => {
                  setIsEdit((x) => !x);
                  isEdit && saveLayout();
                }}
                data-tip={`${isEdit ? "Save" : "Edit"} your dashboard layout`}
                className={`edit-dashboard ${isEdit ? "save-layout-icon" : "edit-layout-icon"}`}
              />
              <label className="form-tooltip">
                <ReactTooltip place="left" />
              </label>
            </div>
            <ManagerPanel
              stackedClusteredChart={stackedClusteredChart}
              mapChartParams={mapChartParams}
              downtimeChartParams={downtimeChartParams}
              clusterChartParams={clusterChartParams}
              assetCheckParams={assetCheckParams}
              dataReady={[dataReady5, dataReady3, dataReady4, dataReady6, dataReady10]}
              errors={[error5, error3, error4, error6, error10]}
              dashboard_layout={mngr_layout}
              isEdit={isEdit}
            />
          </TabPanel>
        </TabView>
      ) : (
        hasModulePermission("fleet_at_a_glance_manager") && (
          <React.Fragment>
            {isMobile && (
              <PanelHeader icon={faChartArea} text={t("fleetPanel.page_title_mobile")} />
            )}
            <div className="row">
              <div
                onClick={() => {
                  setIsEdit((x) => !x);
                  isEdit && saveLayout();
                }}
                data-tip={`${isEdit ? "Save" : "Edit"} your dashboard layout`}
                className={`edit-dashboard ${isEdit ? "save-layout-icon" : "edit-layout-icon"}`}
              />
              <label className="form-tooltip">
                <ReactTooltip place="left" />
              </label>
            </div>
            <ManagerPanel
              stackedClusteredChart={stackedClusteredChart}
              mapChartParams={mapChartParams}
              downtimeChartParams={downtimeChartParams}
              clusterChartParams={clusterChartParams}
              assetCheckParams={assetCheckParams}
              dataReady={[dataReady5, dataReady3, dataReady4, dataReady6, dataReady10]}
              errors={[error5, error3, error4, error6, error10]}
              dashboard_layout={mngr_layout}
              isEdit={isEdit}
            />
          </React.Fragment>
        )
      )}
    </div>
  );
};

export default FleetPanel;
