import React from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { RadioButton } from "primereact/radiobutton";
import RefurbishRepairRequest from "./RefurbishRepairRequest";
import CardWidget from "../../ShareComponents/CardWidget";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import DatePicker from "../../ShareComponents/DatePicker";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import "../../../styles/helpers/textfield2.scss";

const AssetDisposalForm = ({
  vehicle,
  refurbishRequired,
  setRefurbishRequired,
  interiorCond,
  setInteriorCond,
  interiorDets,
  setInteriorDets,
  exteriorCond,
  setExteriorCond,
  exteriorDets,
  setExteriorDets,
  disposalReason,
  setDisposalReason,
  replacementResaon,
  setReplacementResaon,
  approvedRepairVendor,
  setApprovedRepairVendor,
  multiSelectedRepairVendor,
  setMultiSelectedRepairVendor,
  repairVendoremail,
  setRepairVendorEmail,
  isRepairVendorSelected,
  setIsRepairVendorSelected,
  repairdDescription,
  setRepairDescription,
  hours,
  setHours,
  mileage,
  setMileage,
  pickupDate,
  disposalPickupDate,
  setPickupDate,
  setDisposalPickupDate,
  requestDate,
  setRequestDate,
  quoteDeadline,
  setQuoteDeadline,
  disposalQuoteDeadline,
  setDisposalQuoteDeadline,
  disposalVendorTransportToVendor,
  setDisposalVendorTransportToVendor,
  repairVendorTransportToVendor,
  setRepairVendorTransportToVendor,
  repairVendorTransportToClient,
  setRepairVendorTransportToClient,
}) => {
  const { t } = useTranslation();
  const generalStatus = [
    { name: t("general.yes"), key: "yes" },
    { name: t("general.no"), key: "no" },
  ];
  const interiorConditionStatus = [
    { name: t("removalPanel.condition_poor"), key: "i_poor" },
    { name: t("removalPanel.condition_avg"), key: "i_avg" },
    { name: t("removalPanel.condition_good"), key: "i_good" },
    { name: t("removalPanel.condition_na"), key: "i_na" },
  ];
  const exteriorConditionStatus = [
    { name: t("removalPanel.condition_poor"), key: "e_poor" },
    { name: t("removalPanel.condition_avg"), key: "e_avg" },
    { name: t("removalPanel.condition_good"), key: "e_good" },
    { name: t("removalPanel.condition_na"), key: "e_na" },
  ];
  const disposalReasons = [
    { name: t("removalPanel.being_replaced"), key: "being_replaced" },
    { name: t("removalPanel.operational_change"), key: "operational_change" },
    { name: t("removalPanel.location_closing"), key: "location_closing" },
    { name: t("removalPanel.no_longer_fit_for_purpose"), key: "no_longer_fit_for_purpose" },
  ];
  const replacementResaons = [
    { name: t("removalPanel.end_of_useful_life"), key: "end_of_useful_life" },
    { name: t("removalPanel.accident"), key: "accident" },
    { name: t("removalPanel.equipment_failure"), key: "equipment_failure" },
  ];
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  return (
    <React.Fragment>
      <div className="asset-disposal-form p-sm-12 p-md-12 p-lg-6 p-xl-6 p-d-flex p-flex-column">
        <h5 className="p-mb-3 form-tooltip">
          {t("removalPanel.asset_disposal_form")}
          <Tooltip
            label={"upload-tooltip"}
            description={t("removalPanel.asset_disposal_form_tooltip")}
          />
        </h5>
        <div className="form-q-container w-100">
          <CardWidget status={Object.keys(refurbishRequired).length !== 0} YN lightBg>
            <label className="h5 font-weight-bold title">
              {t("removalPanel.refurbish_required")}
            </label>
            <div className="p-d-flex">
              {generalStatus.map((status) => {
                return (
                  <div key={status.key} className="disposal-radio p-d-flex p-ai-center">
                    <RadioButton
                      inputId={status.key}
                      name="refurbishmentStatus"
                      value={status}
                      onChange={(e) => setRefurbishRequired(e.value)}
                      checked={refurbishRequired.key === status.key}
                    />
                    <label className="mb-0 ml-2 mr-3" htmlFor={status.key}>
                      {status.name}
                    </label>
                  </div>
                );
              })}
            </div>
          </CardWidget>
          <CardWidget status={Object.keys(interiorCond).length !== 0 && interiorDets} YN lightBg>
            <label className="h5 font-weight-bold title">
              {t("removalPanel.interior_condition_of_the_asset")}
            </label>
            <div className="p-d-flex p-flex-wrap">
              {interiorConditionStatus.map((status) => {
                return (
                  <div key={status.key} className="disposal-radio p-d-flex p-ai-center p-my-1">
                    <RadioButton
                      inputId={status.key}
                      name="status"
                      value={status}
                      onChange={(e) => setInteriorCond(e.value)}
                      checked={interiorCond.key === status.key}
                    />
                    <label className="mb-0 ml-2 mr-3" htmlFor={status.key}>
                      {status.name}
                    </label>
                  </div>
                );
              })}
            </div>
            <label className="h5 p-mt-3 font-weight-bold">
              {t("removalPanel.interior_condition_details")}
            </label>
            <div className="txtField-2">
              <CustomTextArea className="w-100" value={interiorDets} onChange={setInteriorDets} />
            </div>
          </CardWidget>
          <CardWidget status={Object.keys(exteriorCond).length !== 0 && exteriorDets} YN lightBg>
            <label className="h5 font-weight-bold title">
              {t("removalPanel.exterior_condition_of_the_asset")}
            </label>
            <div className="p-d-flex p-flex-wrap">
              {exteriorConditionStatus.map((status) => {
                return (
                  <div key={status.key} className="disposal-radio p-d-flex p-ai-center p-my-1">
                    <RadioButton
                      inputId={status.key}
                      name="status"
                      value={status}
                      onChange={(e) => setExteriorCond(e.value)}
                      checked={exteriorCond.key === status.key}
                    />
                    <label className="mb-0 ml-2 mr-3" htmlFor={status.key}>
                      {status.name}
                    </label>
                  </div>
                );
              })}
            </div>
            <label className="h5 p-mt-3 font-weight-bold">
              {t("removalPanel.exterior_condition_details")}
            </label>
            <div className="txtField-2">
              <CustomTextArea className="w-100" value={exteriorDets} onChange={setExteriorDets} />
            </div>
          </CardWidget>
          <CardWidget status={Object.keys(disposalReason).length !== 0} YN lightBg>
            <label className="h5 font-weight-bold title">
              {t("removalPanel.reason_for_disposal")}
            </label>
            <div className="p-d-flex p-flex-wrap">
              {disposalReasons.map((reason) => {
                return (
                  <div key={reason.key} className="disposal-radio p-d-flex p-ai-center p-my-1">
                    <RadioButton
                      inputId={reason.key}
                      name="disposalReason"
                      value={reason}
                      onChange={(e) => setDisposalReason(e.value)}
                      checked={disposalReason.key === reason.key}
                    />
                    <label className="mb-0 ml-2 mr-3" htmlFor={reason.key}>
                      {reason.name}
                    </label>
                  </div>
                );
              })}
            </div>
          </CardWidget>
          {disposalReason.name === t("removalPanel.being_replaced") ? (
            <CardWidget status={Object.keys(replacementResaon).length !== 0} YN lightBg>
              <label className="h5 font-weight-bold title">
                {t("removalPanel.reason_for_replacement")}
              </label>
              <div className="p-d-flex p-flex-wrap">
                {replacementResaons.map((reason) => {
                  return (
                    <div key={reason.key} className="disposal-radio p-d-flex p-ai-center p-my-1">
                      <RadioButton
                        inputId={reason.key}
                        name="replacementResaon"
                        value={reason}
                        onChange={(e) => setReplacementResaon(e.value)}
                        checked={replacementResaon.key === reason.key}
                      />
                      <label className="mb-0 ml-2 mr-3" htmlFor={reason.key}>
                        {reason.name}
                      </label>
                    </div>
                  );
                })}
              </div>
            </CardWidget>
          ) : null}
          <CardWidget
            status={disposalVendorTransportToVendor !== null && disposalPickupDate ? true : false}
            lightBg
          >
            <React.Fragment>
              <label htmlFor="tansportToVendor" className="h5 font-weight-bold title p-mt-3">
                {t("general.transport_to_vendor_question", { request_type: "disposal" })}
              </label>
              <div className="p-d-flex darkRadio">
                <div className="p-field-radiobutton p-mr-3 p-mb-0">
                  <RadioButton
                    inputId="tansportToVendorTrue"
                    name="tansportToVendor"
                    value={disposalVendorTransportToVendor}
                    onChange={(e) => {
                      setDisposalVendorTransportToVendor(true);
                      setDisposalPickupDate(null);
                    }}
                    checked={disposalVendorTransportToVendor === true}
                  />
                  <label className="p-m-0 p-m-2" htmlFor="tansportToVendorTrue">
                    {t("general.transport_vendor_pickup")}
                  </label>
                </div>
                <div className="p-field-radiobutton p-mb-0">
                  <RadioButton
                    inputId="tansportToVendorFalse"
                    name="tansportToVendor"
                    value={disposalVendorTransportToVendor}
                    onChange={(e) => {
                      setDisposalVendorTransportToVendor(false);
                      setDisposalPickupDate(null);
                    }}
                    checked={disposalVendorTransportToVendor === false}
                  />
                  <label className="p-m-0 p-m-2" htmlFor="tansportToVendorFalse">
                    {t("general.transport_client_dropoff")}
                  </label>
                </div>
              </div>
            </React.Fragment>
            {disposalVendorTransportToVendor !== null && (
              <React.Fragment>
                <label className="h5 font-weight-bold title p-mt-3">
                  {disposalVendorTransportToVendor
                    ? t("general.available_pickup_date")
                    : t("general.client_dropoff_date")}
                </label>
                <div className="cal-disable-status">
                  <DatePicker
                    onChange={setDisposalPickupDate}
                    initialDate={disposalPickupDate}
                    minDate={new Date()}
                  />
                </div>
              </React.Fragment>
            )}
          </CardWidget>
          <CardWidget status={disposalQuoteDeadline} lightBg>
            <label className="h5 font-weight-bold title">
              {t("general.quote_deadline_label")}
              <Tooltip
                label="disposal_quote_deadline"
                description={t("general.quote_deadline_explanation")}
              />
            </label>
            <div className="cal-disable-status">
              <DatePicker
                onChange={setDisposalQuoteDeadline}
                initialDate={disposalQuoteDeadline}
                minDate={new Date()}
              />
            </div>
          </CardWidget>
        </div>
      </div>
      <div
        className={`asset-refurbish-form ${
          !isMobile ? "p-sm-12 p-md-12 p-lg-6 p-xl-6" : "w-100 p-m-3"
        }`}
      >
        {Object.keys(refurbishRequired).length !== 0 ? (
          refurbishRequired.name.toLowerCase() === "yes" ? (
            <RefurbishRepairRequest
              vehicle={vehicle}
              approvedRepairVendor={approvedRepairVendor}
              setApprovedRepairVendor={setApprovedRepairVendor}
              multiSelectedRepairVendor={multiSelectedRepairVendor}
              setMultiSelectedRepairVendor={setMultiSelectedRepairVendor}
              repairVendoremail={repairVendoremail}
              setRepairVendorEmail={setRepairVendorEmail}
              isRepairVendorSelected={isRepairVendorSelected}
              setIsRepairVendorSelected={setIsRepairVendorSelected}
              repairdDescription={repairdDescription}
              setRepairDescription={setRepairDescription}
              hours={hours}
              setHours={setHours}
              mileage={mileage}
              setMileage={setMileage}
              pickupDate={pickupDate}
              setPickupDate={setPickupDate}
              requestDate={requestDate}
              setRequestDate={setRequestDate}
              quoteDeadline={quoteDeadline}
              setQuoteDeadline={setQuoteDeadline}
              repairVendorTransportToVendor={repairVendorTransportToVendor}
              setRepairVendorTransportToVendor={setRepairVendorTransportToVendor}
              repairVendorTransportToClient={repairVendorTransportToClient}
              setRepairVendorTransportToClient={setRepairVendorTransportToClient}
            />
          ) : null
        ) : null}
      </div>
    </React.Fragment>
  );
};

export default AssetDisposalForm;
