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
import FuelCardsDetails from "./FuelCardsDetails";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import VINLink from "../../ShareComponents/helpers/VINLink";
import "../../../styles/ShareComponents/Table/table.scss";

const FuelCardsPanel = () => {
  const { t } = useTranslation();
  const [fuelCards, setFuelCards] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [dataReady, setDataReady] = useState(false);
  const [mobileDetails, setMobileDetails] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (!dataReady) {
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Fuel/Get/All/FuelCards`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((res) => {
          setFuelCards(res.data);
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
      header: t("fuel_cards.card_issuer"),
      colFilter: { field: "card_issuer", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("fuel_cards.card_number"),
      colFilter: { field: "card_id"},
    },
    {
      header: t("fuel_cards.expiration"),
      colFilter: {
        field: "expiration",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
    {
      header: t("fuel_cards.assigned_employee"),
      colFilter: { field: "assigned_employee"},
    },
    {
      header: t("fuel_cards.business_unit"),
      colFilter: { field: "business_unit"},
    },
    {
      header: t("fuel_cards.card_status"),
      colFilter: { field: "card_is_active" },
    }
  ];

  const tableData = dataReady ? fuelCards.fuel_cards.map((card) => {
    return {
      id: card.card_id,
      dataPoint: { ...card},
      cells: [
        card.issuer,
        card.card_id,
        card.expiration ? moment(card.expiration).format("YYYY-MM-DD") : t("general.not_applicable"),
        card.assigned_employee,
        card.business_unit || t("general.not_applicable"),
        (card.is_active ? "Active" : "Inactive") || t("general.not_applicable")
      ],
    };
  }) : [];

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["Fuel Tracking", "Transaction", "Order History", "Fuel Cards"]}
          activeTab={"Fuel Cards"}
          urls={["/energy", "/energy/fuel-transaction", "/energy/energy-orders", "/energy/fuel-cards"]}
        />
      )}
      <PanelHeader icon={faBolt} text={t("navigationItems.fuel_cards")} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Fuel Tracking", "Transaction", "Order History", "Fuel Cards"]}
          activeTab={"Fuel Cards"}
          urls={["/energy", "/energy/fuel-transaction", "/energy/energy-orders", "/energy/fuel-cards"]}
        />
      )}
      {isMobile ? (
        <React.Fragment>
          {selectedOrder && mobileDetails ? (
            <div className="p-mx-3">
              {/* <FuelCardsDetails
                selectedOrder={selectedOrder}
                setSelectedOrder={setSelectedOrder}
                setMobileDetails={setMobileDetails}
              /> */}
            </div>
          ) : (
            <div className="darkTable p-mb-5">
              <Table
                dataReady={dataReady}
                tableHeaders={tableHeaders}
                tableData={tableData}
                onSelectionChange={(card) => setSelectedOrder(card)}
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
              onSelectionChange={(card) => setSelectedOrder(card)}
              hasSelection
            />
          </div>
          {/* {selectedOrder && (
            <FuelCardsDetails
              selectedOrder={selectedOrder}
              setSelectedOrder={setSelectedOrder}
              setMobileDetails={setMobileDetails}
            />
          )} */}
        </React.Fragment>
      )}
    </div>
  );
};
export default FuelCardsPanel;
