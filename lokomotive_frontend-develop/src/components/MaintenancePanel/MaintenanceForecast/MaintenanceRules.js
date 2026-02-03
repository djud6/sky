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
import "../../../styles/MaintenancePanel/MaintenanceForecast/MaintenanceRules.scss";

const MaintenanceRules = ({ maintenanceTypes }) => {
  const { t } = useTranslation();
  const [vehicle, setVehicle] = useState(null);
  const [listReady, setListReady] = useState(false);
  const [maintenanceRulesList, setMaintenanceRulesList] = useState([]);
  const [selectedRule, setSelectedRule] = useState(null);
  const [onChangeRule, setOnChangeRule] = useState(false);
  const [updateMode, setUpdateMode] = useState("add");
  const [forceUpdateTable, setForceUpdateTable] = useState(Date.now);

  useEffect(() => {
    if (vehicle) {
      setListReady(false);
      setMaintenanceRulesList([]);
      setSelectedRule(null);
      setOnChangeRule(false);
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

  return (
    <div className="maintenance-rule">
      <div className="title-hint">
        <h5>{t("maintenanceForecastPanel.rules_card_content_1")}</h5>
      </div>
      {!onChangeRule ?
        <React.Fragment>
          <div className="p-mt-4">
            <VINSearch
              onVehicleSelected={(v) => {
                setSelectedRule(null);
                setMaintenanceRulesList([]);
                setListReady(false);
                setVehicle(v);
              }}
            />
          </div>
          {vehicle && (
            <React.Fragment>
              <div className="table-title p-mx-5 p-mt-5">
                <h5>{t("maintenanceSchedulePanel.table_title", {vin: vehicle.VIN})}</h5>
              </div>
              <RulesTable
                rulesList={maintenanceRulesList}
                dataReady={listReady}
                maintenanceTypes={maintenanceTypes}
                setSelectedRule={setSelectedRule}
              />
              <div className="p-d-flex p-jc-center p-my-5">
                <div className="btn-5 p-mx-3">
                  <Button
                    icon="pi pi-refresh"
                    onClick={() => {
                      setUpdateMode("update");
                      setOnChangeRule(true);
                    }}
                    label={t("maintenanceForecastPanel.editing_existing_rule")}
                    disabled={!selectedRule}
                  />
                </div>
                <div className="btn-5 active-bg p-mx-3">
                  <Button
                    icon="pi pi-plus"
                    onClick={() => {
                      setUpdateMode("add");
                      setOnChangeRule(true);
                    }}
                    label={t("maintenanceForecastPanel.creating_new_rule")}
                  />
                </div>
              </div>
            </React.Fragment>
          )}
        </React.Fragment>
        :
        <div className="p-d-flex p-jc-center w-100">
          <div className="form-wrapper">
            <div className="no-style-btn p-my-3">
              <Button
                label={t("general.back")}
                className="p-button-link"
                icon="pi pi-chevron-left"
                onClick={() => {
                  setSelectedRule(null);
                  setOnChangeRule(false);
                }}
              />
            </div>
            {updateMode === "add" &&
              <div>
                <AddMaintenanceRuleDialog
                  vehicle={vehicle}
                  maintenanceTypes={maintenanceTypes && maintenanceTypes}
                  setForceUpdateTable={setForceUpdateTable}
                />
              </div>
            }
            {updateMode === "update" &&
              <div>
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
          </div>
        </div>
      }
    </div>
  )
}

export default MaintenanceRules;