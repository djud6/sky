import React, { useEffect, useState } from "react";
import axios from "axios";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { faSearch } from "@fortawesome/free-solid-svg-icons";
import { getAuthHeader } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import { capitalize } from "../../../helpers/helperFunctions";
import Table from "../../ShareComponents/Table/Table";
import VINLink from "../../ShareComponents/helpers/VINLink";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import MaintenanceDetails from "../MaintenanceStatus/MaintenanceDetails";
import MaintenanceDetailsMore from "../MaintenanceStatus/MaintenanceDetailsMore";
import MaintenanceDetailsMoreMobile from "../MaintenanceStatus/MaintenanceDetailsMoreMobile";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";

const MaintenanceTable = ({ maintenanceList, dataReady, setSelectedMaintenance }) => {
  const { t } = useTranslation();

  let maintenanceTableHeaders = [
    { header: t("general.id"), colFilter: { field: "work_order" } },
    { header: t("general.vin"), colFilter: { field: "VIN" } },
    {
      header: t("maintenanceLookupPanel.maintenance_type_label"),
      colFilter: { field: "inspection_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("maintenanceLookupPanel.location_label"),
      colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("maintenanceLookupPanel.mileage_label"),
      colFilter: { field: "mileage" },
    },
    {
      header: t("general.status"),
      colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("maintenanceLookupPanel.complete_label"),
      colFilter: {
        field: "date_completed",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
  ];

  let maintenanceTableData = maintenanceList.map((item) => {
    return {
      id: item.maintenance_id,
      dataPoint: item,
      cells: [
        item.work_order,
        <VINLink vin={item.VIN} />,
        item.inspection_type,
        item.current_location,
        item.mileage,
        capitalize(item.status),
        ...(moment(item.date_completed).isValid()
          ? [moment(item.date_completed).format("YYYY-MM-DD")]
          : [t("general.not_applicable")]),
      ],
    };
  });

  return (
    <div className="darkTable">
      <Table
        dataReady={dataReady}
        tableHeaders={maintenanceTableHeaders}
        tableData={maintenanceTableData}
        hasSelection
        onSelectionChange={(request) => setSelectedMaintenance(request)}
      />
    </div>
  );
};

const MaintenanceLookupPanel = () => {
  const { t } = useTranslation();
  const [vin, setVin] = useState(null);
  const [maintenanceList, setMaintenanceList] = useState([]);
  const [dataReady, setDataReady] = useState(false);
  const [selectedMaintenance, setSelectedMaintenance] = useState(null);
  const [mobileDetails, setMobileDetails] = useState(false);
  const [moreDetails, setMoreDetails] = useState(false);
  const [detailsSection, setDetailsSection] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (vin) {
      setDataReady(false);
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/VIN/${vin}`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          const maintenance = response.data;
          for (var i in maintenance) {
            maintenance[i].date_completed = moment(maintenance[i].date_completed).format(
              "YYYY-MM-DD"
            );
          }
          setMaintenanceList(response.data);
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
  }, [vin]);

  useEffect(() => {
    if (selectedMaintenance) {
      setMobileDetails(true);
    }
  }, [selectedMaintenance]);

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["Status", "Schedule", "Forecast", "Lookup"]}
          activeTab={"Lookup"}
          urls={[
            "/maintenance",
            "/maintenance/schedule",
            "/maintenance/forecast",
            "/maintenance/lookup",
          ]}
        />
      )}
      <PanelHeader icon={faSearch} text={t("maintenanceLookupPanel.page_title")} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Status", "Schedule", "Forecast", "Lookup"]}
          activeTab={"Lookup"}
          urls={[
            "/maintenance",
            "/maintenance/schedule",
            "/maintenance/forecast",
            "/maintenance/lookup",
          ]}
        />
      )}
      {moreDetails ? (
        isMobile ? (
          <MaintenanceDetailsMoreMobile
            maintenance={selectedMaintenance}
            detailsSection={detailsSection}
            setMoreDetails={setMoreDetails}
            setDataReady={setDataReady}
          />
        ) : (
          <MaintenanceDetailsMore
            maintenance={selectedMaintenance}
            setMoreDetails={setMoreDetails}
            setDataReady={setDataReady}
          />
        )
      ) : (
        <React.Fragment>
          {!isMobile ? (
            <div className="p-mt-5">
              <VINSearch
                onVehicleSelected={(v) => {
                  setSelectedMaintenance(null);
                  setMaintenanceList([]);
                  if (v) setVin(v.VIN);
                }}
              />
              {vin && (
                <MaintenanceTable
                  maintenanceList={maintenanceList}
                  dataReady={dataReady}
                  setSelectedMaintenance={setSelectedMaintenance}
                />
              )}
              {selectedMaintenance && (
                <MaintenanceDetails
                  maintenance={selectedMaintenance}
                  setSelectedMaintenance={setSelectedMaintenance}
                  setMoreDetails={setMoreDetails}
                  setDetailsSection={setDetailsSection}
                  setMaintenances={setMaintenanceList}
                  maintenanceType={"search"}
                />
              )}
            </div>
          ) : (
            <React.Fragment>
              {selectedMaintenance && mobileDetails ? (
                <div className="p-mb-5 p-mx-3">
                  <MaintenanceDetails
                    maintenance={selectedMaintenance}
                    setSelectedMaintenance={setSelectedMaintenance}
                    setDataReady={setDataReady}
                    setMobileDetails={setMobileDetails}
                    setMoreDetails={setMoreDetails}
                    setDetailsSection={setDetailsSection}
                    setMaintenances={setMaintenanceList}
                    maintenanceType={"search"}
                  />
                </div>
              ) : (
                <React.Fragment>
                  <div className={`p-pb-4`}>
                    <VINSearch
                      onVehicleSelected={(v) => {
                        setSelectedMaintenance(null);
                        setMaintenanceList([]);
                        if (v) setVin(v.VIN);
                      }}
                    />
                  </div>
                  {vin && (
                    <div className="p-mt-3 p-mb-5">
                      <MaintenanceTable
                        maintenanceList={maintenanceList}
                        dataReady={dataReady}
                        setSelectedMaintenance={setSelectedMaintenance}
                      />
                    </div>
                  )}
                </React.Fragment>
              )}
            </React.Fragment>
          )}
        </React.Fragment>
      )}
    </div>
  );
};

export default MaintenanceLookupPanel;
