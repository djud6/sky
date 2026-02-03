import React, { useState, useEffect } from "react";
import axios from "axios";
import swal from "sweetalert";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { useHistory, useLocation } from "react-router-dom";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { faCarCrash } from "@fortawesome/free-solid-svg-icons";
import { getAuthHeader, getRolePermissions } from "../../../helpers/Authorization";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import { loadingAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import IncidentReportForm from "./IncidentReportForm";
import ConsoleHelper from "../../../helpers/ConsoleHelper";

const ReportIncidentPanel = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const history = useHistory();
  const location = useLocation();
  const [isOperator, setIsOperator] = useState(false);
  const [vehicle, setVehicle] = useState(null);
  const [forceUpdateKey, setForceUpdateKey] = useState(Date.now);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    const rolePermissions = getRolePermissions();
    if (rolePermissions.role.toLowerCase() === "operator") setIsOperator(true);
  }, []);

  if (!vehicle && location.query) {
    setVehicle(location.query.vehicle);
  }

  const sendIncidentReport = (incidentReport) => {
    loadingAlert();
    const headers = getAuthHeader();
    headers.headers["Content-Type"] = "application/json";
    const requestConfig = {
      method: "post",
      url: `${Constants.ENDPOINT_PREFIX}/api/v1/Accident/Add`,
      ...headers,
      data: incidentReport,
    };
    axios(requestConfig)
      .then((res) => {
        successAlert();
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  const successAlert = () => {
    return swal({
      title: t("general.success"),
      text: t("reportIncidentPanel.success_alert_text"),
      icon: "success",
      buttons: { return: t("general.return"), new: t("general.new_request") },
    }).then((value) => {
      switch (value) {
        case "return":
          history.push("/incidents");
          break;
        case "new":
          setVehicle(null);
          setForceUpdateKey(Date.now);
          break;
        default:
          setVehicle(null);
          setForceUpdateKey(Date.now);
      }
    });
  };

  return (
    <div>
      {isMobile && !isOperator && (
        <QuickAccessTabs
          tabs={["Incident Reports", "New Incident"]}
          activeTab={"New Incident"}
          urls={["/incidents", "/incidents/new"]}
        />
      )}
      <PanelHeader icon={faCarCrash} text={t("reportIncidentPanel.report_new_incident")} />
      {!isMobile && !isOperator && (
        <QuickAccessTabs
          tabs={["Incident Reports", "New Incident"]}
          activeTab={"New Incident"}
          urls={["/incidents", "/incidents/new"]}
        />
      )}
      <div className={`${isMobile ? "p-pb-4" : "p-mt-5"}`}>
        <VINSearch
          key={forceUpdateKey}
          defaultValue={`${!vehicle && location.state ? location.state.vehicle.VIN : ""}`}
          onVehicleSelected={(v) => {
            setVehicle(v);
          }}
        />
      </div>
      {vehicle && !Array.isArray(vehicle) && (
        <div className="p-mx-3">
          <IncidentReportForm
            vehicle={vehicle}
            title={t("reportIncidentPanel.report_incident_for_vehicle_vin", {
              vehicle_vin: vehicle.VIN,
            })}
            sendIncidentReport={sendIncidentReport}
          />
        </div>
      )}
    </div>
  );
};

export default ReportIncidentPanel;
