import React, { useState, useEffect } from "react";
import axios from "axios";
import { useMediaQuery } from "react-responsive";
import { ToggleButton } from "primereact/togglebutton";
import { getAuthHeader } from "../../helpers/Authorization";
import * as Constants from "../../constants";
import AssetDetailsLog from "./AssetDetailsLog";
import { capitalize } from "../../helpers/helperFunctions";
import FormDropdown from "../ShareComponents/Forms/FormDropdown";
import AssetTimeline from "../ShareComponents/AssetTimeline/AssetTimeline";
import FullWidthSkeleton from "../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import ConsoleHelper from "../../helpers/ConsoleHelper";

const AssetLogTab = ({ vin, asset }) => {
  const [assetLogs, setAssetLogs] = useState([]);
  const [dataReady, setDataReady] = useState(false);
  const [checkedFilters, setCheckedFilters] = useState([]);
  const [eventTypeFilter, setEventTypeFilter] = useState([]);
  const [theAllFilter, setTheAllFilter] = useState(true);
  const [eventTypes, setEventTypes] = useState([]);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    let assetLogsRequest = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Asset/Get/Logs/${vin}`, {
      ...getAuthHeader(),
      cancelToken: cancelTokenSource.token,
    });
    let eventTypesRequest = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Asset/Get/Logs/Event/Types`,
      {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      }
    );

    axios
      .all([assetLogsRequest, eventTypesRequest])
      .then(
        axios.spread((...responses) => {
          let filtersArray = new Array(1 + responses[1].data.length).fill(false);
          if (!checkedFilters.includes(true)) setCheckedFilters(filtersArray);
          setAssetLogs(responses[0].data);
          setEventTypes(["comment", ...responses[1].data]);
          setDataReady(true);
        })
      )
      .catch((error) => {
        ConsoleHelper(error);
      });
    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vin, dataReady, JSON.stringify(checkedFilters)]);

  let events = assetLogs.map((log) => {
    return {
      content: log.content,
      event_type: log.log_type === "comment" ? "comment" : log.event_type,
      create_date: log.asset_log_created,
      author: log.created_by,
      event_id: log.event_id
    };
  });

  let filteredEvents = events.filter(function (event) {
    if (eventTypeFilter.length === 0) return true;
    return eventTypeFilter.includes(event.event_type);
  });

  const filtersHandler = (eventType, i) => {
    let copyOfCheckedFilters = [...checkedFilters];
    copyOfCheckedFilters[i] = !checkedFilters[i];
    setCheckedFilters(copyOfCheckedFilters);
    setTheAllFilter(false);
    let copyOfEventTypeFilter = [...eventTypeFilter];
    if (eventTypeFilter.includes(eventType)) {
      copyOfEventTypeFilter = copyOfEventTypeFilter.filter((type) => type !== eventType);
      setEventTypeFilter(copyOfEventTypeFilter);
      if (copyOfEventTypeFilter.length === 0) setTheAllFilter(!theAllFilter);
    } else {
      copyOfEventTypeFilter.push(eventType);
      setEventTypeFilter(copyOfEventTypeFilter);
    }
  };

  const handleTheAllFilter = () => {
    const clearAllFilters = new Array(checkedFilters.length).fill(false);
    setCheckedFilters(clearAllFilters);
    setTheAllFilter(true);
    setEventTypeFilter([]);
  };

  const selectEventType = (selected) => {
    setTheAllFilter(false);
    setEventTypeFilter([selected]);
  };

  const filterButtons = eventTypes.map((eventType, i) => {
    return (
      <ToggleButton
        key={eventType + i}
        checked={checkedFilters[i]}
        onChange={() => filtersHandler(eventType, i)}
        onLabel={capitalize(eventType)}
        offLabel={capitalize(eventType)}
        onIcon=""
        offIcon=""
        className="p-mr-2 p-mb-2 p-button-rounded"
      />
    );
  });

  return (
    <div className="p-mt-3 asset-details-log-tab">
      <h5 className="p-mb-3 asset-log-title">Asset History for {asset.VIN}</h5>
      {dataReady ? (
        <React.Fragment>
          <div className="timeline">
            {!isMobile && (
              <div className="p-d-flex p-flex-wrap p-jc-center p-pt-3">
                <ToggleButton
                  checked={theAllFilter}
                  onChange={handleTheAllFilter}
                  onLabel="All"
                  offLabel="All"
                  onIcon=""
                  offIcon=""
                  className="p-mr-2 p-mb-2 p-button-rounded"
                />
                {filterButtons}
              </div>
            )}
            <div className="add-comment">
              <AssetDetailsLog asset={asset} setDataReady={setDataReady} />
            </div>
            {isMobile && (
              <div className="select-event-mobile p-d-flex p-flex-wrap p-jc-between">
                <ToggleButton
                  checked={theAllFilter}
                  onChange={handleTheAllFilter}
                  onLabel="All"
                  offLabel="All"
                  onIcon=""
                  offIcon=""
                  className="p-mr-2 p-mb-2 p-button-rounded"
                />
                <div className="event-formdropdown">
                  <FormDropdown
                    onChange={selectEventType}
                    options={
                      eventTypes &&
                      eventTypes.map((type) => ({
                        name: capitalize(type),
                        code: type,
                      }))
                    }
                    plain_dropdown
                    placeholder="Event Type"
                  />
                </div>
              </div>
            )}
            <AssetTimeline asset={asset} events={filteredEvents} />
          </div>
        </React.Fragment>
      ) : (
        <React.Fragment>
          <FullWidthSkeleton height={"450px"} />
        </React.Fragment>
      )}
    </div>
  );
};

export default AssetLogTab;
