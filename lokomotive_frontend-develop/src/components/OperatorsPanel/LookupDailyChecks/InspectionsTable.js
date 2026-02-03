import React, { useState, useEffect } from "react";
import axios from "axios";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import DailyCheckDetails from "./DailyCheckDetails";
import Table from "../../ShareComponents/Table/Table";
import VINLink from "../../ShareComponents/helpers/VINLink";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/ShareComponents/Table/table.scss";

const InspectionsTable = ({ vehicle }) => {
  const [dataReady, setDataReady] = useState(false);
  const [inspections, setInspections] = useState(null);
  const [selectedInspection, setSelectedInspection] = useState(null);
  const [mobileDetails, setMobileDetails] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const { t } = useTranslation();

  useEffect(() => {
    if (selectedInspection) {
      setMobileDetails(true);
    }
  }, [selectedInspection]);

  useEffect(() => {
    if (vehicle) {
      setSelectedInspection(null);
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/DailyOperationalChecks/VIN/${vehicle.VIN}`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          const inspections = response.data;
          for (var i in inspections) {
            inspections[i].current_location = vehicle.current_location;
          }
          setInspections(inspections);
          setDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    } else {
      setInspections(null);
      setDataReady(false);
    }
  }, [vehicle]);

  if (!inspections) return null;

  const statusType = {
    all: t("general.all"),
    operable: t("lookupDailyCheckPanel.op"),
    inopoperable: t("lookupDailyCheckPanel.inop"),
  };

  const statusItemTemplate = (value) => {
    return !value ? statusType.operable : statusType.inopoperable;
  };

  let tableHeaderTitles = [
    { header: t("general.id"), colFilter: { field: "custom_id" } },
    { header: t("lookupDailyCheckPanel.vin_label"), colFilter: { field: "VIN" } },
    {
      header: t("lookupDailyCheckPanel.asset_type_label"),
      colFilter: { field: "asset_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("lookupDailyCheckPanel.operator_label"),
      colFilter: { field: "created_by", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("lookupDailyCheckPanel.location_label"),
      colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("lookupDailyCheckPanel.date_completed_label"),
      colFilter: {
        field: "date_created",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
    {
      header: t("lookupDailyCheckPanel.status_label"),
      colFilter: {
        field: "is_tagout",
        filterOptions: {
          filterAs: "dropdown",
          valueTemplate: statusItemTemplate,
          itemTemplate: statusItemTemplate,
        },
      },
    },
    {
      header: t("general.modified_by"),
      colFilter: { field: "modified_by", filterOptions: { filterAs: "dropdown" } },
    },
  ];

  let tableData = inspections.map((inspection) => {
    return {
      id: inspection.daily_check_id,
      dataPoint: inspection,
      cells: [
        inspection.custom_id,
        <VINLink vin={inspection.VIN} />,
        inspection.asset_type,
        inspection.created_by || t("general.not_applicable"),
        inspection.current_location,
        moment(inspection.date_created).format("YYYY-MM-DD"),
        !inspection.is_tagout ? t("lookupDailyCheckPanel.op") : t("lookupDailyCheckPanel.inop"),
        inspection.modified_by || t("general.not_applicable"),
      ],
    };
  });

  return (
    <React.Fragment>
      {isMobile ? (
        selectedInspection && mobileDetails ? (
          <DailyCheckDetails
            vehicle={vehicle}
            inspection={selectedInspection}
            setSelectedInspection={setSelectedInspection}
            setMobileDetails={setMobileDetails}
          />
        ) : (
          <div className="darkTable">
            <Table
              dataReady={dataReady}
              tableHeaders={tableHeaderTitles}
              tableData={tableData}
              onSelectionChange={(inspection) => setSelectedInspection(inspection)}
              hasSelection
            />
          </div>
        )
      ) : (
        <div className="darkTable">
          <Table
            dataReady={dataReady}
            tableHeaders={tableHeaderTitles}
            tableData={tableData}
            onSelectionChange={(inspection) => setSelectedInspection(inspection)}
            hasSelection
          />
          {selectedInspection && (
            <DailyCheckDetails
              vehicle={vehicle}
              inspection={selectedInspection}
              setSelectedInspection={setSelectedInspection}
              setMobileDetails={setMobileDetails}
            />
          )}
        </div>
      )}
    </React.Fragment>
  );
};

export default InspectionsTable;
