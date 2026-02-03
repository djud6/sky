import React, { useState, useEffect } from "react";
import axios from "axios";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import { Table } from "../../ShareComponents/Table";
import { faBolt } from "@fortawesome/free-solid-svg-icons";
import { capitalize } from "../../../helpers/helperFunctions";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import FuelOrderDetails from "./FuelOrderDetails";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import VINLink from "../../ShareComponents/helpers/VINLink";
import "../../../styles/ShareComponents/Table/table.scss";

const FuelOrdersHistoryPanel = () => {
  const { t } = useTranslation();
  const [fuelOrders, setFuelOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [dataReady, setDataReady] = useState(false);
  const [mobileDetails, setMobileDetails] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (!dataReady) {
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Fuel/Get/All/Orders`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((res) => {
          setFuelOrders(res.data);
          setDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
  }, [dataReady]);

  useEffect(() => {
    if (selectedOrder) {
      setMobileDetails(true);
    }
  }, [selectedOrder]);

  const tableHeaders = [
    {
      header: t("general.vin"),
      colFilter: { field: "VIN" },
    },
    {
      header: t("fuelOrder.fuel_type"),
      colFilter: { field: "fuel_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("fuelOrder.volume"),
      colFilter: { field: "volume" },
    },
    {
      header: t("fuelOrder.volume_unit"),
      colFilter: { field: "volume_unit", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.cost"),
      colFilter: { field: "total_cost" },
    },
    {
      header: t("fuelOrder.currency"),
      colFilter: { field: "currency", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.date_created"),
      colFilter: {
        field: "date_created",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
  ];
  const tableData = fuelOrders.map((order) => {
    return {
      id: order.id,
      dataPoint: { ...order, total_cost: order.total_cost.toFixed(2) },
      cells: [
        <VINLink vin={order.VIN} />,
        capitalize(order.fuel_type),
        order.volume,
        capitalize(order.volume_unit),
        order.total_cost.toFixed(2),
        order.currency,
        moment(order.date_created).format("YYYY-MM-DD"),
      ],
    };
  });

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["Fuel Tracking", "Transaction", "Order History", "Fuel Cards"]}
          activeTab={"Order History"}
          urls={["/energy", "/energy/fuel-transaction", "/energy/energy-orders", "/energy/fuel-cards"]}
        />
      )}
      <PanelHeader icon={faBolt} text={t("navigationItems.fuel_orders")} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Fuel Tracking", "Transaction", "Order History", "Fuel Cards"]}
          activeTab={"Order History"}
          urls={["/energy", "/energy/fuel-transaction", "/energy/energy-orders", "/energy/fuel-cards"]}
        />
      )}
      {isMobile ? (
        <React.Fragment>
          {selectedOrder && mobileDetails ? (
            <div className="p-mx-3">
              <FuelOrderDetails
                selectedOrder={selectedOrder}
                setSelectedOrder={setSelectedOrder}
                setMobileDetails={setMobileDetails}
              />
            </div>
          ) : (
            <div className="darkTable p-mb-5">
              <Table
                dataReady={dataReady}
                tableHeaders={tableHeaders}
                tableData={tableData}
                onSelectionChange={(order) => setSelectedOrder(order)}
                hasSelection
              />
            </div>
          )}
        </React.Fragment>
      ) : (
        <React.Fragment>
          <div className="darkTable p-mt-5">
            <Table
              dataReady={dataReady}
              tableHeaders={tableHeaders}
              tableData={tableData}
              onSelectionChange={(order) => setSelectedOrder(order)}
              hasSelection
            />
          </div>
          {selectedOrder && (
            <FuelOrderDetails
              selectedOrder={selectedOrder}
              setSelectedOrder={setSelectedOrder}
              setMobileDetails={setMobileDetails}
            />
          )}
        </React.Fragment>
      )}
    </div>
  );
};
export default FuelOrdersHistoryPanel;
