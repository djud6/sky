import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { TabView, TabPanel } from "primereact/tabview";
import * as Constants from "../../../constants";
import { faBolt } from "@fortawesome/free-solid-svg-icons";
import FuelCostInput from "../../AssetDetailPanel/CostsTab/FuelCostInput";
import FuelHistoryTable from "./FuelHistoryTable";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/EnergyPanel/FuelTransaction.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";

const FuelTransactionPanel = () => {
  const { t } = useTranslation();
  const [vehicle, setVehicle] = useState(null);
  const [fuelRefresh, setFuelRefresh] = useState(new Date());
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["Fuel Tracking", "Transaction", "Order History", "Fuel Cards"]}
          activeTab={"Transaction"}
          urls={["/energy", "/energy/fuel-transaction", "/energy/energy-orders", "/energy/fuel-cards"]}
        />
      )}
      <PanelHeader text={t("navigationItems.fuel_transaction")} icon={faBolt} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Fuel Tracking", "Transaction", "Order History", "Fuel Cards"]}
          activeTab={"Transaction"}
          urls={["/energy", "/energy/fuel-transaction", "/energy/energy-orders", "/energy/fuel-cards"]}
        />
      )}
      <div className={`${isMobile ? "p-pb-4" : "p-mt-5"}`}>
        <VINSearch onVehicleSelected={(vehicle) => setVehicle(vehicle)} />
      </div>
      {vehicle ? (
        <div className="fuel-transaction">
          <h4 className="page-title">
            {t("fuelTransaction.transaction_title", { vin: vehicle.VIN })}
          </h4>
          <TabView className="darkSubTab darkTable">
            <TabPanel header={t("fuelTransaction.new_transaction_tab").toUpperCase()}>
              <div className="p-d-flex p-flex-column p-ai-center transaction-form">
                <FuelCostInput vin={vehicle.VIN} refresh={setFuelRefresh} />
              </div>
            </TabPanel>
            <TabPanel
              header={
                isMobile
                  ? t("general.history").toUpperCase()
                  : t("fuelTransaction.spending_history").toUpperCase()
              }
            >
              <div className={`${isMobile && "p-mb-5"}`}>
                <FuelHistoryTable vin={vehicle.VIN} key={fuelRefresh} />
              </div>
            </TabPanel>
          </TabView>
        </div>
      ) : null}
    </div>
  );
};

export default FuelTransactionPanel;
