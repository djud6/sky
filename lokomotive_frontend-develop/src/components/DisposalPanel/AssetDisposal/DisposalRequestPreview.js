import React from "react";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import CardWidget from "../../ShareComponents/CardWidget";

const DisposalRequestPreview = ({
  vin,
  vinImagePreview,
  mileageImagePreview,
  interiorCond,
  interiorDets,
  exteriorCond,
  exteriorDets,
  disposalReason,
  replacementResaon,
  disposalMethod,
  multiSelectedVendor,
  email,
  selectedBusinessUnit,
  selectedJobSpec,
  refurbishRequired,
  multiSelectedRepairVendor,
  repairVendoremail,
  repairdDescription,
  hours,
  mileage,
  pickupDate,
  disposalPickupDate,
  disposalQuoteDeadline,
  requestDate,
  repairQuoteDeadline,
  disposalVendorTransportToVendor,
  repairVendorTransportToVendor,
  repairVendorTransportToClient,
}) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const ReviewRow = ({ title, info }) => {
    return (
      <div className={`p-d-flex ${!isMobile ? "p-px-2" : "p-flex-column p-mb-2"}`}>
        <label className={`h6 ${!isMobile ? "p-col-6 p-m-0 p-p-2" : "w-100"}`}>{title}:</label>
        <span className={`h6 ${!isMobile ? "p-col-6 p-m-0 p-p-2" : "w-100"}`}>{info}</span>
      </div>
    );
  };

  return (
    <React.Fragment>
      <div
        className={`preview-left-container ${
          !isMobile ? "p-sm-12 p-md-12 p-lg-6 p-xl-6" : "w-100 p-mx-3"
        }`}
      >
        <h5 className="p-mb-3">{t("removalPanel.preview_title", { VIN: vin })}</h5>
        <CardWidget status blueBg>
          <ReviewRow
            title={t("removalPanel.interior_condition_of_the_asset")}
            info={
              Object.keys(interiorCond).length !== 0
                ? interiorCond.name
                : t("general.not_applicable")
            }
          />
          <ReviewRow
            title={t("removalPanel.interior_condition_details")}
            info={interiorDets ? interiorDets : t("general.not_applicable")}
          />
          <ReviewRow
            title={t("removalPanel.exterior_condition_of_the_asset")}
            info={
              Object.keys(exteriorCond).length !== 0
                ? exteriorCond.name
                : t("general.not_applicable")
            }
          />
          <ReviewRow
            title={t("removalPanel.exterior_condition_details")}
            info={exteriorDets ? exteriorDets : t("general.not_applicable")}
          />
          <ReviewRow
            title={t("removalPanel.reason_for_disposal")}
            info={
              Object.keys(disposalReason).length !== 0
                ? disposalReason.name
                : t("general.not_applicable")
            }
          />
          {disposalReason.name === t("removalPanel.being_replaced") ? (
            <ReviewRow
              title={t("removalPanel.reason_for_replacement")}
              info={replacementResaon ? replacementResaon.name : t("general.not_applicable")}
            />
          ) : null}
          <ReviewRow title={t("removalPanel.disposal_method_title")} info={disposalMethod.name} />
          <ReviewRow
            title={t("removalPanel.recipient_vendor")}
            info={
              multiSelectedVendor.length
                ? multiSelectedVendor.map((el) => `${el.name}`).join(", ")
                : email
                ? email
                : t("general.not_applicable")
            }
          />
          {disposalMethod.name === t("removalPanel.repurpose") ? (
            <React.Fragment>
              <ReviewRow
                title={t("removalPanel.review_new_department")}
                info={
                  selectedBusinessUnit ? selectedBusinessUnit.name : t("general.not_applicable")
                }
              />
              <ReviewRow
                title={t("removalPanel.review_job_specification")}
                info={selectedJobSpec ? selectedJobSpec.name : t("general.not_applicable")}
              />
            </React.Fragment>
          ) : null}
          <ReviewRow
            title={t("general.in_transit_to_vendor_label")}
            info={
              disposalVendorTransportToVendor
                ? t("general.transport_vendor_pickup")
                : t("general.transport_client_dropoff")
            }
          />
          <ReviewRow
            title={
              disposalVendorTransportToVendor
                ? t("general.available_pickup_date")
                : t("general.client_dropoff_date")
            }
            info={
              disposalPickupDate
                ? moment(disposalPickupDate.toISOString()).format("YYYY-MM-DD")
                : t("general.not_applicable")
            }
          />
          <ReviewRow
            title={t("general.quote_deadline_label")}
            info={
              disposalQuoteDeadline
                ? moment(disposalQuoteDeadline.toISOString()).format("YYYY-MM-DD")
                : t("general.not_applicable")
            }
          />
        </CardWidget>
        {Object.keys(refurbishRequired).length !== 0 ? (
          refurbishRequired.name.toLowerCase() === "yes" ? (
            <React.Fragment>
              <h5 className="p-mt-5 p-mb-3">{t("removalPanel.refurbish_repair_request")}</h5>
              <CardWidget status blueBg>
                <ReviewRow
                  title={t("repairRequestPanel.recipient_vendor")}
                  info={
                    multiSelectedRepairVendor.length
                      ? multiSelectedRepairVendor.map((el) => `${el.name}`).join(", ")
                      : repairVendoremail
                      ? repairVendoremail
                      : t("general.not_applicable")
                  }
                />
                <ReviewRow
                  title={t("repairRequestPanel.repair_description_label")}
                  info={repairdDescription ? repairdDescription : t("general.not_applicable")}
                />
                {hours ? (
                  <ReviewRow
                    title={t("general.hours")}
                    info={hours ? hours : t("general.not_applicable")}
                  />
                ) : null}
                {mileage ? (
                  <ReviewRow
                    title={t("general.mileage")}
                    info={mileage ? mileage : t("general.not_applicable")}
                  />
                ) : null}
                <ReviewRow
                  title={t("general.in_transit_to_vendor_label")}
                  info={
                    repairVendorTransportToVendor
                      ? t("general.transport_vendor_pickup")
                      : t("general.transport_client_dropoff")
                  }
                />
                <ReviewRow
                  title={
                    repairVendorTransportToVendor
                      ? t("general.available_pickup_date")
                      : t("general.client_dropoff_date")
                  }
                  info={
                    pickupDate
                      ? moment(pickupDate.toISOString()).format("YYYY-MM-DD")
                      : t("general.not_applicable")
                  }
                />
                <ReviewRow
                  title={t("general.in_transit_to_client_label")}
                  info={
                    repairVendorTransportToClient
                      ? t("general.transport_vendor_delivery")
                      : t("general.transport_client_pickup")
                  }
                />
                <ReviewRow
                  title={
                    repairVendorTransportToClient
                      ? t("repairRequestPanel.requested_delivery_date_label")
                      : t("repairRequestPanel.requested_pickup_date_label")
                  }
                  info={
                    requestDate
                      ? moment(requestDate.toISOString()).format("YYYY-MM-DD")
                      : t("general.not_applicable")
                  }
                />
                <ReviewRow
                  title={t("general.quote_deadline_label")}
                  info={
                    repairQuoteDeadline
                      ? moment(repairQuoteDeadline.toISOString()).format("YYYY-MM-DD")
                      : t("general.not_applicable")
                  }
                />
              </CardWidget>
            </React.Fragment>
          ) : null
        ) : null}
      </div>
      <div className="p-sm-12 p-md-12 p-lg-6 p-xl-6">
        {(vinImagePreview.length !== 0 || mileageImagePreview.length !== 0) && (
          <div className="upload-files-preview p-d-flex p-flex-column">
            <label className="h4 p-ml-5 p-mt-4 p-mb-3">{t("general.image_preview")}</label>
            <div className="p-d-flex p-jc-start image-section">
              {vinImagePreview[0] ? (
                <div className="p-mb-5 image-style">
                  <img width="100%" src={vinImagePreview[0]} alt="vin_image_preview" />
                </div>
              ) : null}
              {mileageImagePreview[0] ? (
                <div className="p-mb-5 image-style">
                  <img width="100%" src={mileageImagePreview[0]} alt="mileage_image_preview" />
                </div>
              ) : null}
              {mileageImagePreview[1] ? (
                <div className="p-mb-5 image-style">
                  <img width="100%" src={mileageImagePreview[1]} alt="hours_image_preview" />
                </div>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </React.Fragment>
  );
};

export default DisposalRequestPreview;
