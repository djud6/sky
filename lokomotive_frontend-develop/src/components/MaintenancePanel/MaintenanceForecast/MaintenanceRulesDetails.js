import React from "react";
import { useTranslation } from "react-i18next";
import DetailsView from "../../ShareComponents/DetailView/DetailsView";

const MaintenanceRulesDetails = ({ rule, setSelectedRule, detailsReady }) => {
  const { t } = useTranslation();

  let detailViewTitles = [
    t("general.id"),
    t("maintenanceForecastPanel.inspection_type"),
    t("maintenanceForecastPanel.mileage_cycle"),
    t("maintenanceForecastPanel.hours_cycle"),
    t("maintenanceForecastPanel.time_cycle"),
    t("general.date_created"),
    t("general.created_by"),
    t("general.date_updated"),
    t("general.modified_by"),
  ];

  let detailViewValues = [
    rule.custom_id,
    rule.inspection_name,
    ...(rule.mileage_cycle !== -1.0 ? [rule.mileage_cycle]: [t("general.not_applicable")]),
    ...(rule.hour_cycle !== -1.0 ? [rule.hour_cycle]: [t("general.not_applicable")]),
    ...(rule.time_cycle !== -1.0 ? [rule.time_cycle]: [t("general.not_applicable")]),
    rule.date_created,
    rule.created_by,
    rule.date_updated,
    rule.modified_by,
  ];
  
  return (
    <DetailsView
      headers={[
        t("maintenanceForecastPanel.maintenance_rule"),
        t("general.header_vin", { vin: rule.VIN }),
      ]}
      titles={detailViewTitles}
      values={detailViewValues}
      onHideDialog={setSelectedRule}
      detailsReady={detailsReady}
    />
  )
}

export default MaintenanceRulesDetails;