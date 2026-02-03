import React, { useState, useEffect } from "react";
import axios from "axios";
import moment from "moment";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { capitalize } from "../../../helpers/helperFunctions";
import { getAuthHeader } from "../../../helpers/Authorization";
import MaintenanceDetails from "./MaintenanceDetails";
import { Table } from "../../ShareComponents/Table";
import VINLink from "../../ShareComponents/helpers/VINLink";
import DateBadge from "../../ShareComponents/helpers/DateBadge";
import robotOn from "../../../images/menu/topbar_menu_robot_on.png";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import "../../../styles/helpers/button2.scss";
import "../../../styles/ShareComponents/helpers/CostContainer.scss";

const CommomMaintenancePanel = ({
  category,
  maintenances,
  selectedMaintenance,
  setSelectedMaintenance,
  dataReady,
  setMoreDetails,
  setDetailsSection,
  setMaintenances,
  setDataReady,
  maintenanceType,
  tab,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [mobileDetails, setMobileDetails] = useState(false);
  const [costSelect, setCostSelect] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  let TableHeaders = [];
  let TableData = {};

  useEffect(() => {
    if (selectedMaintenance) {
      setMobileDetails(true);
    }
  }, [selectedMaintenance]);

  useEffect(() => {
    if (!costSelect && !isMobile) {
      setSelectedMaintenance(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [costSelect]);

  const handleExport = () => {
    let selectedRequests = [];
    selectedMaintenance.forEach((maintenance) => {
      selectedRequests.push(maintenance.maintenance_id);
    });

    exportCostCSV(selectedRequests);
  };

  const exportCostCSV = (ids) => {
    let authHeader = getAuthHeader();
    loadingAlert();
    axios({
      url: `${Constants.ENDPOINT_PREFIX}/api/v1/Report/WorkOrder/Cost`,
      method: "post",
      data: { maintenance_ids: ids },
      responseType: "blob",
      auth: false,
      headers: authHeader.headers,
    })
      .then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `maintenance-costs-${Date.now()}.csv`);
        document.body.appendChild(link);
        link.click();
        setCostSelect(false);
        successAlert("msg", t("exportCostIndex.export_success_msg"));
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  if (!maintenances) return null;

  if (category === "outstanding") {
    TableHeaders = [
      { header: t("general.id"), colFilter: { field: "work_order" } },
      { header: t("general.vin"), colFilter: { field: "VIN" } },
      {
        header: t("general.asset_type"),
        colFilter: { field: "asset_type", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("general.inspection_type"),
        colFilter: { field: "inspection_type", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("general.status"),
        colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("general.location"),
        colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("general.vendor"),
        colFilter: { field: "vendor_name", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("maintenancePanelIndex.expected_delivery_date"),
        colFilter: {
          field: "requested_delivery_date",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },
    ];
    TableData = maintenances.map((maintenance) => {
      maintenance.asset_type = maintenance.asset_type
        ? maintenance.asset_type
        : t("general.not_applicable");
      maintenance.current_location = maintenance.current_location
        ? maintenance.current_location
        : t("general.not_applicable");
      maintenance.vendor_name = maintenance.vendor_name
        ? maintenance.vendor_name
        : t("general.not_applicable");

      return {
        id: maintenance.maintenance_id,
        dataPoint: maintenance,
        cells: [
          maintenance.work_order,
          <VINLink vin={maintenance.VIN} />,
          maintenance.asset_type,
          maintenance.inspection_type,
          capitalize(maintenance.status),
          maintenance.current_location,
          maintenance.vendor_name,
          ...(moment(maintenance.requested_delivery_date).isValid()
            ? [
                <DateBadge
                  currentDate={moment(maintenance.requested_delivery_date).format("YYYY-MM-DD")}
                  dateRange={2}
                />,
              ]
            : [t("general.not_applicable")]),
        ],
      };
    });
  } else if (category === "completed") {
    TableHeaders = [
      { header: t("general.id"), colFilter: { field: "work_order" } },
      { header: t("general.vin"), colFilter: { field: "VIN" } },
      {
        header: t("general.asset_type"),
        colFilter: { field: "asset_type", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("general.location"),
        colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("general.vendor"),
        colFilter: { field: "vendor_name", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("general.status"),
        colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("maintenancePanelIndex.date_completed"),
        colFilter: {
          field: "date_completed",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },
    ];
    TableData = maintenances.map((maintenance) => {
      maintenance.asset_type = maintenance.asset_type
        ? maintenance.asset_type
        : t("general.not_applicable");
      maintenance.current_location = maintenance.current_location
        ? maintenance.current_location
        : t("general.not_applicable");
      maintenance.vendor_name = maintenance.vendor_name
        ? maintenance.vendor_name
        : t("general.not_applicable");

      return {
        id: maintenance.maintenance_id,
        dataPoint: maintenance,
        cells: [
          maintenance.work_order,
          <VINLink vin={maintenance.VIN} />,
          maintenance.asset_type || t("general.not_applicable"),
          maintenance.current_location || t("general.not_applicable"),
          maintenance.vendor_name || t("general.not_applicable"),
          capitalize(maintenance.status),
          moment(maintenance.date_completed).format("YYYY-MM-DD") || t("general.not_applicable"),
        ],
      };
    });
  }

  return (
    <React.Fragment>
      {isMobile ? (
        <React.Fragment>
          {selectedMaintenance && mobileDetails ? (
            <div className="p-mb-5">
              <MaintenanceDetails
                maintenance={selectedMaintenance}
                setSelectedMaintenance={setSelectedMaintenance}
                setMobileDetails={setMobileDetails}
                setMoreDetails={setMoreDetails}
                setDetailsSection={setDetailsSection}
                setMaintenances={setMaintenances}
                setDataReady={setDataReady}
                maintenanceType={maintenanceType}
              />
            </div>
          ) : (
            <div className="p-mb-5">
              <Table
                dataReady={dataReady}
                tableHeaders={TableHeaders}
                tableData={TableData}
                onSelectionChange={(maintenance) => setSelectedMaintenance(maintenance)}
                hasSelection
                tab={tab}
              />
            </div>
          )}
        </React.Fragment>
      ) : (
        <React.Fragment>
          <div className="export-cost-container">
            <div className="p-d-flex p-jc-end btns-container">
              {costSelect && (
                <div className={`btn-2 p-mr-3 export-btn-color`}>
                  <Button
                    icon="pi pi-upload"
                    label={t("exportCostIndex.export_btn")}
                    tooltip={t("exportCostIndex.export_tooltip")}
                    tooltipOptions={{ position: "top" }}
                    onClick={() => handleExport()}
                    disabled={
                      !dataReady ||
                      !selectedMaintenance ||
                      (selectedMaintenance && selectedMaintenance.length === 0)
                    }
                  />
                </div>
              )}
              <div className={`btn-2 ${costSelect ? "cancel-btn-color" : ""}`}>
                <Button
                  icon={costSelect ? "pi pi-times-circle" : "pi pi-upload"}
                  label={
                    costSelect
                      ? t("exportCostIndex.export_cancel_btn")
                      : t("exportCostIndex.export_btn")
                  }
                  tooltip={
                    costSelect
                      ? t("exportCostIndex.export_cancel_tooltip")
                      : t("exportCostIndex.export_tooltip")
                  }
                  tooltipOptions={{ position: "top" }}
                  onClick={() => setCostSelect(!costSelect)}
                  disabled={!dataReady}
                />
              </div>
            </div>
            {costSelect && (
              <div className="p-d-flex p-jc-center p-mt-2 p-mb-5">
                <div className="export-assistant">
                  <img src={robotOn} alt="" />
                </div>
                <div className="export-helper">{t("exportCostIndex.export_helper")}</div>
              </div>
            )}
          </div>
          <Table
            dataReady={dataReady}
            tableHeaders={TableHeaders}
            tableData={TableData}
            onSelectionChange={(maintenance) => {
              setSelectedMaintenance(maintenance);
            }}
            hasSelection
            multipleSelection={costSelect ? true : false}
            globalSearch={costSelect ? false : true}
            tab={tab}
          />
          {selectedMaintenance && !Array.isArray(selectedMaintenance) && (
            <MaintenanceDetails
              maintenance={selectedMaintenance}
              setSelectedMaintenance={setSelectedMaintenance}
              setMoreDetails={setMoreDetails}
              setDetailsSection={setDetailsSection}
              setMaintenances={setMaintenances}
              setDataReady={setDataReady}
              maintenanceType={maintenanceType}
            />
          )}
        </React.Fragment>
      )}
    </React.Fragment>
  );
};

export default CommomMaintenancePanel;
