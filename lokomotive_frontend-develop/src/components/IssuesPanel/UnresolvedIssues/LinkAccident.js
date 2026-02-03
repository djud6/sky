import React, { useState, useEffect } from "react";
import axios from "axios";
import moment from "moment";
import { useDispatch } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import { Table } from "../../ShareComponents/Table";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";

const RelatedAccidentsTable = ({ dataReady, relatedAccidents, setSelectedAccident }) => {
  const { t } = useTranslation();
  const incidentType = {
    all: t("general.all"),
    preventable: t("general.preventable"),
    nonpreventable: t("general.non_preventable"),
  };

  const incidentItemTemplate = (value) => {
    return value ? incidentType.preventable : incidentType.nonpreventable;
  };

  let accidentTableHeaders = [];
  let accidentTableData = [];

  if (relatedAccidents) {
    relatedAccidents = relatedAccidents.filter((i) => {
      return !i.is_resolved;
    });

    accidentTableHeaders = [
      { header: t("general.id"), colFilter: { field: "custom_id" } },
      { header: t("incidentsDetails.accident_summary"), colFilter: { field: "accident_summary" } },
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
    ];

    accidentTableData = relatedAccidents.map((incident) => {
      return {
        id: incident.accident_id,
        dataPoint: incident,
        cells: [
          incident.custom_id,
          incident.accident_summary,
          incident.is_preventable ? incidentType.preventable : incidentType.nonpreventable,
          moment(incident.date_created).format("YYYY-MM-DD"),
        ],
      };
    });
  }

  return (
    <div className="darkTable">
      <Table
        dataReady={dataReady}
        tableHeaders={accidentTableHeaders}
        tableData={accidentTableData}
        onSelectionChange={(incident) => setSelectedAccident(incident)}
        hasSelection
      />
    </div>
  );
};

const LinkAccident = ({
  issue,
  displayAccidentTable,
  setDisplayAccidentTable,
  setSelectedIssue,
  setIssues,
  issuePanel,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [accidentDataReady, setAccidentDataReady] = useState(false);
  const [relatedAccidents, setRelatedAccidents] = useState([]);
  const [selectedAccident, setSelectedAccident] = useState(null);

  useEffect(() => {
    if (displayAccidentTable) {
      const cancelTokenSource = axios.CancelToken.source();
      setRelatedAccidents([]);
      setSelectedAccident(null);
      setAccidentDataReady(false);
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Accident/VIN/${issue.VIN}`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          setRelatedAccidents(response.data);
          setAccidentDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [displayAccidentTable]);

  const renderFooter = (cancelAction, confirmAction) => {
    return (
      <div>
        <Button
          label="Cancel"
          icon="pi pi-times"
          onClick={() => cancelAction(false)}
          className="p-button-text"
        />
        <Button
          label="Confirm"
          icon="pi pi-check"
          onClick={() => confirmAction()}
          autoFocus
          disabled={!selectedAccident}
        />
      </div>
    );
  };

  const linkAccident = () => {
    loadingAlert();
    axios
      .post(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Issues/ID/${issue.issue_id}/Set/Accident/ID/${selectedAccident.accident_id}`,
        null,
        getAuthHeader()
      )
      .then((response) => {
        setDisplayAccidentTable(false);
        refreshData();
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  const refreshData = async () => {
    const cancelTokenSource = axios.CancelToken.source();
    let response;
    if (issuePanel === "all") {
      response = await axios.post(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Issues/List/Type`,
        {},
        { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
      );
    } else if (issuePanel === "search") {
      response = await axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Issues/VIN/${issue.VIN}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });
    }

    const getIssues = response.data;
    const filteredIssue = getIssues.filter((i) => i.issue_id === issue.issue_id);

    setSelectedIssue(filteredIssue[0]);
    setIssues(getIssues);
    successAlert(t("issueDetails.link_accident_success_text"));
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
  };

  return (
    <div>
      {/* Link Accident Dialog */}
      <Dialog
        className="custom-main-dialog"
        header={t("issueDetails.select_accident")}
        visible={displayAccidentTable}
        onHide={() => setDisplayAccidentTable(false)}
        style={{ width: "50vw" }}
        breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
        footer={renderFooter(setDisplayAccidentTable, linkAccident)}
        baseZIndex={1000}
      >
        <RelatedAccidentsTable
          dataReady={accidentDataReady}
          relatedAccidents={relatedAccidents}
          setSelectedAccident={setSelectedAccident}
        />
      </Dialog>
    </div>
  );
};

export default LinkAccident;
