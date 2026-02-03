import React, { useEffect, useState } from "react";
import axios from "axios";
import _ from "lodash";
import { getAuthHeader } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import { useTranslation } from "react-i18next";
import { TabView, TabPanel } from "primereact/tabview";
import DocumentUpload from "./DocumentUpload";
import DocumentHistory from "./DocumentHistory";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";
import "../../../styles/AssetDetailsPanel/DocumentUpload.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";

const DocumentTab = ({ vin }) => {
  const { t } = useTranslation();
  const [dataReady, setDataReady] = useState(false);
  const [registrationPreviousFiles, setRegistrationPreviousFiles] = useState([]);
  const [insurancePreviousFiles, setInsurancePreviousFiles] = useState([]);
  const [otherPreviousFiles, setOtherPreviousFiles] = useState([]);

  // HANDLES INSURANCE & REGISTRATION FILES
  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Get/Files/${vin}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((res) => {
        filterInsAndRegArrays(res.data, "registration");
        filterInsAndRegArrays(res.data, "insurance");
        filterInsAndRegArrays(res.data, "other");
        setDataReady(true);
      })
      .catch((err) => {
        ConsoleHelper(err);
      });
    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vin, dataReady]);

  const filterInsAndRegArrays = (arr, type) => {
    let documentArr = [];
    documentArr = arr.filter((doc) => {
      return doc.file_purpose === type;
    });
    const sortedDocs = _.orderBy(documentArr, (doc) => doc.expiration_date, ["desc"]);
    const sorted = sortedDocs.filter((doc) => doc.expiration_date !== null);

    if (type === "registration") {
      setRegistrationPreviousFiles(sorted);
    }
    if (type === "insurance") {
      setInsurancePreviousFiles(sorted);
    }
    if (type === "other"){
      setOtherPreviousFiles(documentArr);
    }
  };

  return (
    <div className="document-upload">
      <div className="tab-title">{t("documentTab.tab_title")}</div>
      <TabView className="darkSubTab">
        <TabPanel header={t("documentTab.upload_document")}>
          <div className="p-d-flex p-jc-center p-mt-5">
            <DocumentUpload vin={vin} setDataReady={setDataReady} />
          </div>
        </TabPanel>
        <TabPanel header={"History"}>
          <DocumentHistory
            vin={vin}
            registrationFiles={registrationPreviousFiles}
            insuranceFiles={insurancePreviousFiles}
            otherFiles={otherPreviousFiles}
            dataReady={dataReady}
          />
        </TabPanel>
      </TabView>
    </div>
  );
};

export default DocumentTab;
