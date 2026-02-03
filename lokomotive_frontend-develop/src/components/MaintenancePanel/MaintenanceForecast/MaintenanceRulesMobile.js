import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import RulesTable from "./RulesTable";
import AddMaintenanceRuleDialog from "./AddMaintenanceRule";
import { getAuthHeader } from "../../../helpers/Authorization";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button4.scss";
import "../../../styles/helpers/button5.scss";
import "../../../styles/MaintenancePanel/MaintenanceForecast/MaintenanceRulesMobile.scss";

const MaintenanceRulesMobile = ({ maintenanceTypes, setMobilePage }) => {
  const { t } = useTranslation();
  const [vehicle, setVehicle] = useState(null);
  const [listReady, setListReady] = useState(false);
  const [maintenanceRulesList, setMaintenanceRulesList] = useState([]);
  const [selectedRule, setSelectedRule] = useState(null);
  const [updateMode, setUpdateMode] = useState("none");
  const [forceUpdateTable, setForceUpdateTable] = useState(Date.now);

  useEffect(() => {
    if (vehicle) {
      setUpdateMode("none");
      setListReady(false);
      setMaintenanceRulesList([]);
      setSelectedRule(null);
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Forecast/Rule/List/VIN/${vehicle.VIN}`,
          {
            ...getAuthHeader(),
            cancelToken: cancelTokenSource.token,
          }
        )
        .then((response) => {
          setMaintenanceRulesList(response.data);
          setListReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicle, forceUpdateTable]);

  useEffect(() => {
    if(selectedRule) setUpdateMode("update");
  }, [selectedRule]);

  return (
    <div className="maintenance-rule-mobile">
      {updateMode === "none" &&
        <div className="no-style-btn p-mx-3 p-mb-4">
          <Button
            label={t("general.back")}
            className="p-button-link"
            icon="pi pi-chevron-left"
            onClick={() => setMobilePage("main")}
          />
        </div>
      }
      <div className="header-search">
        <VINSearch
          onVehicleSelected={(v) => {
            setSelectedRule(null);
            setMaintenanceRulesList([]);
            setListReady(false);
            setVehicle(v);
          }}
        />
        <div className="title-hint">
          <h5>{t("maintenanceForecastPanel.rules_card_content_1")}</h5>
        </div>
      </div>
      {vehicle ?
        <React.Fragment>
          {updateMode === "none" &&
            <React.Fragment>
              <RulesTable
                rulesList={maintenanceRulesList}
                dataReady={listReady}
                maintenanceTypes={maintenanceTypes}
                setSelectedRule={setSelectedRule}
              />
              <div className="p-d-flex p-jc-center">
                <hr />
              </div>
              <div className="p-d-flex p-jc-center p-mt-3 p-mb-5">
                <div className="btn-5 active-bg add-rule-btn">
                  <Button
                    icon="pi pi-plus"
                    onClick={() => {
                      setUpdateMode("add");
                    }}
                    label={t("maintenanceForecastPanel.creating_new_rule")}
                  />
                </div>
              </div>
            </React.Fragment>
          }
          {updateMode === "update" &&
            <div className="add-rule-dialog">
              <div className="no-style-btn p-mx-2 p-my-3">
                <Button
                  label={t("general.back")}
                  className="p-button-link"
                  icon="pi pi-chevron-left"
                  onClick={() => setUpdateMode("none")}
                />
              </div>
              <AddMaintenanceRuleDialog
                vehicle={vehicle}
                maintenanceTypes={maintenanceTypes && maintenanceTypes}
                rule={selectedRule}
                key={selectedRule.id}
                setDataReady={setListReady}
                setForceUpdateTable={setForceUpdateTable}
              />
            </div>
          }
          {updateMode === "add" &&
            <div className="add-rule-dialog">
              <div className="no-style-btn p-mx-2 p-my-3">
                <Button
                  label={t("general.back")}
                  className="p-button-link"
                  icon="pi pi-chevron-left"
                  onClick={() => setUpdateMode("none")}
                />
              </div>
              <AddMaintenanceRuleDialog
                vehicle={vehicle}
                maintenanceTypes={maintenanceTypes && maintenanceTypes}
                setForceUpdateTable={setForceUpdateTable}
              />
            </div>
          }
        </React.Fragment>
        :
        null
      }
    </div>
  )
}

export default MaintenanceRulesMobile;