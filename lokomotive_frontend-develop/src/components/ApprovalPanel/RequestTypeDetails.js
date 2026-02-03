import React, { useState, useEffect } from "react";
import axios from "axios";
import moment from "moment";
import { useMediaQuery } from "react-responsive";
import { useTranslation } from "react-i18next";
import * as Constants from "../../constants";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import { capitalize } from "../../helpers/helperFunctions";
import { getAuthHeader } from "../../helpers/Authorization";
import LoadingAnimation from "../ShareComponents/LoadingAnimation";

const RequestTypeDetails = ({
  request,
  dataReady,
  setSelectedRequest,
  setDataReady,
  setRequestFiles,
  setQuotesList,
}) => {
  const { t } = useTranslation();
  const [requestDetails, setRequestDetails] = useState([]);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    const getDetails = (URL, cb, errorHandler) => {
      return axios
        .get(URL, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then(cb)
        .catch(errorHandler);
    };
    const errorHandler = (err) => {
      ConsoleHelper(err);
    };
    if (!dataReady && request) {
      let details;
      let requestURL;
      let cb;

      if (request.maintenance_request) {
        requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Get/Details/ID/${request.maintenance_request}`;
        cb = (res) => {
          const data = res.data;
          setSelectedRequest(data);
          let titles = [
            t("general.id"),
            t("general.inspection_type"),
            t("general.status"),
            ...(data.status === "complete" && data.status === "delivered"
              ? [t("general.date_completed")]
              : []),
            t("general.asset_type"),
            t("general.location"),
            ...(data.mileage !== -1.0 ? [t("general.mileage")] : []),
            ...(data.hours !== -1.0 ? [t("general.hours")] : []),
            t("general.vendor"),
            ...(data.status !== "delivered" ? [t("general.requested_delivery_date")] : []),
            ...(data.status !== "delivered" ? [t("general.estimated_delivery_date")] : []),
            ...(data.status !== "delivered" ? [t("general.available_pickup_date")] : []),
            ...(data.status !== "delivered" ? [t("general.vendor_contacted_date")] : []),
            t("general.created_by"),
            t("general.modified_by"),
            t("general.date_created"),
            t("general.date_updated"),
          ];
          let values = [
            data.work_order,
            data.inspection_type,
            capitalize(data.status),
            ...(data.status === "complete" && data.status === "delivered"
              ? [moment(data.date_completed).format("YYYY-MM-DD")]
              : []),
            request.asset_type,
            data.current_location,
            ...(data.mileage !== -1.0 ? [data.mileage] : []),
            ...(data.hours !== -1.0 ? [data.hours] : []),
            data.vendor_name || t("general.not_applicable"),
            ...(data.status !== "delivered"
              ? moment(data.requested_delivery_date).isValid()
                ? [moment(data.requested_delivery_date).format("YYYY-MM-DD")]
                : [t("general.not_applicable")]
              : []),
            ...(data.status !== "delivered"
              ? moment(data.estimated_delivery_date).isValid()
                ? [moment(data.estimated_delivery_date).format("YYYY-MM-DD")]
                : [t("general.not_applicable")]
              : []),
            ...(data.status !== "delivered"
              ? moment(data.available_pickup_date).isValid()
                ? [moment(data.available_pickup_date).format("YYYY-MM-DD")]
                : [t("general.not_applicable")]
              : []),
            ...(data.status !== "delivered"
              ? moment(data.vendor_contacted_date).isValid()
                ? [moment(data.vendor_contacted_date).format("YYYY-MM-DD")]
                : [t("general.not_applicable")]
              : []),
            data.created_by,
            data.modified_by,
            moment(data.date_created).format("YYYY-MM-DD"),
            moment(data.date_updated).format("YYYY-MM-DD"),
          ];
          details = titles.map((title, index) => ({ title, value: values[index] }));
          setRequestDetails(details);
          setDataReady(true);
          setRequestFiles(data.files);
          setQuotesList(data.quotes);
        };
        getDetails(requestURL, cb, errorHandler);
      } else if (request.repair_request) {
        requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Get/Details/ID/${request.repair_request}`;
        cb = (res) => {
          const data = res.data;
          setSelectedRequest(data);
          let titles = [
            t("general.id"),
            t("general.status"),
            ...(data.status === "complete" ? [t("general.date_completed")] : []),
            t("general.asset_type"),
            t("general.division"),
            t("general.location"),
            ...(data.mileage !== -1.0 ? [t("general.mileage")] : []),
            ...(data.hours !== -1.0 ? [t("general.hours")] : []),
            t("general.vendor"),
            ...(data.status !== "complete" ? [t("general.requested_delivery_date")] : []),
            ...(data.status !== "complete" ? [t("general.estimated_delivery_date")] : []),
            ...(data.status !== "complete" ? [t("general.available_pickup_date")] : []),
            t("general.created_by"),
            t("general.modified_by"),
            t("general.date_created"),
            t("general.date_updated"),
          ];
          let values = [
            data.work_order,
            capitalize(data.status),
            ...(data.status === "complete"
              ? [moment(data.date_completed).format("YYYY-MM-DD")]
              : []),
            request.asset_type,
            data.business_unit,
            data.current_location,
            ...(data.mileage !== -1.0 ? [data.mileage] : []),
            ...(data.hours !== -1.0 ? [data.hours] : []),
            data.vendor_name || t("general.not_applicable"),
            ...(data.status !== "complete"
              ? moment(data.requested_delivery_date).isValid()
                ? [moment(data.requested_delivery_date).format("YYYY-MM-DD")]
                : [t("general.not_applicable")]
              : []),
            ...(data.status !== "complete"
              ? moment(data.estimated_delivery_date).isValid()
                ? [moment(data.estimated_delivery_date).format("YYYY-MM-DD")]
                : [t("general.not_applicable")]
              : []),
            ...(data.status !== "complete"
              ? moment(data.available_pickup_date).isValid()
                ? [moment(data.available_pickup_date).format("YYYY-MM-DD")]
                : [t("general.not_applicable")]
              : []),
            data.created_by,
            data.modified_by,
            moment(data.date_created).format("YYYY-MM-DD"),
            moment(data.date_modified).format("YYYY-MM-DD"),
          ];
          details = titles.map((title, index) => ({ title, value: values[index] }));
          setRequestDetails(details);
          setDataReady(true);
          setRequestFiles(data.files);
          setQuotesList(data.quotes);
        };
        getDetails(requestURL, cb, errorHandler);
      } else if (request.asset_transfer_request) {
        requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Transfer/Get/Details/ID/${request.asset_transfer_request}`;
        cb = (res) => {
          const data = res.data;
          setSelectedRequest(data);
          let titles = [
            t("general.id"),
            t("general.status"),
            t("general.business_unit"),
            t("general.current_location"),
            t("general.destination_location"),
            t("general.created_by"),
            t("general.modified_by"),
            t("general.date_created"),
            t("general.date_updated"),
          ];
          let values = [
            data.custom_id,
            capitalize(data.status),
            data.business_unit,
            data.current_location,
            data.destination_location,
            data.created_by || t("general.not_applicable"),
            data.modified_by || t("general.not_applicable"),
            moment(data.date_created).format("YYYY-MM-DD") || t("general.not_applicable"),
            moment(data.date_modified).format("YYYY-MM-DD") || t("general.not_applicable"),
          ];
          details = titles.map((title, index) => ({ title, value: values[index] }));
          setRequestDetails(details);
          setDataReady(true);
          setRequestFiles(data.files);
        };
        getDetails(requestURL, cb, errorHandler);
      } else if (request.asset_request) {
        requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/AssetRequest/Get/Details/ID/${request.asset_request}`;
        cb = (res) => {
          const data = res.data;
          setSelectedRequest(data);
          let titles = [
            t("general.id"),
            t("general.status"),
            t("general.asset_type"),
            t("assetOrderDetails.business_unit_label"),
            t("assetOrderDetails.manufacturer_label"),
            t("assetOrderDetails.equipment_type_label"),
            t("assetOrderDetails.date_required_label"),
            t("assetOrderDetails.justification_label"),
            t("general.vendor_email"),
            t("general.created_by"),
            t("general.modified_by"),
            t("general.date_created"),
            t("general.date_updated"),
          ];
          let values = [
            data.custom_id,
            capitalize(data.status),
            request.asset_type,
            data.business_unit,
            data.manufacturer,
            data.model_number,
            moment(data.date_required).format("YYYY-MM-DD"),
            data.justification,
            data.vendor_email,
            data.created_by,
            data.modified_by || t("general.not_applicable"),
            moment(data.date_created).format("YYYY-MM-DD"),
            moment(data.date_updated).format("YYYY-MM-DD"),
          ];
          details = titles.map((title, index) => ({ title, value: values[index] }));
          setRequestDetails(details);
          setDataReady(true);
          setRequestFiles(data.files);
          setQuotesList(data.quotes);
        };
        getDetails(requestURL, cb, errorHandler);
      } else if (request.disposal_request) {
        requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/AssetDisposal/Get/Details/ID/${request.disposal_request}`;
        cb = (res) => {
          const data = res.data;
          setSelectedRequest(data);
          let titles = [
            t("general.id"),
            t("general.status"),
            t("general.asset_type"),
            t("fleetPanel.manufacturer_label"),
            t("general.model_number"),
            t("removalDetails.disposal_reason"),
            t("removalDetails.refurbish_required"),
            t("removalDetails.interior_condition"),
            t("removalDetails.exterior_condition"),
            t("general.available_pickup_date"),
            t("general.created_by"),
            t("general.modified_by"),
            t("general.date_created"),
            t("general.date_updated"),
          ];
          let values = [
            data.custom_id,
            capitalize(data.status),
            request.asset_type,
            data.manufacturer || t("general.not_applicable"),
            data.model_number || t("general.not_applicable"),
            capitalize(data.disposal_reason),
            data.refurbished ? t("general.yes") : t("general.no"),
            capitalize(data.interior_condition),
            capitalize(data.exterior_condition),
            moment(data.available_pickup_date).format("YYYY-MM-DD") || t("general.not_applicable"),
            data.created_by || t("general.not_applicable"),
            data.modified_by || t("general.not_applicable"),
            moment(data.date_created).format("YYYY-MM-DD") || t("general.not_applicable"),
            moment(data.date_modified).format("YYYY-MM-DD") || t("general.not_applicable"),
          ];
          details = titles.map((title, index) => ({ title, value: values[index] }));
          setRequestDetails(details);
          setDataReady(true);
          setRequestFiles(data.files);
          setQuotesList(data.quotes);
        };
        getDetails(requestURL, cb, errorHandler);
      }
    }
    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [request, dataReady]);
  return (
    <React.Fragment>
      {!dataReady ? (
        <div className="p-mt-2">
          <LoadingAnimation height={"150px"} />
        </div>
      ) : (
        <React.Fragment>
          {requestDetails ? (
            <div
              className={`add-descr-section p-d-flex p-flex-column ${
                isMobile ? "main-details" : ""
              }`}
            >
              {isMobile && <hr />}
              <div className="p-d-flex p-jc-between">
                <span className="title font-weight-bold">{request.request_type}</span>
              </div>
              {requestDetails.map((el, index) => (
                <div className="p-d-flex p-jc-between" key={index}>
                  <span className="sub-title">{`${el.title}:`}</span>
                  <span className="sub-value">{el.value}</span>
                </div>
              ))}
              {!isMobile && <hr />}
            </div>
          ) : null}
        </React.Fragment>
      )}
    </React.Fragment>
  );
};

export default RequestTypeDetails;
