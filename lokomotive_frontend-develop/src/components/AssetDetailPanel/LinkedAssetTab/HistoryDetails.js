import React from "react";
import moment from "moment";
import { useMediaQuery } from "react-responsive";
import { useTranslation } from "react-i18next";
import * as Constants from "../../../constants";
import { Button } from "primereact/button";
import DetailsViewMobile from "../../ShareComponents/DetailView/DetailsViewMobile";

const HistoryDetails = ({ child, setSelectedChild }) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const titles = [
    t("childHistory.VIN_id"),
    t("childHistory.parent_id"),
    t("childHistory.date"),
    t("childHistory.status"),
    t("childHistory.unit_number"),
    t("childHistory.license_plate"),
    t("childHistory.fire_extinguisher_quantity"),
    t("childHistory.fire_extinguisher_inspection_date"),
    t("childHistory.last_process"),
    t("childHistory.cycle_nuit"),
    ...(child.mileage !== -1.0 ? [t("general.mileage")] : []),
    ...(child.hours !== -1.0 ? [t("general.hours")] : []),
    t("childHistory.mileage_unit"),
    t("childHistory.total_cost"),
    t("childHistory.daily_average_hours"),
    t("childHistory.daily_average_mileage"),
    t("childHistory.replacement_hours"),
    t("childHistory.replacement_mileage"),
    t("childHistory.load_capacity"),
    t("childHistory.load_capacity_unit"),
    t("childHistory.engine"),
    t("childHistory.fuel_tank_capacity"),
    t("childHistory.fuel_tank_capacity_unit"),
    t("childHistory.is_rental"),
    t("childHistory.monthly_subscription_cost"),
  ];

  const values = [
    child.VIN_id,
    child.parent_id,
    moment(child.date).isValid()
      ? moment(child.date).format("YYYY-MM-DD")
      : t("general.not_applicable"),
    child.status,
    child.unit_number || t("general.not_applicable"),
    child.license_plate || t("general.not_applicable"),
    child.fire_extinguisher_quantity !== "NA" && child.fire_extinguisher_quantity !== null
      ? child.fire_extinguisher_quantity
      : t("general.not_applicable"),
    moment(child.fire_extinguisher_inspection_date).isValid()
      ? moment(child.fire_extinguisher_inspection_date).format("YYYY-MM-DD")
      : t("general.not_applicable"),
    child.last_process !== "Null" && child.last_process !== null
      ? child.last_process
      : t("general.not_applicable"),
    child.hours_or_mileage,
    ...(child.mileage !== -1.0 ? [child.mileage] : []),
    ...(child.hours !== -1.0 ? [child.hours] : []),
    child.mileage_unit || t("general.not_applicable"),
    child.total_cost.toFixed(1),
    child.daily_average_hours.toFixed(1),
    child.daily_average_mileage.toFixed(1),
    child.replacement_hours.toFixed(1),
    child.replacement_mileage.toFixed(1),
    child.load_capacity || t("general.not_applicable"),
    child.load_capacity_unit || t("general.not_applicable"),
    child.engine || t("general.not_applicable"),
    child.fuel_tank_capacity || t("general.not_applicable"),
    child.fuel_tank_capacity_unit || t("general.not_applicable"),
    child.is_rental || t("general.not_applicable"),
    child.monthly_subscription_cost || t("general.not_applicable"),
  ];
  return (
    <div className="p-mx-2">
      {isMobile ? (
        <React.Fragment>
          <div className="no-style-btn p-my-3">
            <Button
              label={t("childHistory.back_btn")}
              className="p-button-link"
              icon="pi pi-undo"
              onClick={() => setSelectedChild(null)}
            />
          </div>
          <DetailsViewMobile
            header={t("general.header_vin", { vin: child.VIN_id })}
            titles={titles}
            values={values}
          />
        </React.Fragment>
      ) : (
        <React.Fragment>
          <div className="p-d-flex p-flex-column p-m-3">
            {titles &&
              titles.map((title, index) => {
                return (
                  <div key={index}>
                    <div className="p-d-flex p-jc-between text-white">
                      <span className="font-weight-bold">{title}</span>
                      <span>{values[index]}</span>
                    </div>
                    <hr className="solid" />
                  </div>
                );
              })}
          </div>
          <div className="p-mt-3 p-mb-3 p-d-flex p-jc-center">
            <Button
              style={{ width: "350px" }}
              className="p-button-raised p-button-warning p-button-outlined"
              label={t("childHistory.back_btn")}
              icon="pi pi-undo"
              onClick={() => setSelectedChild(null)}
            />
          </div>
        </React.Fragment>
      )}
    </div>
  );
};

export default HistoryDetails;
