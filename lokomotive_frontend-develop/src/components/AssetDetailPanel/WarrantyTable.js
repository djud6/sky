import React, { useState, useEffect } from "react";
import axios from "axios";
import _ from "lodash";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { getAuthHeader } from "../../helpers/Authorization";
import * as Constants from "../../constants";
import Table from "../ShareComponents/Table/Table";
import DateBadge from "../ShareComponents/helpers/DateBadge";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import "../../styles/ShareComponents/Table/table.scss";

const WarrantyTable = ({ vin }) => {
  const { t } = useTranslation();
  const [warrantyDataReady, setWarrantyDataReady] = useState(false);
  const [warrantyPreviousFiles, setWarrantyPreviousFiles] = useState([]);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  let reversedArr = [];
  reversedArr = [...warrantyPreviousFiles].reverse();

  let tableHeaders = [
    {
      header: t("documentTab.warranty_document"),
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

  let tableData = reversedArr.map((warrantyFile) => {
    let fileName;
    if (warrantyFile.file_name.toLowerCase() === "na") {
      fileName = warrantyFile.file_url.slice(96 + warrantyFile.VIN.length).split("?se=")[0];
    } else {
      fileName = warrantyFile.file_name;
    }

    return {
      id: warrantyFile.file_id,
      dataPoint: warrantyFile,
      cells: [
        <a href={warrantyFile.file_url} target="_blank" rel="noopener noreferrer">
          {fileName}
        </a>,
        <DateBadge currentDate={warrantyFile.expiration_date} dateRange={2} />,
      ],
    };
  });

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Get/Files/${vin}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((res) => {
        const warrantyArr = res.data.filter((doc) => {
          return doc.file_purpose === "warranty";
        });
        const sortedDocs = _.orderBy(warrantyArr, (doc) => doc.expiration_date);
        const sorted = sortedDocs.filter((doc) => doc.expiration_date !== null);

        setWarrantyPreviousFiles(sorted);
        setWarrantyDataReady(true);
      })
      .catch((err) => {
        ConsoleHelper(err);
      });
    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vin, warrantyDataReady]);

  return (
    <div className="darkTable">
      <Table
        dataReady={warrantyDataReady}
        tableHeaders={tableHeaders}
        tableData={tableData}
        rows={5}
        globalSearch={isMobile ? true : false}
        persistPage={false}
        timeOrder={false}
      />
    </div>
  );
};

export default React.memo(WarrantyTable);
