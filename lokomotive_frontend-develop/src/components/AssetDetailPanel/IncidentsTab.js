import React, { useEffect, useState } from "react";
import axios from "axios";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { getAuthHeader } from "../../helpers/Authorization";
import * as Constants from "../../constants";
import Danger from "../../components/ShareComponents/helpers/Danger";
import Success from "../../components/ShareComponents/helpers/Success";
import Table from "../ShareComponents/Table/Table";
import IncidentDetails from "../IncidentsPanel/IncidentReports/IncidentDetails";
import ConsoleHelper from "../../helpers/ConsoleHelper";

const IncidentsTab = ({ vin, mobileDetails, setMobileDetails }) => {
  const { t } = useTranslation();
  const [incidents, setIncidents] = useState([]);
  const [dataReady, setDataReady] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    setSelectedIncident(null);
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Accident/VIN/${vin}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        setIncidents(response.data);
        setDataReady(true);
      })
      .catch((error) => {
        ConsoleHelper(error);
      });
    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [vin, dataReady]);

  useEffect(() => {
    if (selectedIncident && isMobile) setMobileDetails(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedIncident]);

  const convertStringBoolean = (value) => {
    return typeof value === "string" ? value === "true" : Boolean(value);
  };

  const equipmentFailureItemTemplate = (value) => {
    return convertStringBoolean(value) ? (
      <Danger>{t("general.yes")}</Danger>
    ) : (
      <Success>{t("general.no")}</Success>
    );
  };
  const evaluationItemTemplate = (value) => {
    return convertStringBoolean(value) ? t("general.yes") : t("general.no");
  };
  const resolvedItemTemplate = (value) => {
    return convertStringBoolean(value) ? (
      <Success>{t("general.yes")}</Success>
    ) : (
      <Danger>{t("general.no")}</Danger>
    );
  };

  //Preparing table data
  let tableHeaders = [
    {
      header: t("general.id"),
      colFilter: { field: "custom_id" },
    },
    {
      header: t("assetDetailPanel.date_created"),
      colFilter: {
        field: "date_created",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
    {
      header: t("assetDetailPanel.date_modified"),
      colFilter: {
        field: "date_modified",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
    {
      header: t("assetDetailPanel.equipment_failure"),
      colFilter: {
        field: "is_equipment_failure",
        filterOptions: {
          filterAs: "dropdown",
          valueTemplate: equipmentFailureItemTemplate,
          itemTemplate: equipmentFailureItemTemplate,
        },
      },
    },
    {
      header: t("assetDetailPanel.evaluation_required"),
      colFilter: {
        field: "evaluation_required",
        filterOptions: {
          filterAs: "dropdown",
          valueTemplate: evaluationItemTemplate,
          itemTemplate: evaluationItemTemplate,
        },
      },
    },
    {
      header: t("general.resolved"),
      colFilter: {
        field: "is_resolved",
        filterOptions: {
          filterAs: "dropdown",
          valueTemplate: resolvedItemTemplate,
          itemTemplate: resolvedItemTemplate,
        },
      },
    },
  ];

  let tableData = null;

  if (!!incidents) {
    tableData = incidents.map((incident) => {
      return {
        id: incident.accident_id,
        dataPoint: incident,
        cells: [
          incident.custom_id,
          moment(incident.date_created).format("YYYY-MM-DD"),
          moment(incident.date_modified).format("YYYY-MM-DD"),
          equipmentFailureItemTemplate(incident.is_equipment_failure),
          evaluationItemTemplate(incident.evaluation_required),
          resolvedItemTemplate(incident.is_resolved),
        ],
      };
    });
  }

  return (
    <div className={`${!isMobile ? "p-mt-5" : "p-mt-3"}`}>
      {isMobile ? (
        <React.Fragment>
          {selectedIncident && mobileDetails ? (
            <IncidentDetails
              incident={selectedIncident}
              setDataReady={setDataReady}
              setSelectedIncident={setSelectedIncident}
              setMobileDetails={setMobileDetails}
              disableButtons
            />
          ) : (
            <div className="p-mb-5">
              <h5 className="p-mb-3">{t("assetDetailPanel.incident_history")}</h5>
              <div className="darkTable section-table">
                <Table
                  tableHeaders={tableHeaders}
                  tableData={tableData}
                  dataReady={dataReady}
                  onSelectionChange={(item) => setSelectedIncident(item)}
                  hasSelection
                  rows={5}
                />
              </div>
            </div>
          )}
        </React.Fragment>
      ) : (
        <React.Fragment>
          <h5 className="p-mb-3">{t("assetDetailPanel.incident_history")}</h5>
          <div className="darkTable section-table">
            <Table
              tableHeaders={tableHeaders}
              tableData={tableData}
              dataReady={dataReady}
              onSelectionChange={(item) => setSelectedIncident(item)}
              hasSelection
              rows={5}
            />
          </div>
          {selectedIncident && (
            <IncidentDetails
              incident={selectedIncident}
              setSelectedIncident={setSelectedIncident}
              setDataReady={setDataReady}
              disableButtons
            />
          )}
        </React.Fragment>
      )}
    </div>
  );
};

export default IncidentsTab;
