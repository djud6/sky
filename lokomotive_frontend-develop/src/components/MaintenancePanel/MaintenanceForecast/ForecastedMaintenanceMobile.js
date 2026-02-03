import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import MaintenanceTable from "./MaintenanceTable";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import DatePicker from "../../ShareComponents/DatePicker";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import CardWidget from "../../ShareComponents/CardWidget";
import { getAuthHeader } from "../../../helpers/Authorization";
import { toPythonDate } from "../../../helpers/getPythonDate";
import "../../../styles/helpers/button5.scss";
import "../../../styles/MaintenancePanel/MaintenanceForecast/ForecastedMaintenanceMobile.scss";

const ForecastedMaintenanceMobile = ({ setMobilePage, maintenanceList, dataReady }) => {
  const { t } = useTranslation();
  const [selectedMaintenanceType, setSelectedMaintenanceType] = useState(null);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [assetList, setAssetList] = useState([]);
  const [tableDataReady, setTableDataReady] = useState(false);
  const [selectedMaintenance, setSelectedMaintenance] = useState([]);

  useEffect(() => {
    if (!!selectedMaintenanceType && !!startDate && !!endDate) {
      setTableDataReady(false);
      setSelectedMaintenance([]);
      setAssetList([]);
      const data = {
        inspection_type_id: selectedMaintenanceType.id,
        start_date: toPythonDate(startDate),
        end_date: toPythonDate(endDate),
      };
      const headers = getAuthHeader();
      headers.headers["Content-Type"] = "application/json";
      const config = {
        method: "post",
        url: `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Forecast/Rule/Daterange`,
        ...headers,
        data: data,
      };
      axios(config)
        .then(function (response) {
          setTableDataReady(true);
          setAssetList(response.data.in_range_assets);
        })
        .catch(function (error) {
          ConsoleHelper(error);
        });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(selectedMaintenanceType), JSON.stringify(startDate), JSON.stringify(endDate)]);

  const selectType = (id) => {
    let selected = maintenanceList.find((v) => v.id === parseInt(id));
    setSelectedMaintenanceType(selected);
  };

  return (
    <div className="forecasted-maintenance-mobile p-mx-3">
      <div className="no-style-btn p-my-3">
        <Button
          label={t("general.back")}
          className="p-button-link"
          icon="pi pi-chevron-left"
          onClick={() => setMobilePage("main")}
        />
      </div>
      <div className="title-hint">
        <h6>{t("maintenanceForecastPanel.forecast_card_header")}</h6>
      </div>
      <div className="search-bar-container">
        <CardWidget status={selectedMaintenanceType}>
          <label className="h6">{t("maintenanceForecastPanel.maintenance_type")}</label>
          <div className="w-100">
            <FormDropdown
              onChange={selectType}
              options={
                maintenanceList &&
                maintenanceList.map((type) => ({
                  name: `Check ${type.inspection_name}`,
                  code: type.id,
                }))
              }
              loading={!dataReady}
              disabled={!dataReady}
              dataReady={dataReady}
              plain_dropdown
            />
          </div>
        </CardWidget>
        <CardWidget status={startDate}>
          <label className="h6">{t("general.from")}</label>
          <DatePicker onChange={setStartDate} initialDate={startDate} />
        </CardWidget>
        <CardWidget status={endDate}>
          <label className="h6">{t("general.to")}</label>
          <DatePicker
            onChange={setEndDate}
            initialDate={endDate}
            minDate={startDate || new Date()}
          />
        </CardWidget>
      </div>
      <hr />
      {selectedMaintenance.length > 0 && (
        <div className="btn-5 p-d-flex p-jc-center p-mt-5 schedule-btn">
          <Link
            to={{
              pathname: `/maintenance/schedule/`,
              query: {
                vehicles: selectedMaintenance,
                maintenanceType: selectedMaintenanceType.id,
                maintenanceTypes: maintenanceList,
              },
            }}
          >
            <Button
              icon="pi pi-plus"
              label={t("maintenanceForecastPanel.create_preventative_maintenance_btn")}
            />
          </Link>
        </div>
      )}
      {!!selectedMaintenanceType &&
        !!startDate &&
        !!endDate &&
        (assetList.length > 0 || !tableDataReady) && (
          <MaintenanceTable
            maintenanceList={assetList}
            dataReady={tableDataReady}
            setSelectedMaintenance={(item) => setSelectedMaintenance(item)}
          />
        )}
      {!!selectedMaintenanceType &&
        !!startDate &&
        !!endDate &&
        assetList.length === 0 &&
        tableDataReady && (
          <div className="text-center p-mt-5">
            <h2 className="text-white font-weight-bold">
              {t("maintenanceForecastPanel.no_matching_vehicles_found")}
            </h2>
          </div>
        )}
    </div>
  );
};

export default ForecastedMaintenanceMobile;
