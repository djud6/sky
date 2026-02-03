import React, { useState, useEffect } from "react";
import axios from "axios";
import swal from "sweetalert";
import { useDispatch } from "react-redux";
import { useHistory, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { faOilCan } from "@fortawesome/free-solid-svg-icons";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import ScheduleMaintenanceTable from "./ScheduleMaintenanceTable";
import MaintenanceOptions from "./MaintenanceOptions";
import { loadingAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/MaintenancePanel/scheduleMaintenance.scss";

const ScheduleMaintenancePanel = (props) => {
  const dispatch = useDispatch();
  const history = useHistory();
  const location = useLocation();
  const { t } = useTranslation();
  const [vehicle, setVehicle] = useState(null);
  const [selectedVehicles, setSelectedVehicles] = useState(
    location.query ? location.query.vehicles : []
  );
  const [maintenanceTypes, setMaintenanceTypes] = useState(
    location.query ? location.query.maintenanceTypes : []
  );
  const [dataReady, setDataReady] = useState(false);
  const [maintenanceType, setMaintenanceType] = useState(
    location.query ? location.query.maintenanceType : null
  );
  const [mileageNhours, setMileageNhours] = useState([]);
  const [usageWarningMsg, setUsageWarningMsg] = useState([]);
  const [files, setFiles] = useState({});
  const [pickupDate, setPickupDate] = useState(null);
  const [requestedDeliveryDate, setRequestedDeliveryDate] = useState(null);
  const [quoteDeadline, setQuoteDeadline] = useState(null);
  const [vendorEmail, setVendorEmail] = useState("");
  const [inHouse, setInHouse] = useState(null);
  const [approvedVendors, setApprovedVendors] = useState(null);
  const [approvedVendor, setApprovedVendor] = useState(null);
  const [multiSelectedVendor, setMultiSelectedVendor] = useState([]);
  const [vendorTransportToVendor, setVendorTransportToVendor] = useState(null);
  const [vendorTransportToClient, setVendorTransportToClient] = useState(null);
  const [estimatedCost, setEstimatedCost] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const handleSubmit = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    const tempData = selectedVehicles.map((asset, i) => {
      let scheduleData = {
        maintenance_data: {
          VIN: asset.VIN,
          inspection_type: maintenanceType,
          location: "1",
          is_complete: false,
          quote_deadline: quoteDeadline.toISOString(),
          ...(inHouse === t("general.yes")
            ? { in_house: true, estimated_cost: estimatedCost }
            : { in_house: false }),
          ...(inHouse === t("general.no")
            ? {
                vendor_transport_to_vendor: vendorTransportToVendor,
                available_pickup_date: pickupDate.toISOString(),
                vendor_transport_to_client: vendorTransportToClient,
                requested_delivery_date: requestedDeliveryDate.toISOString(),
              }
            : { available_pickup_date: new Date().toISOString() }), // todo remove hard-coding once backend is ready
          ...(inHouse === t("general.no") && approvedVendor === t("general.approved_vendors")
            ? {
                assigned_vendor: null, //TODO need to auto setup this in the future
                potential_vendor_ids: `-${multiSelectedVendor.map((el) => el.code).join("-")}-`,
              }
            : null),
          ...(inHouse === t("general.no") && approvedVendor === t("general.other_vendors")
            ? { vendor_email: vendorEmail }
            : null),
          ...{
            file_info: files[asset.VIN].length
              ? [
                  {
                    file_name: files[asset.VIN][0]["name"],
                    purpose: "other",
                  },
                ]
              : [],
          },
        },
        // TODO: Replace the placeholder info for approval_data
        approval_data: {
          title: "Maintenance Approval",
          description: "This is an approval made for testing purposes.",
        },
      };
      if (
        asset.hours_or_mileage.toLowerCase() === "mileage" ||
        asset.hours_or_mileage.toLowerCase() === "both"
      ) {
        scheduleData.maintenance_data.mileage = Number(mileageNhours[i].Mileage);
      }
      if (
        asset.hours_or_mileage.toLowerCase() === "hours" ||
        asset.hours_or_mileage.toLowerCase() === "both"
      ) {
        scheduleData.maintenance_data.hours = Number(mileageNhours[i].Hours);
      }

      return scheduleData;
    });

    let maintenanceRequests = new FormData();
    let dataFormat = { assets: tempData };
    maintenanceRequests.append("data", JSON.stringify(dataFormat));
    selectedVehicles.forEach((asset) => {
      if (files[asset.VIN][0]) {
        maintenanceRequests.append("files", files[asset.VIN][0]);
      }
    });
    submitRequest(maintenanceRequests);
  };

  const submitRequest = (maintenanceRequests) => {
    const headers = getAuthHeader();
    headers.headers["Content-Type"] = "application/json";
    const requestConfig = {
      method: "post",
      url: `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Add/Batch`,
      ...headers,
      data: maintenanceRequests,
    };
    loadingAlert();
    axios(requestConfig)
      .then((response) => {
        successAlert();
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  const successAlert = () => {
    return swal({
      title: t("maintenanceSchedulePanel.alert_success_title"),
      text: t("maintenanceSchedulePanel.alert_success_text"),
      icon: "success",
      buttons: {
        return: t("maintenanceSchedulePanel.alert_success_button_return"),
        new: t("maintenanceSchedulePanel.alert_success_button_new_request"),
      },
    }).then((value) => {
      switch (value) {
        case "return":
          history.push("/maintenance");
          break;
        default:
          resetAll();
      }
    });
  };

  // Reset function
  const resetAll = () => {
    setVehicle(null);
    setSelectedVehicles([]);
    setMaintenanceType(location.query ? location.query.maintenanceType : null);
    setPickupDate(null);
    setRequestedDeliveryDate(null);
    setQuoteDeadline(null);
    setInHouse(null);
    setApprovedVendor(null);
    setMultiSelectedVendor([]);
    setVendorEmail("");
  };

  // Getting inspection types
  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();

    let inspectionAPI = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Inspection/List`,
      getAuthHeader()
    );
    let approvedVendorsAPI = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/ApprovedVendor/List/By/Task/maintenance`,
      getAuthHeader()
    );

    axios
      .all([inspectionAPI, approvedVendorsAPI])
      .then(
        axios.spread((...responses) => {
          setMaintenanceTypes(responses[0].data);
          const approvedVendorAPIResponse = !!responses[1] ? responses[1].data : null;
          setApprovedVendors(approvedVendorAPIResponse);

          setDataReady(true);
        })
      )
      .catch((err) => {
        ConsoleHelper(err);
      });

    return () => {
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, []);

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["Status", "Schedule", "Forecast", "Lookup"]}
          activeTab={"Schedule"}
          urls={[
            "/maintenance",
            "/maintenance/schedule",
            "/maintenance/forecast",
            "/maintenance/lookup",
          ]}
        />
      )}
      <PanelHeader icon={faOilCan} text={t("maintenanceSchedulePanel.page_title")} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Status", "Schedule", "Forecast", "Lookup"]}
          activeTab={"Schedule"}
          urls={[
            "/maintenance",
            "/maintenance/schedule",
            "/maintenance/forecast",
            "/maintenance/lookup",
          ]}
        />
      )}
      {!vehicle
        ? selectedVehicles.length === 0 && (
            <div className={`${isMobile ? "p-pb-4" : "p-mt-5"}`}>
              <VINSearch
                defaultValue={`${!vehicle && location.state ? location.state.vehicle.VIN : ""}`}
                onVehicleSelected={(v) => {
                  if (!Array.isArray(v) && v != null) {
                    !selectedVehicles.some((el) => el.VIN === v.VIN) &&
                      setSelectedVehicles([...selectedVehicles, v]);
                  }
                  setVehicle(v);
                }}
              />
            </div>
          )
        : null}
      {selectedVehicles.length > 0 && (
        <div className={`${!isMobile ? "p-mt-3" : ""}`}>
          <ScheduleMaintenanceTable
            selectedVehicles={selectedVehicles}
            maintenanceTypes={maintenanceTypes}
            maintenanceType={maintenanceType}
            setSelectedVehicles={setSelectedVehicles}
            resetAll={resetAll}
            setVehicle={setVehicle}
          />
          <MaintenanceOptions
            selectedVehicles={selectedVehicles}
            maintenanceTypes={maintenanceTypes}
            maintenanceType={maintenanceType}
            setMaintenanceType={setMaintenanceType}
            mileageNhours={mileageNhours}
            setUsageWarningMsg={setUsageWarningMsg}
            usageWarningMsg={usageWarningMsg}
            files={files}
            setFiles={setFiles}
            setMileageNhours={setMileageNhours}
            pickupDate={pickupDate}
            setPickupDate={setPickupDate}
            quoteDeadline={quoteDeadline}
            setQuoteDeadline={setQuoteDeadline}
            requestedDeliveryDate={requestedDeliveryDate}
            setRequestedDeliveryDate={setRequestedDeliveryDate}
            inHouse={inHouse}
            setInHouse={setInHouse}
            approvedVendors={approvedVendors}
            approvedVendor={approvedVendor}
            setApprovedVendor={setApprovedVendor}
            multiSelectedVendor={multiSelectedVendor}
            setMultiSelectedVendor={setMultiSelectedVendor}
            vendorEmail={vendorEmail}
            setVendorEmail={setVendorEmail}
            dataReady={dataReady}
            handleSubmit={handleSubmit}
            vendorTransportToVendor={vendorTransportToVendor}
            setVendorTransportToVendor={setVendorTransportToVendor}
            vendorTransportToClient={vendorTransportToClient}
            setVendorTransportToClient={setVendorTransportToClient}
            estimatedCost={estimatedCost}
            setEstimatedCost={setEstimatedCost}
          />
        </div>
      )}
    </div>
  );
};

export default ScheduleMaintenancePanel;
