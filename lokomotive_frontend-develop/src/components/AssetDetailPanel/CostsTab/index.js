import React, { useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { TabView, TabPanel } from "primereact/tabview";
import FuelCostInput from "./FuelCostInput";
import RentalCostInput from "./RentalCostInput";
import InsuranceCostInput from "./InsuranceCostInput";
import LicenseCostInput from "./LicenseCostInput";
import AcquisitionCostInput from "./AcquisitionCostInput";
import DeliveryCostInput from "./DeliveryCostInput";
import {
  FuelHistory,
  InsuranceHistory,
  RentalHistory,
  LicenseHistory,
  AcquisitionHistory,
  DeliveryHistory,
} from "./HistoryTables";
import "../../../styles/ShareComponents/TabStyles/tabStyles.scss";
import "../../../styles/ShareComponents/TabStyles/subTab2.scss";
import "../../../styles/AssetDetailsPanel/CostsTab.scss";
import useWindowSize from "../../ShareComponents/helpers/useWindowSize";

const CostsTab = ({ vin }) => {
  const { t } = useTranslation();
  const [fuelRefresh, setFuelRefresh] = useState(new Date());
  const [rentalRefresh, setRentalRefresh] = useState(new Date());
  const [licenseRefresh, setLicenseRefresh] = useState(new Date());
  const [insuranceRefresh, setInsuranceRefresh] = useState(new Date());
  const [acquisitionRefresh, setAcquisitionRefresh] = useState(new Date());
  const [deliveryRefresh, setDeliveryRefresh] = useState(new Date());
  const [activeIndex, setActiveIndex] = useState(0);
  const costTabRef = useRef(null);
  const windowWidth = useWindowSize().width;

  useEffect(() => {
    let currentCostTab = costTabRef.current;
    if (currentCostTab) {
      let width = currentCostTab.offsetWidth;
      let spacedTabsView = currentCostTab
        .getElementsByClassName("spaced-tabs")[0]
        .getElementsByClassName("p-tabview-nav")[0];
      if (width <= 768 && width > 330) {
        spacedTabsView.style.gridTemplateColumns = "repeat(3, 1fr)";
      } else if (width <= 330) {
        spacedTabsView.style.gridTemplateColumns = "repeat(2, 1fr)";
      } else {
        spacedTabsView.style = null;
      }
    }
  }, [costTabRef, windowWidth]);

  return (
    <div className="detail-cost-tab" ref={costTabRef}>
      <h5 className="p-mb-3 cost-tab-title">{t("general.costs")}</h5>
      <TabView
        className="darkTab darkTabwidth spaced-tabs"
        onTabChange={(e) => setActiveIndex(e.index)}
        activeIndex={activeIndex}
      >
        <TabPanel header={t("costsTab.fuel_title")} />
        <TabPanel header={t("costsTab.rental_title")} />
        <TabPanel header={t("costsTab.insurance_title")} />
        <TabPanel header={t("costsTab.license_title")} />
        <TabPanel header={t("costsTab.acquisition_title")} />
        <TabPanel header={t("costsTab.delivery_title")} />
      </TabView>

      <hr />

      {activeIndex === 0 && (
        <TabView className="darkSubTab-2">
          <TabPanel header={t("costsTab.fuel_submit_label")}>
            <FuelCostInput vin={vin} refresh={setFuelRefresh} />
          </TabPanel>
          <TabPanel header={t("costsTab.fuel_history_title")}>
            <FuelHistory vin={vin} key={fuelRefresh} />
          </TabPanel>
        </TabView>
      )}

      {activeIndex === 1 && (
        <TabView className="darkSubTab-2">
          <TabPanel header={t("costsTab.rental_submit_label")}>
            <RentalCostInput vin={vin} refresh={setRentalRefresh} />
          </TabPanel>
          <TabPanel header={t("costsTab.rental_history_title")}>
            <RentalHistory vin={vin} key={rentalRefresh} />
          </TabPanel>
        </TabView>
      )}

      {activeIndex === 2 && (
        <TabView className="darkSubTab-2">
          <TabPanel header={t("costsTab.insurance_submit_label")}>
            <InsuranceCostInput vin={vin} refresh={setInsuranceRefresh} />
          </TabPanel>
          <TabPanel header={t("costsTab.insurance_history_title")}>
            <InsuranceHistory vin={vin} key={insuranceRefresh} />
          </TabPanel>
        </TabView>
      )}

      {activeIndex === 3 && (
        <TabView className="darkSubTab-2">
          <TabPanel header={t("costsTab.license_submit_label")}>
            <LicenseCostInput vin={vin} refresh={setLicenseRefresh} />
          </TabPanel>
          <TabPanel header={t("costsTab.license_history_title")}>
            <LicenseHistory vin={vin} key={licenseRefresh} />
          </TabPanel>
        </TabView>
      )}

      {activeIndex === 4 && (
        <TabView className="darkSubTab-2">
          <TabPanel header={t("costsTab.acquisition_submit_label")}>
            <AcquisitionCostInput vin={vin} refresh={setAcquisitionRefresh} />
          </TabPanel>
          <TabPanel header={t("costsTab.acquisition_history_title")}>
            <AcquisitionHistory vin={vin} key={acquisitionRefresh} />
          </TabPanel>
        </TabView>
      )}

      {activeIndex === 5 && (
        <TabView className="darkSubTab-2">
          <TabPanel header={t("costsTab.delivery_submit_label")}>
            <DeliveryCostInput vin={vin} refresh={setDeliveryRefresh} />
          </TabPanel>
          <TabPanel header={t("costsTab.delivery_history_title")}>
            <DeliveryHistory vin={vin} key={deliveryRefresh} />
          </TabPanel>
        </TabView>
      )}
    </div>
  );
};

export default CostsTab;
