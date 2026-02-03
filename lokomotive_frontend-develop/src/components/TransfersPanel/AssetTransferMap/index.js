import React, { useState, useEffect } from "react";
import axios from "axios";
import { useSelector } from "react-redux";
import { useMediaQuery } from "react-responsive";
import { getAuthHeader, getRolePermissions } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import { faExchangeAlt } from "@fortawesome/free-solid-svg-icons";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import { useTranslation } from "react-i18next";
import TransferMap from "./TransferMap";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";

const TransfersPanel = () => {
  const { t } = useTranslation();
  const { listLocations } = useSelector((state) => state.apiCallData);
  const [transfersData, setTransfersData] = useState({
    awaitingApproval: [],
    awaitingTransfer: [],
    inTransit: [],
  });
  const [originLocs, setOriginLocs] = useState({
    awaitingApproval: [],
    awaitingTransfer: [],
    inTransit: [],
  });
  const [destinationLocs, setDestinationLocs] = useState({
    awaitingApproval: [],
    awaitingTransfer: [],
    inTransit: [],
  });
  const [dataReady, setDataReady] = useState(false);
  const [mapDataReady, setMapDataReady] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const [isSupervisor, setIsSupervisor] = useState(false);

  useEffect(() => {
    const rolePermissions = getRolePermissions();
    if (rolePermissions.role.toLowerCase() === "supervisor") setIsSupervisor(true);
    else setIsSupervisor(false);

    setDataReady(false);
    const cancelTokenSource = axios.CancelToken.source();
    let TransferListAPIcall = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Transfer/List`, {
      ...getAuthHeader(),
      cancelToken: cancelTokenSource.token,
    });
    axios
      .all([TransferListAPIcall])
      .then(
        axios.spread((...responses) => {
          const transferList = !!responses[0] ? responses[0].data : [];
          const awaitingTransfer = transferList.filter(
            (transfer) => transfer.status.toLowerCase() === "awaiting transfer"
          );
          const awaitingApproval = transferList.filter(
            (transfer) => transfer.status.toLowerCase() === "awaiting approval"
          );
          const inTransit = transferList.filter(
            (transfer) => transfer.status.toLowerCase() === "in transit"
          );
          setTransfersData({
            awaitingApproval: awaitingApproval,
            awaitingTransfer: awaitingTransfer,
            inTransit: inTransit,
          });
          setDataReady(true);
        })
      )
      .catch((error) => {
        ConsoleHelper(error);
      });

    return () => {
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, []);

  useEffect(() => {
    if (dataReady) {
      function getLocations(list, param) {
        let locations = [];
        list.forEach((transfer) => {
          return locations.includes(transfer[`${param}`])
            ? null
            : locations.push(transfer[`${param}`]);
        });
        return locations;
      }
      function getOriginLocationObject(list, allTransfers, oriLocations) {
        let temp_array = [];
        oriLocations.forEach((location) => {
          let temp_dest_array = [];
          let temp_count = 0;
          let tooltipString = "";
          let origin = list.find((object) => object.location_name === location);
          allTransfers.forEach((transfer) => {
            if (transfer["current_location"] === origin.location_name) {
              temp_count++;
              if (!temp_dest_array.includes(transfer["destination_location"])) {
                temp_dest_array.push(transfer["destination_location"]);
              }
              tooltipString =
                tooltipString + `${transfer["VIN"]}: to ${transfer["destination_location"]} \n `;
            }
          });
          let origin_object = {
            id: origin.location_name,
            title: origin.location_name,
            latitude: origin.latitude,
            longitude: origin.longitude,
            destinations: temp_dest_array,
            tooltip: `Location: ${origin.location_name} (${temp_count}) \n\n ` + tooltipString,
            scale: 1.5,
            zoomLevel: 5,
            zoomLongitude: origin.longitude,
            zoomLatitude: origin.latitude,
            asset_count: temp_count,
          };
          temp_array.push(origin_object);
        });
        return temp_array;
      }
      function getDestinationObjects(listLocations, oriLocations, oriDestionations) {
        let temp_locationlist = listLocations.filter((location) => {
          return !oriLocations.includes(location["location_name"]);
        });
        let temp_destList = temp_locationlist.filter((location) => {
          return oriDestionations.includes(location["location_name"]);
        });
        let temp_destinations = temp_destList.map((location) => ({
          id: location.location_name,
          title: location.location_name,
          latitude: location.latitude,
          longitude: location.longitude,
        }));
        return temp_destinations;
      }

      Object.entries(transfersData).forEach(([key, val]) => {
        if (val.length !== 0) {
          const temp = getLocations(transfersData[key], "current_location");
          const dest = getLocations(transfersData[key], "destination_location");

          const originLocs = getOriginLocationObject(listLocations, transfersData[key], temp);
          const destLocs = getDestinationObjects(listLocations, temp, dest);
          setOriginLocs((prevState) => ({
            ...prevState,
            [key]: originLocs,
          }));
          setDestinationLocs((prevState) => ({
            ...prevState,
            [key]: destLocs,
          }));
        }
      });
      setMapDataReady(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataReady]);

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={isSupervisor ? ["Map", "Transfers"] : ["Map", "Transfers", "Request"]}
          activeTab={"Map"}
          urls={
            isSupervisor
              ? ["/transfers", "/transfers/list"]
              : ["/transfers", "/transfers/list", "/transfers/asset-transfer"]
          }
        />
      )}
      <PanelHeader icon={faExchangeAlt} text={t("assetTransferPanel.transfers")} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={
            isSupervisor
              ? ["Transfer Map", "List Transfers"]
              : ["Transfer Map", "List Transfers", "Transfer Asset"]
          }
          activeTab={"Transfer Map"}
          urls={
            isSupervisor
              ? ["/transfers", "/transfers/list"]
              : ["/transfers", "/transfers/list", "/transfers/asset-transfer"]
          }
        />
      )}
      {mapDataReady ? (
        <div className={`${!isMobile ? "p-mt-5" : "p-mt-2 p-mb-5"}`}>
          <TransferMap originLocs={originLocs} destinationLocs={destinationLocs} />
        </div>
      ) : (
        <div className="p-pt-5">
          <FullWidthSkeleton height="600px">{""}</FullWidthSkeleton>
        </div>
      )}
    </div>
  );
};

export default TransfersPanel;
