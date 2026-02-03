import React from "react";
import { useTranslation } from "react-i18next";
import { InputText } from "primereact/inputtext";
import DatePicker from "../../ShareComponents/DatePicker";
import CardWidget from "../../ShareComponents/CardWidget";
import VendorOption from "./VendorOption";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import { RadioButton } from "primereact/radiobutton";
import "../../../styles/helpers/textfield2.scss";

const RefurbishRepairRequest = ({
  vehicle,
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
  setPickupDate,
  requestDate,
  setRequestDate,
  quoteDeadline,
  setQuoteDeadline,
  repairVendorTransportToVendor,
  setRepairVendorTransportToVendor,
  repairVendorTransportToClient,
  setRepairVendorTransportToClient,
}) => {
  const { t } = useTranslation();

  return (
    <React.Fragment>
      <h5 className="p-mb-3">{t("removalPanel.refurbish_repair_request")}</h5>
      <div className="w-100 refurbish-q-container">
        <CardWidget status={isRepairVendorSelected} lightBg>
          <VendorOption
            method={t("removalPanel.refurbish")}
            email={repairVendoremail}
            setEmail={setRepairVendorEmail}
            approvedVendor={approvedRepairVendor}
            setApprovedVendor={setApprovedRepairVendor}
            multiSelectedVendor={multiSelectedRepairVendor}
            setMultiSelectedVendor={setMultiSelectedRepairVendor}
            setIsVendorSelected={setIsRepairVendorSelected}
            vendorType="repair"
          />
        </CardWidget>
        <CardWidget status={repairdDescription} lightBg>
          <label className="h5 font-weight-bold">
            {t("repairRequestPanel.repair_description_label")}
          </label>
          <div className="txtField-2">
            <CustomTextArea
              className="w-100"
              value={repairdDescription}
              onChange={setRepairDescription}
              required
              autoResize
              rows={3}
            />
          </div>
        </CardWidget>
        {vehicle.hours_or_mileage.toLowerCase() === "hours" ||
        vehicle.hours_or_mileage.toLowerCase() === "both" ? (
          <CardWidget status={hours} lightBg>
            <label className="h5 font-weight-bold">{t("general.hours")}</label>
            <div className="txtField-2">
              <InputText
                className="w-100"
                value={hours}
                onChange={(e) => setHours(e.target.value)}
                keyfilter={/^\d*\.?\d*$/}
              />
            </div>
          </CardWidget>
        ) : null}
        {vehicle.hours_or_mileage.toLowerCase() === "mileage" ||
        vehicle.hours_or_mileage.toLowerCase() === "both" ? (
          <CardWidget status={mileage} lightBg>
            <label className="h5 font-weight-bold">{t("general.mileage")}</label>
            <div className="txtField-2">
              <InputText
                className="w-100"
                value={mileage}
                onChange={(e) => setMileage(e.target.value)}
                keyfilter={/^\d*\.?\d*$/}
              />
            </div>
          </CardWidget>
        ) : null}
        <CardWidget
          status={repairVendorTransportToVendor !== null && pickupDate ? true : false}
          lightBg
        >
          <React.Fragment>
            <label htmlFor="tansportToVendor" className="h5 font-weight-bold p-mt-3">
              {t("general.transport_to_vendor_question", { request_type: "repair" })}
            </label>
            <div className="p-d-flex darkRadio">
              <div className="p-field-radiobutton p-mr-3 p-mb-0">
                <RadioButton
                  inputId="tansportToVendorTrue"
                  name="tansportToVendor"
                  value={repairVendorTransportToVendor}
                  onChange={(e) => {
                    setRepairVendorTransportToVendor(true);
                    setPickupDate(null);
                  }}
                  checked={repairVendorTransportToVendor === true}
                />
                <label className="p-m-0 p-m-2" htmlFor="tansportToVendorTrue">
                  {t("general.transport_vendor_pickup")}
                </label>
              </div>
              <div className="p-field-radiobutton p-mb-0">
                <RadioButton
                  inputId="tansportToVendorFalse"
                  name="tansportToVendor"
                  value={repairVendorTransportToVendor}
                  onChange={(e) => {
                    setRepairVendorTransportToVendor(false);
                    setPickupDate(null);
                  }}
                  checked={repairVendorTransportToVendor === false}
                />
                <label className="p-m-0 p-m-2" htmlFor="tansportToVendorFalse">
                  {t("general.transport_client_dropoff")}
                </label>
              </div>
            </div>
          </React.Fragment>
          {repairVendorTransportToVendor !== null && (
            <React.Fragment>
              <label className="h5 font-weight-bold p-mt-3">
                {repairVendorTransportToVendor
                  ? t("general.available_pickup_date")
                  : t("general.client_dropoff_date")}
              </label>
               <div className="cal-disable-status">
                <DatePicker
                  onChange={(e) => {
                    setPickupDate(e);
                    if (requestDate && Date.parse(e) > Date.parse(requestDate)) {
                      setRequestDate(null);
                    }
                  }}
                  initialDate={pickupDate}
                  minDate={new Date()}
                />
              </div>
            </React.Fragment>
          )}
        </CardWidget>
        <CardWidget status={repairVendorTransportToClient !== null && requestDate} lightBg>
          <React.Fragment>
            <label htmlFor="tansportToClient" className="h5 font-weight-bold p-mt-3">
              {t("general.transport_to_client_question", { request_type: "repair" })}
            </label>
            <div className="p-d-flex darkRadio">
              <div className="p-field-radiobutton p-mr-3 p-mb-0">
                <RadioButton
                  inputId="tansportToClientTrue"
                  name="tansportToClient"
                  value={repairVendorTransportToClient}
                  onChange={(e) => {
                    setRepairVendorTransportToClient(true);
                  }}
                  checked={repairVendorTransportToClient === true}
                />
                <label className="p-m-0 p-m-2" htmlFor="tansportToClientTrue">
                  {t("general.transport_vendor_delivery")}
                </label>
              </div>
              <div className="p-field-radiobutton p-mb-0">
                <RadioButton
                  inputId="tansportToClientFalse"
                  name="tansportToClient"
                  value={repairVendorTransportToClient}
                  onChange={(e) => {
                    setRepairVendorTransportToClient(false);
                    setRequestDate(null);
                  }}
                  checked={repairVendorTransportToClient === false}
                />
                <label className="p-m-0 p-m-2" htmlFor="tansportToClientFalse">
                  {t("general.transport_client_pickup")}
                </label>
              </div>
            </div>
          </React.Fragment>
          {repairVendorTransportToClient !== null && (
            <React.Fragment>
              <label className="h5 font-weight-bold mt-3">
                {repairVendorTransportToClient
                  ? t("repairRequestPanel.requested_delivery_date_label")
                  : t("repairRequestPanel.requested_pickup_date_label")}
              </label>
              <div className="cal-disable-status">
                <DatePicker
                  onChange={setRequestDate}
                  initialDate={requestDate}
                  minDate={pickupDate || new Date()}
                  required
                />
              </div>
            </React.Fragment>
          )}
        </CardWidget>
        <CardWidget status={quoteDeadline} lightBg>
          <label className="h5 font-weight-bold">
            {t("general.quote_deadline_label")}
            <Tooltip
              label="repair_quote_deadline"
              description={t("general.quote_deadline_explanation")}
            />
          </label>
          <div className="cal-disable-status">
            <DatePicker
              onChange={setQuoteDeadline}
              initialDate={quoteDeadline}
              minDate={new Date()}
              required
            />
          </div>
        </CardWidget>
      </div>
    </React.Fragment>
  );
};

export default RefurbishRepairRequest;
