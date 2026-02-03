import React, { useState, useEffect } from "react";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { Table } from "../../ShareComponents/Table";
import VINLink from "../../ShareComponents/helpers/VINLink";
import IncidentDetails from "./IncidentDetails";

const CommonIncidentsPanel = ({
  incidents,
  selectedIncident,
  setSelectedIncident,
  dataReady,
  setDataReady,
  setShowChart,
  setIncidents,
  tab,
}) => {
  const { t } = useTranslation();
  const [forceUpdateTable, setForceUpdateTable] = useState(Date.now);
  const [mobileDetails, setMobileDetails] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const incidentType = {
    all: t("general.all"),
    preventable: t("general.preventable"),
    nonpreventable: t("general.non_preventable"),
  };

  useEffect(() => {
    isMobile ? setShowChart(!mobileDetails) : setShowChart(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mobileDetails, isMobile]);

  useEffect(() => {
    if (selectedIncident) {
      setMobileDetails(true);
    }
  }, [selectedIncident]);

  useEffect(() => {
    setSelectedIncident(null);
    setForceUpdateTable(Date.now);
  }, [setSelectedIncident]);

  if (!incidents) return null;

  const incidentItemTemplate = (value) => {
    return value ? incidentType.preventable : incidentType.nonpreventable;
  };

  let unresolvedTableHeaders = [
    { header: t("general.id"), colFilter: { field: "custom_id" } },
    { header: t("general.vin"), colFilter: { field: "VIN" } },
    {
      header: t("general.asset_type"),
      colFilter: { field: "asset_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("incidentsDetails.business_unit_label"),
      colFilter: { field: "business_unit", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.location"),
      colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("incidentsDetails.incident_type_label"),
      colFilter: {
        field: "is_preventable",
        filterOptions: {
          filterAs: "dropdown",
          valueTemplate: incidentItemTemplate,
          itemTemplate: incidentItemTemplate,
        },
      },
    },
    {
      header: t("incidentsDetails.date_reported_label"),
      colFilter: {
        field: "date_created",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
    {
      header: t("incidentsDetails.estimated_return_to_service"),
      colFilter: {
        field: "estimated_return_date",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
  ];
  let unresolvedTableData = incidents.map((incident) => {
    return {
      id: incident.accident_id,
      dataPoint: incident,
      cells: [
        incident.custom_id,
        <VINLink vin={incident.VIN} />,
        incident.asset_type,
        incident.business_unit,
        incident.current_location,
        incident.is_preventable ? incidentType.preventable : incidentType.nonpreventable,
        moment(incident.date_created).format("YYYY-MM-DD"),
        ...(moment(incident.estimated_return_date).isValid()
          ? [moment(incident.estimated_return_date).format("YYYY-MM-DD")]
          : [t("general.not_applicable")]),
      ],
    };
  });

  return (
    <React.Fragment>
      {isMobile ? (
        <React.Fragment>
          {selectedIncident && mobileDetails ? (
            <div className="p-mb-5">
              <IncidentDetails
                incident={selectedIncident}
                setDataReady={setDataReady}
                setSelectedIncident={setSelectedIncident}
                setMobileDetails={setMobileDetails}
                setIncidents={setIncidents}
              />
            </div>
          ) : (
            <div className="p-mb-5">
              <Table
                key={forceUpdateTable}
                dataReady={dataReady}
                tableHeaders={unresolvedTableHeaders}
                tableData={unresolvedTableData}
                onSelectionChange={(incident) => setSelectedIncident(incident)}
                hasSelection
                tab={tab}
              />
            </div>
          )}
        </React.Fragment>
      ) : (
        <React.Fragment>
          <Table
            key={forceUpdateTable}
            dataReady={dataReady}
            tableHeaders={unresolvedTableHeaders}
            tableData={unresolvedTableData}
            onSelectionChange={(incident) => setSelectedIncident(incident)}
            hasSelection
            hasExport
            tab={tab}
          />
          {selectedIncident && (
            <IncidentDetails
              incident={selectedIncident}
              setDataReady={setDataReady}
              setSelectedIncident={setSelectedIncident}
              setMobileDetails={setMobileDetails}
              setIncidents={setIncidents}
            />
          )}
        </React.Fragment>
      )}
    </React.Fragment>
  );
};

export default CommonIncidentsPanel;
