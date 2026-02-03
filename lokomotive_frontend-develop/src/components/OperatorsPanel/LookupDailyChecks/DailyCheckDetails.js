import React, { useEffect, useState } from "react";
import moment from "moment";
import { useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import DetailsView from "../../ShareComponents/DetailView/DetailsView";
import DetailsViewMobile from "../../ShareComponents/DetailView/DetailsViewMobile";
import "../../../styles/helpers/button4.scss";

const DailyCheckDetails = ({
  vehicle,
  setSelectedInspection,
  inspection,
  setMobileDetails,
  disableMobileVersion,
  detailsReady,
}) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const { listAssetTypeChecks } = useSelector((state) => state.apiCallData);
  const [validChecks, setValidChecks] = useState(false);

  const onBack = () => {
    setMobileDetails(false);
    setSelectedInspection(null);
  };

  useEffect(() => {
    if (vehicle) {
      Object.keys(inspection).forEach((name, i) => {
        if (
          (inspection[name] === true || inspection[name] === false) &&
          listAssetTypeChecks.indexOf(name) > -1
        ) {
          setValidChecks(true);
        }
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicle]);

  const OpcheckDetails = (
    <div className="main-details">
      <h5 className="op-title">{t("lookupDailyCheckPanelIndex.visual_op_check")}</h5>
      {validChecks ? (
        <React.Fragment>
          {Object.keys(inspection).map((name, i) => {
            return (
              (inspection[name] === true || inspection[name] === false) &&
              listAssetTypeChecks.indexOf(name) > -1 && (
                <div key={i} className="op-values text-white p-d-flex p-jc-between">
                  <span key={i} className="p-pb-1">
                    {t(`configureChecks.${name}`)}:{" "}
                  </span>
                  <span>
                    {inspection[name] ? (
                      <span>{t("lookupDailyCheckPanelIndex.satisfactory")}</span>
                    ) : (
                      <span className="text-danger">
                        {t("lookupDailyCheckPanelIndex.unsatisfactory")}
                      </span>
                    )}
                  </span>
                </div>
              )
            );
          })}
          {inspection && inspection.comments.length > 0 && (
            <React.Fragment>
              <hr />
              <h5 className="op-title p-mt-1">{t("lookupDailyCheckPanelIndex.check_comments")}</h5>
              {inspection.comments.map((comments, i) => {
                return (
                  <div key={i} className="op-values text-white">
                    <span key={i} className="p-pb-1">
                      {t(`configureChecks.${comments.check}`)}:{" "}
                    </span>
                    <span>{comments.comment}</span>
                    <br />
                  </div>
                );
              })}
            </React.Fragment>
          )}
        </React.Fragment>
      ) : (
        <span className="op-values text-white">{t("general.not_applicable")}</span>
      )}
    </div>
  );

  let detailViewTitles = [
    t("general.id"),
    t("lookupDailyCheckPanel.asset_type_label"),
    t("lookupDailyCheckPanel.operator_label"),
    t("lookupDailyCheckPanel.operator_contacts"),
    t("lookupDailyCheckPanel.location_label"),
    ...(vehicle.hours_or_mileage.toLowerCase() === "mileage" ||
    vehicle.hours_or_mileage.toLowerCase() === "both"
      ? [t("general.mileage")]
      : []),
    ...(vehicle.hours_or_mileage.toLowerCase() === "hours" ||
    vehicle.hours_or_mileage.toLowerCase() === "both"
      ? [t("general.hours")]
      : []),
    t("lookupDailyCheckPanel.date_completed_label"),
    t("lookupDailyCheckPanel.status_label"),
  ];
  let detailViewValues = [
    inspection.custom_id,
    vehicle.asset_type,
    `${inspection.first_name} ${inspection.last_name}`,
    inspection.created_by,
    vehicle.current_location,
    ...(vehicle.hours_or_mileage.toLowerCase() === "mileage" ||
    vehicle.hours_or_mileage.toLowerCase() === "both"
      ? [inspection.mileage]
      : []),
    ...(vehicle.hours_or_mileage.toLowerCase() === "hours" ||
    vehicle.hours_or_mileage.toLowerCase() === "both"
      ? [inspection.hours]
      : []),
    moment(inspection.date_created).format("MMM Do, YYYY"),
    !inspection.is_tagout ? t("lookupDailyCheckPanel.op") : t("lookupDailyCheckPanel.inop"),
  ];

  return (
    <React.Fragment>
      {isMobile && !disableMobileVersion ? (
        <div className="p-my-3">
          <div className="no-style-btn p-my-3">
            <Button
              label={t("general.back")}
              className="p-button-link"
              icon="pi pi-chevron-left"
              onClick={() => onBack()}
            />
          </div>
          <DetailsViewMobile
            header={t("general.header_vin", { vin: vehicle.VIN })}
            titles={detailViewTitles}
            values={detailViewValues}
            additionalDescr={OpcheckDetails}
          />
        </div>
      ) : (
        <DetailsView
          headers={[
            t("lookupDailyCheckPanel.page_detail_title"),
            t("general.header_vin", { vin: vehicle.VIN }),
          ]}
          titles={detailViewTitles}
          values={detailViewValues}
          onHideDialog={setSelectedInspection}
          additionalDescr={OpcheckDetails}
          detailsReady={detailsReady}
        />
      )}
    </React.Fragment>
  );
};

export default DailyCheckDetails;
