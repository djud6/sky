import React, { useState, useEffect } from "react";
import axios from "axios";
import moment from "moment";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import repairs from "../../../images/menu/icon_menu_repairs.png";
import maintenance from "../../../images/menu/icon_menu_maintenance.png";
import incidents from "../../../images/menu/icon_menu_incidents.png";
import issues from "../../../images/menu/icon_menu_issues.png";
import operators from "../../../images/menu/icon_menu_operators.png";
import removal from "../../../images/menu/icon_menu_disposal.png";
import comment from "../../../images/menu/icon_profile-edit.png";
import fleet from "../../../images/menu/icon_menu_dashboard.png";
import { capitalize } from "../../../helpers/helperFunctions";
import { getAuthHeader } from "../../../helpers/Authorization";
import CardWidget from "../CardWidget";
import DailyCheckDetails from "../../OperatorsPanel/LookupDailyChecks/DailyCheckDetails";
import IncidentDetails from "../../IncidentsPanel/IncidentReports/IncidentDetails";
import IssueDetails from "../../IssuesPanel/UnresolvedIssues/IssueDetails";
import RepairDetails from "../../RepairsPanel/ListRepairs/RepairDetails";
import MaintenanceDetails from "../../MaintenancePanel/MaintenanceStatus/MaintenanceDetails";
import MaintenanceRulesDetails from "../../MaintenancePanel/MaintenanceForecast/MaintenanceRulesDetails";
import AssetRemovalDetails from "../../DisposalPanel/RemovalHistory/AssetRemovalDetails";
import TransferDetails from "../../TransfersPanel/TransferDetails";
import { generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button2.scss";
import "../../../styles/ShareComponents/AssetTimeline.scss";
import Timeline from "../../../components_two/Timeline/Timeline";

const AssetTimeline = ({ asset, events }) => {
  const [showMore, setShowMore] = useState(events.length > 50);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [eventDetails, setEventDetails] = useState(false);
  const [detailsReady, setDetailsReady] = useState(false);
  const displayEvents = showMore ? events.slice(0, 50) : events;

  useEffect(() => {
    // reset the state when passed in events is updatedw
    setShowMore(events.length > 50);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(events)]);

  const idClicked = (item) => {
    setEventDetails(false);
    setSelectedEvent(item);
    setDetailsReady(false);
    let api_url;
    if (item.event_type === "operator check") {
      api_url = `/api/v1/DailyOperationalChecks/Get/Details/CustomID/${item.event_id}`
    } else if (item.event_type === "accident") {
      api_url = `/api/v1/Accident/Get/Details/CustomID/${item.event_id}`
    } else if (item.event_type === "issue") {
      api_url = `/api/v1/Issues/Get/Details/CustomID/${item.event_id}`
    } else if (item.event_type === "repair") {
      api_url = `/api/v1/Repair/Get/Details/WorkOrder/${item.event_id}`
    } else if (item.event_type === "maintenance") {
      api_url = `/api/v1/Maintenance/Get/Details/WorkOrder/${item.event_id}`
    } else if (item.event_type === "maintenance rule") {
      api_url = `/api/v1/Maintenance/Forecast/Rule/Details/CustomID/${item.event_id}`
    } else if (item.event_type === "disposal") {
      api_url = `/api/v1/AssetDisposal/Get/Details/CustomID/${item.event_id}`
    } else if (item.event_type === "transfer") {
      api_url = `/api/v1/Transfer/Get/Details/CustomID/${item.event_id}`
    } 

    getDetails(api_url);
  }

  const getDetails = (url) => {
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}${url}`, {
        ...getAuthHeader(), cancelToken: cancelTokenSource.token 
      })
      .then((res) => {
        setEventDetails(res.data);
        setDetailsReady(true);
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        ConsoleHelper(error);
      })
  }

  const customizedContent = (item) => {
    const contentCopy = item.content.split(item.event_id);
    return (
      <div className="timeline-content-card p-mb-5">
        <CardWidget status={"inActive"}>
          <div className="title p-mb-2">
            {capitalize(item.event_type)}
          </div>
          <div className="subtitle">
            {`${moment(item.create_date).format("YYYY-MM-DD HH:mm A")} by ${item.author}`}
          </div>
          {item.content &&
            item.event_id ?
              <span className="message">
                {contentCopy[0]}
                  <span
                    className="clickable-id"
                    onClick={() => idClicked(item)}
                  >
                    {"ID: " + item.event_id}
                  </span>
                {contentCopy[1]}
              </span>
              :
              <span className="message">{item.content}</span>
          }
        </CardWidget>
      </div>
    );
  };

  const customizedMarker = (item) => {
    let icon;
    switch (item.event_type) {
      case "comment":
        icon = comment;
        break;
      case "repair":
        icon = repairs;
        break;
      case "operator check":
        icon = operators;
        break;
      case "maintenance":
        icon = maintenance;
        break;
      case "issue":
        icon = issues;
        break;
      case "disposal":
        icon = removal;
        break;
      case "accident":
        icon = incidents;
        break;
      case "maintenance rule":
        icon = maintenance;
        break;
      case "transfer":
        icon = fleet;
        break;
      default:
        icon = comment;
    }

    return (
      <span className="custom-marker p-shadow-2" style={{ backgroundColor: "#115A98" }}>
        <img src={icon} className="pi pi-fw timeline-icon" alt={item.label} />
      </span>
    );
  };

  return (
    <div className="asset-log-timeline">
      {displayEvents.length > 0 ? (
        <Timeline
          value={displayEvents}
          align="left"
          className="customized-timeline"
          marker={customizedMarker}
          content={customizedContent}
        />
      ) : (
        <h2 className="no-event text-center p-mt-5">No event found</h2>
      )}
      {showMore && (
        <div className="p-d-flex p-jc-center btn-2">
          <Button
            label="Show More"
            className="p-button-lg p-mb-5"
            onClick={() => setShowMore(false)}
          />
        </div>
      )}
      {selectedEvent &&
        (selectedEvent.event_type === "operator check" ?
          <DailyCheckDetails
            vehicle={asset}
            inspection={eventDetails}
            setSelectedInspection={setSelectedEvent}
            detailsReady={detailsReady}
            disableMobileVersion
          />
        :
        selectedEvent.event_type === "accident" ?
          <IncidentDetails
            incident={eventDetails}
            setSelectedIncident={setSelectedEvent}
            detailsReady={detailsReady}
            disableButtons
            disableMobileVersion
          />
        : 
        selectedEvent.event_type === "issue" ?
          <IssueDetails
            issue={eventDetails}
            setSelectedIssue={setSelectedEvent}
            detailsReady={detailsReady}
            disableButtons
            disableMobileVersion
          />
        :
        selectedEvent.event_type === "repair" ?
          <RepairDetails
            repair={eventDetails}
            setSelectedRepair={setSelectedEvent}
            detailsReady={detailsReady}
            disableButtons
            disableMobileVersion
          />
        :
        selectedEvent.event_type === "maintenance" ?
          <MaintenanceDetails
            maintenance={eventDetails}
            setSelectedMaintenance={setSelectedEvent}
            detailsReady={detailsReady}
            disableButtons
            disableMobileVersion
          />
        :
        selectedEvent.event_type === "maintenance rule" ?
          <MaintenanceRulesDetails
            rule={eventDetails}
            setSelectedRule={setSelectedEvent}
            detailsReady={detailsReady}
          />
        :
        selectedEvent.event_type === "disposal" ?
          <AssetRemovalDetails
            asset={eventDetails}
            setSelectedAsset={setSelectedEvent}
            detailsReady={detailsReady}
            disableButtons
            disableMobileVersion
          />
        :
        selectedEvent.event_type === "transfer" ?
          <TransferDetails
            transfer={eventDetails}
            setSelectedTransfer={setSelectedEvent}
            detailsReady={detailsReady}
            disableMobileVersion
          />
        : null)
      }
    </div>
  );
};

export default AssetTimeline;
