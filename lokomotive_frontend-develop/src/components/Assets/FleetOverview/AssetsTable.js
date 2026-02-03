import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { getRolePermissions } from "../../../helpers/Authorization";
import { Button } from "primereact/button";
import Table from "../../ShareComponents/Table/Table";
import VINLink from "../../ShareComponents/helpers/VINLink";
import AssetDetailsQuickView from "./AssetDetailsQuickView";
import AssetDetailsMobile from "./AssetDetailsMobile";
import { Dialog } from "primereact/dialog";
import { ToggleButton } from "primereact/togglebutton";
import { capitalize } from "../../../helpers/helperFunctions";
import "../../../styles/OperatorsPanel/DailyOperatorsCheck.scss";
import "../../../styles/ShareComponents/Table/table.scss";

const AssetsTable = ({
  assets,
  selectedAsset,
  setSelectedAsset,
  dataReady,
  forceUpdate,
  setForceUpdate,
}) => {
  const { t } = useTranslation();
  const [isOperator, setIsOperator] = useState(false);
  const [isSupervisor, setIsSupervisor] = useState(false);
  const [mobileDetails, setMobileDetails] = useState(false);
  const [dialog, setDialog] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const [checkedFilters, setCheckedFilters] = useState([]);
  const [eventTypeFilter, setEventTypeFilter] = useState([]);
  const [theAllFilter, setTheAllFilter] = useState(true);
  const [eventTypes, setEventTypes] = useState([]);
  const [columnlist, setColumnlist] = useState({});
  const [tableHeaders, settableHeaders] = useState([]);
  const [tableData, settableData] = useState([]);

  const exportPdfColumn = [
    {
      title: "Class Code",
      dataIndex: "class_code",
    },
    {
      title: "Manufacture",
      dataIndex: "manufacturer",
    },
    {
      title: "Model",
      dataIndex: "model_number",
    },
    {
      title: "Model Year",
      dataIndex: "date_of_manufacture",
    },
    {
      title: "Business Unit",
      dataIndex: "businessUnit",
    },
    {
      title: "Unit Number",
      dataIndex: "unit_number",
    },
  ];

  const default_col_num = 5;

  const columns = [
    "unit number",
    "vin",
    "asset type",
    "fuel type",
    "current location",
    "status",
    "license plate",
    "last process",
    "mileage",
    "hours",
    "cost of ownership",
  ];

  const columns_showlist = {
    "unit number": false,
    vin: false,
    "asset type": false,
    "fuel type": false,
    "current location": false,
    status: false,
    "license plate": false,
    "last process": false,
    mileage: false,
    hours: false,
    "cost of ownership": false,
  };
  {
    /*
     let tableHeadersAll = [
    { header: t("general.vin"), colFilter: { field: "VIN" } },
    {
      header: t("general.asset_type"),
      colFilter: { field: "asset_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.location"),
      colFilter: {
        field: "current_location",
        filterOptions: { filterAs: "dropdown" },
      },
    },
    {
      header: t("general.business_unit"),
      colFilter: { field: "businessUnit", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.status"),
      colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.mileage"), colFilter: { field: "mileage" }
    },
    {
      header: t("general.hours"), colFilter: { field: "hours" }
    },
    {
      header: t("general.unit_number"), colFilter: { field: "unit_number" }
    },
    {
      header: t("general.model_number"), colFilter: { field: "model_number"}
    },
    {
      header: t("general.manufacturer"),
      colFilter: { field: "manufacturer", filterOptions: { filterAs: "dropdown" }}
    },
    {
      header: t("general.company"),
      colFilter: { field: "company", filterOptions: { filterAs: "dropdown" }}
    },
    {
      header: t("general.year_of_manufacture"), colFilter: { field: "year_of_manufacture"}
    },
    {
      header: t("general.fuel_type"),
      colFilter: { field: "fuel_type", filterOptions: { filterAs: "dropdown" }}
    },
    {
      header: t("general.license_plate"), colFilter: { field: "license_plate"}
    },
    {
      header: t("general.parent_asset"),
      colFilter: { field: "parent_asset", filterOptions: { filterAs: "dropdown" }}
    },
    {
      header: t("general.child_assets"),
      colFilter: { field: "child_assets", filterOptions: { filterAs: "dropdown" }}
    },
    {
      header: t("general.daily_average_hours"), colFilter: { field: "daily_average_hours"}
    },
    {
      header: t("general.cost_of_ownership"), colFilter: { field: "cost_of_ownership"}
    },
  ];
   */
  }
  let tableHeadersAll = [
    {
      header: t("general.class_code"),
      colFilter: { field: "class_code", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.manufacturer"),
      colFilter: { field: "manufacturer", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.model_number"),
      colFilter: { field: "model_number" },
    },
    {
      header: t("general.year_of_manufacture"),
      colFilter: { field: "date_of_manufacture", filterOptions: { filterAs: "dateRange" } },
    },
    {
      header: t("general.business_unit"),
      colFilter: { field: "businessUnit", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.unit_number"),
      colFilter: { field: "unit_number" },
    },
    { header: t("general.vin"), colFilter: { field: "VIN" } },
    {
      header: t("general.asset_type"),
      colFilter: { field: "asset_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.fuel_type"),
      colFilter: { field: "fuel_type", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.current_location"),
      colFilter: { field: "current_location", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.status"),
      colFilter: { field: "status", filterOptions: { filterAs: "dropdown" } },
    },
    {
      header: t("general.license_plate"),
      colFilter: { field: "license_plate" },
    },
    {
      header: t("general.last_process"),
      colFilter: { field: "last_process" },
    },
    {
      header: t("general.mileage"),
      colFilter: {
        field: "mileage",
        filterOptions: {
          filterAs: "mileageRange",
        },},
    },
    {
      header: t("general.hours"),
      colFilter: {
        field: "hours",
        filterOptions: {
          filterAs: "hourRange",
        },
      },
    },
    {
      header: t("general.cost_of_ownership"),
      colFilter: {
        field: "total_cost",
        filterOptions: {
          filterAs: "priceRange",
        },
      },
    },
  ];

  let tableDataAll = null;
  if (!!assets) {
    tableDataAll = assets.map((asset) => {
      /*
     return {
       id: asset.VIN,
       dataPoint: asset,
       cells: [
         <VINLink vin={asset.VIN} />,
         asset.asset_type,
         asset.current_location,
         asset.businessUnit,
         asset.status || t("general.not_applicable"),
         asset.hours_or_mileage.toLowerCase() === "mileage" ||
         asset.hours_or_mileage.toLowerCase() === "both"
           ? asset.mileage
           : t("general.not_applicable"),
         asset.hours_or_mileage.toLowerCase() === "hours" ||
         asset.hours_or_mileage.toLowerCase() === "both"
           ? asset.hours
           : t("general.not_applicable"),
         asset.unit_number || t("general.not_applicable"),
         asset.model_number || t("general.not_applicable"),
         asset.manufacturer || t("general.not_applicable"),
         asset.company || t("general.not_applicable"),
         asset.date_of_manufacture || t("general.not_applicable"),
         asset.fuel_type || t("general.not_applicable"),
         asset.license_plate || t("general.not_applicable"),
         asset.parent || t("general.not_applicable"),
         asset.path || t("general.not_applicable"),
         asset.daily_average_hours || t("general.not_applicable"),
         asset.total_cost || t("general.not_applicable"),
       ],
     };
     */
      return {
        id: asset.VIN,
        dataPoint: asset,
        cells: [
          asset.class_code || t("general.not_applicable"),
          asset.manufacturer || t("general.not_applicable"),
          asset.model_number || t("general.not_applicable"),
          asset.date_of_manufacture || t("general.not_applicable"),
          asset.businessUnit || t("general.not_applicable"),
          asset.unit_number || t("general.not_applicable"),
          <VINLink vin={asset.VIN} />,
          asset.asset_type || t("general.not_applicable"),
          asset.fuel_type || t("general.not_applicable"),
          asset.current_location || t("general.not_applicable"),
          asset.status || t("general.not_applicable"),
          asset.license_plate || t("general.not_applicable"),
          asset.last_process || t("general.not_applicable"),
          asset.hours_or_mileage.toLowerCase() === "mileage" ||
          asset.hours_or_mileage.toLowerCase() === "both"
            ? asset.mileage.toLocaleString()
            : t("general.not_applicable"),
          asset.hours_or_mileage.toLowerCase() === "hours" ||
          asset.hours_or_mileage.toLowerCase() === "both" ||
          asset.hours !== -1
            ? asset.hours.toLocaleString()
            : t("general.not_applicable"),

          "$ " +
            asset.total_cost.toLocaleString("en-US", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }) || t("general.not_applicable"), //
        ],
      };
    });
  }

  useEffect(() => {
    setColumnlist(columns_showlist);
    const copyHeaders = [];
    for (let i = 0; i < tableHeadersAll.length; i++) {
      if (i < default_col_num) {
        copyHeaders.push(tableHeadersAll[i]);
        continue;
      }
      const header = tableHeadersAll[i].header;
      if (columnlist[header] == true) {
        copyHeaders.push(tableHeaders[i]);
      }
    }

    settableHeaders(copyHeaders);
    settableData(tableDataAll);
  }, [dataReady]);

  useEffect(() => {
    const rolePermissions = getRolePermissions();
    if (rolePermissions.role.toLowerCase() === "operator") setIsOperator(true);
    else setIsOperator(false);

    if (rolePermissions.role.toLowerCase() === "supervisor") setIsSupervisor(true);
    else setIsSupervisor(false);
  }, []);

  useEffect(() => {
    if (selectedAsset) {
      setMobileDetails(true);
    }
  }, [selectedAsset]);

  useEffect(() => {
    if (dialog) {
      setEventTypes(columns);
    } else {
      const copyHeaders = [];
      for (let i = 0; i < tableHeadersAll.length; i++) {
        if (i < default_col_num) {
          copyHeaders.push(tableHeadersAll[i]);
          continue;
        }
        const header = tableHeadersAll[i].header.toLowerCase();
        if (columnlist[header] == true) {
          copyHeaders.push(tableHeadersAll[i]);
        }
      }

      settableHeaders(copyHeaders);

      const copyTableData = new Array();

      for (let i = 0; i < tableDataAll.length; i++) {
        copyTableData[i] = {
          id: tableDataAll[i].id,
          dataPoint: tableDataAll[i].dataPoint,
          cells: [],
        };
        for (let j = 0; j < tableDataAll[i].cells.length; j++) {
          if (j < default_col_num) {
            copyTableData[i].cells.push(tableDataAll[i].cells[j]);
            continue;
          }
          if (columnlist[columns[j - default_col_num]] == true) {
            copyTableData[i].cells.push(tableDataAll[i].cells[j]);
          }
        }
      }

      settableData(copyTableData);
    }
  }, [dialog]);

  const handleTheAllFilter = () => {
    const clearAllFilters = new Array(checkedFilters.length).fill(false);
    setCheckedFilters(clearAllFilters);
    setTheAllFilter(true);
    setEventTypeFilter([]);
  };

  const filtersHandler = (eventType, i) => {
    let copyOfCheckedFilters = [...checkedFilters];
    copyOfCheckedFilters[i] = !checkedFilters[i];
    setCheckedFilters(copyOfCheckedFilters);
    setTheAllFilter(false);
    let copyOfEventTypeFilter = [...eventTypeFilter];
    if (eventTypeFilter.includes(eventType)) {
      copyOfEventTypeFilter = copyOfEventTypeFilter.filter((type) => type !== eventType);
      setEventTypeFilter(copyOfEventTypeFilter);
      if (copyOfEventTypeFilter.length === 0) setTheAllFilter(!theAllFilter);
    } else {
      copyOfEventTypeFilter.push(eventType);
      setEventTypeFilter(copyOfEventTypeFilter);
    }
  };

  const filterButtons = eventTypes.map((eventType, i) => {
    return (
      <ToggleButton
        key={eventType + i}
        checked={checkedFilters[i]}
        onChange={() => filtersHandler(eventType, i)}
        onLabel={capitalize(eventType)}
        offLabel={capitalize(eventType)}
        onIcon=""
        offIcon=""
        className="p-mr-2 p-mb-2 p-button-rounded"
      />
    );
  });

  const add_extracolumns = () => {
    const columnlistCopy = columnlist;
    for (let i = 0; i < checkedFilters.length; i++) {
      const specific_column = columns[i];
      if (checkedFilters[i] == true) {
        columnlistCopy[specific_column] = true;
      } else {
        columnlistCopy[specific_column] = false;
      }
    }
    setColumnlist(columnlistCopy);
    setDialog(false);
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label="Cancel"
          icon="pi pi-times"
          className="p-button-text"
          onClick={() => setDialog(false)}
        />
        <Button label="Confirm" icon="pi pi-check" onClick={add_extracolumns} />
      </div>
    );
  };

  return (
    <div>
      <div className={`${isMobile ? "" : "p-mt-5"}`}>
        {isMobile ? (
          <React.Fragment>
            {selectedAsset && mobileDetails ? (
              <AssetDetailsMobile
                isSupervisor={isSupervisor}
                isOperator={isOperator}
                asset={selectedAsset}
                setSelectedAsset={setSelectedAsset}
                setMobileDetails={setMobileDetails}
                forceUpdate={forceUpdate}
                setForceUpdate={setForceUpdate}
              />
            ) : (
              <div className="darkTable p-mb-5">
                {/*
                  <div className={`configure-container ml-auto p-mr-2 p-mb-5`}>
                     <Button
                       className="p-button-darkcolor"
                       label={"custom columns"}
                       icon="pi pi-sliders-v"
                       onClick={() => {setDialog(true)}}
                     />
                  </div>
              */}
                <Table
                  tableHeaders={tableHeaders}
                  tableData={tableData}
                  dataReady={dataReady}
                  hasSelection
                  onSelectionChange={(asset) => setSelectedAsset(asset)}
                  timeOrder={false}
                />
              </div>
            )}
          </React.Fragment>
        ) : (
          <React.Fragment>
            <div className="darkTable">
              <div className={`btn-2`}>
                <Button
                  label={"Custom Columns"}
                  icon="pi pi-sliders-v"
                  onClick={() => {
                    setDialog(true);
                  }}
                  style={{ width: "180px" }}
                />
              </div>
              <div className={"fleet_overview"}>
                <Table
                  tableHeaders={tableHeaders}
                  tableData={tableData}
                  dataReady={dataReady}
                  hasSelection
                  onSelectionChange={(asset) => setSelectedAsset(asset)}
                  timeOrder={false}
                  hasPdfExport
                  exportPdfColumns={exportPdfColumn}
                />
              </div>
            </div>
            {selectedAsset && (
              <AssetDetailsQuickView asset={selectedAsset} setSelectedAsset={setSelectedAsset} />
            )}
          </React.Fragment>
        )}
      </div>
      <Dialog
        className="custom-main-dialog configure-checks-dialog"
        header={"Custom Columns"}
        visible={dialog}
        onHide={() => setDialog(false)}
        style={{ width: "60vw" }}
        breakpoints={{ "1440px": "default_col_num5vw", "980px": "85vw", "600px": "90vw" }}
        footer={renderFooter()}
      >
        <div className="p-field">
          <p>Please select the extra columns you want to see.</p>
          <ToggleButton
            checked={theAllFilter}
            onChange={handleTheAllFilter}
            onLabel="None"
            offLabel="None"
            onIcon=""
            offIcon=""
            className="p-mr-2 p-mb-2 p-button-rounded"
          />
          {filterButtons}
        </div>
      </Dialog>
    </div>
  );
};

export default AssetsTable;
