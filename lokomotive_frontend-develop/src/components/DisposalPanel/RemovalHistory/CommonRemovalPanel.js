import React, { useState, useEffect } from "react";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import VINLink from "../../ShareComponents/helpers/VINLink";
import Table from "../../ShareComponents/Table/Table";
import AssetRemovalDetails from "./AssetRemovalDetails";
import { capitalize } from "../../../helpers/helperFunctions";

const CommonRemovalPanel = ({ removalsData, setRemovalData, dataReady, setDataReady, tab }) => {
  const { t } = useTranslation();
  const [mobileDetails, setMobileDetails] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (selectedAsset) {
      setMobileDetails(true);
    }
  }, [selectedAsset]);

  let removalTableHeaders = [
    { header: t("general.id"), colFilter: { field: "custom_id" } },
    { header: t("general.vin"), colFilter: { field: "VIN" } },
    {
      header: t("removalPanel.disposal_type_label"),
      colFilter: { field: "disposal_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.location"),
      colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.status"),
      colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.vendor"),
      colFilter: { field: "vendor_name", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("removalPanel.date_vendor_contacted_label"),
      colFilter: {
        field: "vendor_contacted_date",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
    {
      header: t("removalPanel.date_accounting_notified_label"),
      colFilter: {
        field: "accounting_contacted_date",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
    {
      header: t("removalPanel.date_created_label"),
      colFilter: {
        field: "date_created",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
  ];

  let removalTableData = removalsData.map((item) => {
    item.current_location = item.current_location
      ? item.current_location
      : t("general.not_applicable");
    item.vendor_name = item.vendor_name ? item.vendor_name : t("general.not_applicable");

    return {
      id: item.id,
      dataPoint: item,
      cells: [
        item.custom_id,
        <VINLink vin={item.VIN} />,
        item.disposal_type,
        item.current_location,
        capitalize(item.status),
        item.vendor_name,
        ...(moment(item.vendor_contacted_date).isValid()
          ? [moment(item.vendor_contacted_date).format("YYYY-MM-DD")]
          : [t("general.not_applicable")]),
        ...(moment(item.accounting_contacted_date).isValid()
          ? [moment(item.accounting_contacted_date).format("YYYY-MM-DD")]
          : [t("general.not_applicable")]),
        ...(moment(item.date_created).isValid()
          ? [moment(item.date_created).format("YYYY-MM-DD")]
          : [t("general.not_applicable")]),
      ],
    };
  });

  return (
    <React.Fragment>
      {isMobile ? (
        <React.Fragment>
          {selectedAsset && mobileDetails ? (
            <AssetRemovalDetails
              asset={selectedAsset}
              setDataReady={setDataReady}
              setSelectedAsset={setSelectedAsset}
              setMobileDetails={setMobileDetails}
              setRemovalData={setRemovalData}
            />
          ) : (
            <div className="p-mb-5">
              <Table
                dataReady={dataReady}
                tableHeaders={removalTableHeaders}
                tableData={removalTableData}
                onSelectionChange={(selectedAsset) => setSelectedAsset(selectedAsset)}
                hasSelection
                tab={tab}
              />
            </div>
          )}
        </React.Fragment>
      ) : (
        <React.Fragment>
          <Table
            dataReady={dataReady}
            tableHeaders={removalTableHeaders}
            tableData={removalTableData}
            onSelectionChange={(selectedAsset) => setSelectedAsset(selectedAsset)}
            hasSelection
            tab={tab}
          />
          {selectedAsset && (
            <AssetRemovalDetails
              asset={selectedAsset}
              setDataReady={setDataReady}
              setSelectedAsset={setSelectedAsset}
              setMobileDetails={setMobileDetails}
              setRemovalData={setRemovalData}
            />
          )}
        </React.Fragment>
      )}
    </React.Fragment>
  );
};

export default CommonRemovalPanel;
