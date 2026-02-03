import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { SelectButton } from "primereact/selectbutton";
import Table from "../../ShareComponents/Table/Table";
import WarrantyTable from "../WarrantyTable";
import DateBadge from "../../ShareComponents/helpers/DateBadge";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";

const DocumentHistory = ({ vin, registrationFiles, insuranceFiles, otherFiles, dataReady }) => {
  const { t } = useTranslation();
  const [section, setSection] = useState(t("documentTab.registration"));
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const options = [
    t("documentTab.registration"),
    t("documentTab.insurance"),
    t("documentTab.warranty"),
    t("documentTab.other"),
  ];

  if (!registrationFiles || !insuranceFiles || !otherFiles) return null;

  let rTableHeaders = [
    {
      header: t("documentTab.registration_document"),
      colFilter: { field: "file_name" },
    },
    {
      header: t("documentTab.expiry_date"),
      colFilter: {
        field: "expiration_date",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    }
  ];

  let rTableData = registrationFiles.map((doc) => {
    let fileName;
    if (doc.file_name.toLowerCase() === "na") {
      fileName = doc.file_url.slice(104 + doc.VIN.length).split("?se=")[0];
    } else {
      fileName = doc.file_name;
    }

    return {
      id: doc.file_id,
      dataPoint: doc,
      cells: [
        <a href={doc.file_url} target="_blank" rel="noopener noreferrer">
          {fileName}
        </a>,
        <DateBadge currentDate={doc.expiration_date} dateRange={2} />,
      ],
    };
  });

  let iTableHeaders = [
    {
      header: t("documentTab.insurance_document"),
      colFilter: { field: "file_name" },
    },
    {
      header: t("documentTab.expiry_date"),
      colFilter: {
        field: "expiration_date",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
  ];

  let iTableData = insuranceFiles.map((doc) => {
    let fileName;
    if (doc.file_name.toLowerCase() === "na") {
      fileName = doc.file_url.slice(98 + doc.VIN.length).split("?se=")[0];
    } else {
      fileName = doc.file_name;
    }
    return {
      id: doc.file_id,
      dataPoint: doc,
      cells: [
        <a href={doc.file_url} target="_blank" rel="noopener noreferrer">
          {fileName}
        </a>,
        <DateBadge currentDate={doc.expiration_date} dateRange={2} />,
      ],
    };
  });

  let oTableHeaders = [
    {
      header: t("documentTab.other_document"),
      colFilter: { field: "file_name" },
    },
    {
      header: t("documentTab.expiry_date"),
      colFilter: {
        field: "expiration_date",
        filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
      },
    },
  ];

  let oTableData =otherFiles.map((doc) => {
    let fileName;
    if (doc.file_name.toLowerCase() === "na") {
      fileName = doc.file_url.slice(98 + doc.VIN.length).split("?se=")[0];
    } else {
      fileName = doc.file_name;
    }
    return {
      id: doc.file_id,
      dataPoint: doc,
      cells: [
        <a href={doc.file_url} target="_blank" rel="noopener noreferrer">
          {fileName}
        </a>,
        <DateBadge currentDate={doc.expiration_date} dateRange={2} />,
      ],
    };
  });

  return (
    <div className="document-history">
      <div className="custom-select-btn p-mx-3 p-mb-3  p-d-flex p-jc-end">
        <SelectButton value={section} options={options} onChange={(e) => setSection(e.value)} />
      </div>
      {section === t("documentTab.registration") && (
        <div className={`darkTable ${isMobile ? "p-mb-5" : ""}`}>
          <Table
            dataReady={dataReady}
            tableHeaders={rTableHeaders}
            tableData={rTableData}
            rows={5}
            globalSearch={isMobile ? true : false}
            persistPage={false}
            timeOrder={false}
            showSearchPref={false}
            showAssetCount={false}
          />
        </div>
      )}
      {section === t("documentTab.insurance") && (
        <div className={`darkTable ${isMobile ? "p-mb-5" : ""}`}>
          <Table
            dataReady={dataReady}
            tableHeaders={iTableHeaders}
            tableData={iTableData}
            rows={5}
            globalSearch={isMobile ? true : false}
            persistPage={false}
            timeOrder={false}
          />
        </div>
      )}
      {section === t("documentTab.warranty") && (
        <div className={`${isMobile ? "p-mb-5" : ""}`}>
          <WarrantyTable vin={vin} />
        </div>
      )}
     {section === t("documentTab.other") && (
        <div className={`darkTable ${isMobile ? "p-mb-5" : ""}`}>
          <Table
            dataReady={dataReady}
            tableHeaders={oTableHeaders}
            tableData={oTableData}
            rows={5}
            globalSearch={isMobile ? true : false}
            persistPage={false}
            timeOrder={false}
          />
        </div>
      )}
    </div>
  );
};

export default DocumentHistory;
