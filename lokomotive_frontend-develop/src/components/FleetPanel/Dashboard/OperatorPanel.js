import React from "react";
import { useSelector } from "react-redux";
import { useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import DashboardHeader from "./DashboardHeader";
import opCheckImg from "../../../images/background/op_daily_checks.png";
import opIncidentImg from "../../../images/background/op_incidents.png";
import opIssueImg from "../../../images/background/op_issues.png";
import "../../../styles/helpers/button3.scss";
import "../../../styles/FleetPanel/dashboard.scss";
import "../../../styles/FleetPanel/OperatorPanel.scss";

const OperatorPanel = () => {
  const history = useHistory();
  const { t } = useTranslation();
  const { userInfo } = useSelector((state) => state.apiCallData);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const userInformation = {
    first_name: userInfo.user.first_name,
    role: userInfo.detailed_user.role_permissions.role,
  };

  const onChangePage = (url) => {
    history.push(url);
  };

  return (
    <div>
      {!isMobile ? (
        <DashboardHeader userInfo={userInformation} isOperator />
      ) : (
        <div className="op-mobile-header">
          <div className="subheader-1">
            {t("fleetPanel.welcome_back_userInfo_name", {
              userInfo_name: userInformation.first_name,
            })}
          </div>
          <div className="subheader-2">{t("operator_dashboard.greeting_msg")}</div>
        </div>
      )}
      <div className="operator-panel p-d-flex p-jc-around p-flex-wrap">
        <div className="access-container img-checks" onClick={() => onChangePage("/operators")}>
          <div className="container-text">
            <div>Daily</div>
            <div>Check</div>
          </div>
          <div className="footer-btn">
            <div className="indicator-img">
              <img src={opCheckImg} alt="op-check-img" />
            </div>
            <div className="p-m-3">
              <Button
                icon="pi pi-angle-right"
                iconPos="right"
                onClick={() => onChangePage("/operators")}
              />
            </div>
          </div>
        </div>
        <div
          className="access-container img-incident"
          onClick={() => onChangePage("/incidents/new")}
        >
          <div className="container-text">
            <div>Report</div>
            <div>Incident</div>
          </div>
          <div className="footer-btn">
            <div className="indicator-img">
              <img src={opIncidentImg} alt="op-check-img" />
            </div>
            <div className="p-m-3">
              <Button
                icon="pi pi-angle-right"
                iconPos="right"
                onClick={() => onChangePage("/incidents/new")}
              />
            </div>
          </div>
        </div>
        <div className="access-container img-issue" onClick={() => onChangePage("/issues/new")}>
          <div className="container-text">
            <div>Report</div>
            <div>Issue</div>
          </div>
          <div className="footer-btn">
            <div className="indicator-img">
              <img src={opIssueImg} alt="op-check-img" />
            </div>
            <div className="p-m-3">
              <Button
                icon="pi pi-angle-right"
                iconPos="right"
                onClick={() => onChangePage("/issues/new")}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OperatorPanel;
