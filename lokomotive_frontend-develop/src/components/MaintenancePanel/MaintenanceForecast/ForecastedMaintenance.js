import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import * as Constants from "../../../constants";
import MaintenanceTable from "./MaintenanceTable";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import DatePicker from "../../ShareComponents/DatePicker";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import { getAuthHeader } from "../../../helpers/Authorization";
import { toPythonDate } from "../../../helpers/getPythonDate";
import "../../../styles/tooltipStyles.scss";
import "../../../styles/helpers/button2.scss";
import "../../../styles/helpers/button5.scss";
import "../../../styles/MaintenancePanel/MaintenanceForecast/ForecastedMaintenance.scss";

import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";

const ForecastedMaintenance = ({ maintenanceList, dataReady }) => {
  const { t } = useTranslation();
  const [selectedMaintenanceType, setSelectedMaintenanceType] = useState(null);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [assetList, setAssetList] = useState([]);
  const [calendarDialog, setCalendatDialog] = useState(false);
  const [tableDataReady, setTableDataReady] = useState(false);
  const [selectedMaintenance, setSelectedMaintenance] = useState([]);
  const [pmEvents, setpmEvents] = useState([]);

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
          const tempDates = response.data.in_range_assets.map((maintenance, index) => {
            const data = {
              id: index,
              title: `${maintenance.VIN}`,
              start: maintenance.maintenance_due_date.split("T")[0],
            };
            return data;
          });
          setAssetList(response.data.in_range_assets);
          setpmEvents(tempDates);
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
    <div className="forecasted-maintenance">
      <div className="title-hint">
        <h5>{t("maintenanceForecastPanel.forecast_card_header")}</h5>
      </div>
      <div className="row search-bar-container">
        <div className="col-md-12 col-lg-6 p-d-flex p-ai-center form-mtype p-my-2">
          <div className="m-type-title form-tooltip">
            <span className="p-d-flex p-flex-row">
              {t("maintenanceForecastPanel.maintenance_type")}
              <Tooltip
                label={"m-type-tooltip"}
                description={t("maintenanceForecastPanel.tooltip_type_select")}
              />
            </span>
          </div>
          <FormDropdown
            className="w-100"
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
        <div className="col-md-6 col-lg-3 p-d-flex p-ai-center form-select-date p-my-2">
          <div className="select-date-title form-tooltip">
            <span className="p-d-flex p-flex-row">
              {t("general.from")}
              <Tooltip
                label={"start-date-tooltip"}
                description={t("maintenanceForecastPanel.tooltip_date_start")}
              />
            </span>
          </div>
          <DatePicker onChange={setStartDate} initialDate={startDate} minDate={new Date()} />
        </div>
        <div className="col-md-6 col-lg-3 p-d-flex p-ai-center form-select-date p-my-2">
          <div className="select-date-title form-tooltip">
            <span className="p-d-flex p-flex-row">
              {t("general.to")}
              <Tooltip
                label={"end-date-tooltip"}
                description={t("maintenanceForecastPanel.tooltip_date_end")}
              />
            </span>
          </div>
          <DatePicker
            onChange={setEndDate}
            initialDate={endDate}
            minDate={startDate || new Date()}
          />
        </div>
      </div>

      {!!selectedMaintenanceType &&
        !!startDate &&
        !!endDate &&
        (assetList.length > 0 || !tableDataReady) && (
          <React.Fragment>
            <div className="p-d-flex p-jc-end p-mr-3 p-mb-3 btn-1">
              <Button
                className="p-button-rounded"
                label={"Show on Calendar"}
                icon="pi pi-calendar-plus"
                onClick={() => setCalendatDialog(true)}
              />
            </div>
            <MaintenanceTable
              maintenanceList={assetList}
              dataReady={tableDataReady}
              setSelectedMaintenance={(item) => setSelectedMaintenance(item)}
            />
          </React.Fragment>
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
      {selectedMaintenance.length > 0 && (
        <div className="btn-5 p-d-flex p-jc-center p-mt-5 schedule-btn">
          <Link
            to={{
              pathname: `/maintenance/schedule`,
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
      <Dialog
        className="custom-main-dialog pm-calendar-dialog"
        baseZIndex={1000}
        header={
          selectedMaintenanceType &&
          `Maintenance (Check ${selectedMaintenanceType.inspection_name}) Due Dates`
        }
        visible={calendarDialog}
        footer={<></>}
        onHide={() => setCalendatDialog(false)}
        style={{ width: "80vw" }}
        setCalendatDialogbreakpoints={{ "960px": "95vw" }}
      >
        <div className="calendar-wrapper">
          <FullCalendar
            style={{ width: "100%" }}
            plugins={[dayGridPlugin]}
            initialView="dayGridMonth"
            events={pmEvents}
            initialDate={new Date()}
            selectable
            dayMaxEvents
          />
        </div>
      </Dialog>
    </div>
  );
};

export default ForecastedMaintenance;
