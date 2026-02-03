import React from "react";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import { capitalize } from "../../../helpers/helperFunctions";
import DetailsView from "../../ShareComponents/DetailView/DetailsView";
import DetailsViewMobile from "../../ShareComponents/DetailView/DetailsViewMobile";
import "../../../styles/helpers/button4.scss";

const FuelOrderDetails = ({ selectedOrder, setSelectedOrder, setMobileDetails }) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const onBack = () => {
    setMobileDetails(false);
    setSelectedOrder(null);
  };

  const detailViewTitles = [
    t("fuelOrder.fuel_type"),
    t("fuelOrder.volume"),
    t("fuelOrder.volume_unit"),
    t("general.cost"),
    t("fuelOrder.currency"),
    t("fuelOrder.taxes"),
    t("general.created_by"),
    t("general.date_created"),
  ];

  const detailViewValues = [
    capitalize(selectedOrder.fuel_type),
    selectedOrder.volume,
    capitalize(selectedOrder.volume_unit),
    parseFloat(selectedOrder.total_cost).toFixed(2),
    selectedOrder.currency,
    parseFloat(selectedOrder.taxes).toFixed(2),
    selectedOrder.created_by || t("general.not_applicable"),
    moment(selectedOrder.date_created).format("YYYY-MM-DD") || t("general.not_applicable"),
  ];

  return (
    <React.Fragment>
      {isMobile ? (
        <div>
          <div className="no-style-btn p-my-3">
            <Button
              label={t("general.back")}
              className="p-button-link"
              icon="pi pi-chevron-left"
              onClick={() => onBack()}
            />
          </div>
          <DetailsViewMobile
            header={t("general.header_vin", { vin: selectedOrder.VIN })}
            titles={detailViewTitles}
            values={detailViewValues}
          />
        </div>
      ) : (
        <DetailsView
          headers={[
            t("fuelOrder.fuel_order_details"),
            t("general.header_vin", { vin: selectedOrder.VIN }),
          ]}
          titles={detailViewTitles}
          values={detailViewValues}
          onHideDialog={setSelectedOrder}
        />
      )}
    </React.Fragment>
  );
};

export default FuelOrderDetails;
