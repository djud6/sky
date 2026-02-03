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
import { Table } from "../../ShareComponents/Table";
import RepairDetails from "./RepairDetails";
import VINLink from "../../ShareComponents/helpers/VINLink";
import GeneralBadge from "../../ShareComponents/GeneralBadge";
import DateBadge from "../../ShareComponents/helpers/DateBadge";
import robotOn from "../../../images/menu/topbar_menu_robot_on.png";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import "../../../styles/helpers/button2.scss";
import "../../../styles/ShareComponents/helpers/CostContainer.scss";

const CommonRepairsPanel = ({
  category,
  repairs,
  selectedRepair,
  setSelectedRepair,
  dataReady,
  setMoreDetails,
  setDetailsSection,
  setShowChart,
  setRepairRequests,
  setDataReady,
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
    isMobile ? setShowChart(!mobileDetails) : setShowChart(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mobileDetails, isMobile]);

  useEffect(() => {
    if (selectedRepair) {
      setMobileDetails(true);
    }
  }, [selectedRepair]);

  useEffect(() => {
    if (!costSelect && !isMobile) {
      setSelectedRepair(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [costSelect]);

  const handleExport = () => {
    let selectedRequests = [];
    selectedRepair.forEach((repair) => {
      selectedRequests.push(repair.repair_id);
    });

    exportCostCSV(selectedRequests);
  };

  const exportCostCSV = (ids) => {
    let authHeader = getAuthHeader();
    loadingAlert();
    axios({
      url: `${Constants.ENDPOINT_PREFIX}/api/v1/Report/WorkOrder/Cost`,
      method: "post",
      data: { repair_ids: ids },
      responseType: "blob",
      auth: false,
      headers: authHeader.headers,
    })
      .then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `repair-costs-${Date.now()}.csv`);
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

  if (!repairs) return null;

  if (category === "inProgress") {
    TableHeaders = [
      {
        header: t("general.class_code"),
        colFilter: { field: "class_code", filterOptions: { filterAs: "dropdown" } },
      },
      { header: t("general.id"), colFilter: { field: "work_order" } },
      { header: t("general.vin"), colFilter: { field: "VIN" } },
      {
        header: t("general.location"),
        colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("general.vendor"),
        colFilter: { field: "vendor_name", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("repairRequestPanel.urgent_repair_button"),
        colFilter: { field: "is_urgent", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("general.status"),
        colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
      },
      {
        header: t("general.date_created"),
        colFilter: {
          field: "date_created",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },
      {
        header: t("repairRequestPanel.requested_delivery_date_label"),
        colFilter: {
          field: "requested_delivery_date",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },
    ];

    TableData = repairs.map((repair) => {
      repair.current_location = repair.current_location
        ? repair.current_location
        : t("general.not_applicable");
      repair.vendor_name = repair.vendor_name ? repair.vendor_name : t("general.not_applicable");

      return {
        id: repair.repair_id,
        dataPoint: repair,
        cells: [
          repair.class_code || t("general.not_applicable"),
          repair.work_order,
          <VINLink vin={repair.VIN} />,
          repair.current_location,
          repair.vendor_name,
          <GeneralBadge
            data={repair.is_urgent}
            colorTheme={
              repair.is_urgent.toLowerCase() === "yes" ? "badge-danger" : "badge-secondary"
            }
          />,
          capitalize(repair.status),
          ...(moment(repair.date_created).isValid()
            ? [moment(repair.date_created).format("YYYY-MM-DD")]
            : [t("general.not_applicable")]),
          ...(moment(repair.requested_delivery_date).isValid()
            ? [
                <DateBadge
                  currentDate={moment(repair.requested_delivery_date).format("YYYY-MM-DD")}
                  dateRange={8}
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
        header: t("repairsPanelIndex.date_completed"),
        colFilter: {
          field: "date_completed",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },
    ];

    TableData = repairs.map((repair) => {
      repair.current_location = repair.current_location
        ? repair.current_location
        : t("general.not_applicable");
      repair.vendor_name = repair.vendor_name ? repair.vendor_name : t("general.not_applicable");

      return {

        id: repair.repair_id,
        dataPoint: repair,
        cells: [
          repair.work_order,
          <VINLink vin={repair.VIN} />,
          repair.current_location,
          repair.vendor_name,
          capitalize(repair.status),
          moment(repair.date_completed).format("YYYY-MM-DD") || t("general.not_applicable"),
        ],
      };
    });
  }

  return (
    <React.Fragment>
      {isMobile ? (
        <React.Fragment>
          {selectedRepair && mobileDetails ? (
            <div className="p-mb-5">
              <RepairDetails
                repair={selectedRepair}
                setSelectedRepair={setSelectedRepair}
                setMobileDetails={setMobileDetails}
                setMoreDetails={setMoreDetails}
                setDetailsSection={setDetailsSection}
                setRepairRequests={setRepairRequests}
                setDataReady={setDataReady}
                category={category}
              />
            </div>
          ) : (
            <div className="p-mb-5">
              <Table
                dataReady={dataReady}
                tableHeaders={TableHeaders}
                tableData={TableData}
                onSelectionChange={(repair) => setSelectedRepair(repair)}
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
                      !selectedRepair ||
                      (selectedRepair && selectedRepair.length === 0)
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
            onSelectionChange={(repair) => setSelectedRepair(repair)}
            hasSelection
            multipleSelection={costSelect ? true : false}
            globalSearch={costSelect ? false : true}
            tab={tab}
          />
          {selectedRepair && !Array.isArray(selectedRepair) && (
            <RepairDetails
              repair={selectedRepair}
              setSelectedRepair={setSelectedRepair}
              setMobileDetails={setMobileDetails}
              setMoreDetails={setMoreDetails}
              setDetailsSection={setDetailsSection}
              setRepairRequests={setRepairRequests}
              setDataReady={setDataReady}
              category={category}
            />
          )}
        </React.Fragment>
      )}
    </React.Fragment>
  );
};

export default CommonRepairsPanel;
