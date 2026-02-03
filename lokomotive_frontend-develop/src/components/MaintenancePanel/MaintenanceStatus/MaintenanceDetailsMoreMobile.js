import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { TabView, TabPanel } from "primereact/tabview";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import RequestProgress from "../../ShareComponents/RequestProgress";
import PartsCostTable from "../../RepairsPanel/PartsCostTable";
import LaborCostTable from "../../RepairsPanel/LaborCostTable";
import PartsLaborCostMobile from "../../RepairsPanel/PartsLabourCostMobile";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button4.scss";
import "../../../styles/ShareComponents/DetailsMoreMobile.scss";
import "../../../styles/ShareComponents/TabStyles/subTab.scss";

const MaintenanceDetailsMoreMobile = ({ maintenance, detailsSection, setMoreDetails }) => {
  const { t } = useTranslation();
  const [costDataReady, setCostDataReady] = useState(false);
  const [partsInfo, setPartsInfo] = useState([]);
  const [laborInfo, setLaborInfo] = useState([]);
  const progressSteps = [
    t("requestProgress.waiting_for_vendor"),
    t("requestProgress.awaiting_approval"),
    t("requestProgress.approved"),
    t("requestProgress.in_transit_to_vendor"),
    t("requestProgress.at_vendor"),
    t("requestProgress.complete"),
    t("requestProgress.in_transit_to_client"),
    t("requestProgress.delivered"),
  ];
  const progressStepContent = [
    t("requestProgress.waiting_for_vendor_content"),
    t("requestProgress.awaiting_approval_content"),
    t("requestProgress.approved_content"),
    t(
      "requestProgress.in_transit_to_vendor_content_" +
        Boolean(maintenance.vendor_transport_to_vendor)
    ),
    t("requestProgress.at_vendor_content"),
    t("requestProgress.complete_content"),
    t(
      "requestProgress.in_transit_to_client_content_" +
        Boolean(maintenance.vendor_transport_to_client)
    ),
    t("requestProgress.delivered_content"),
  ];

  useEffect(() => {
    setCostDataReady(false);
    const cancelTokenSource = axios.CancelToken.source();
    let partsAPIcall = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Parts/Get/Costs/Maintenance/${maintenance.maintenance_id}`,
      { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
    );
    let laborAPIcall = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Labor/Get/Costs/Maintenance/${maintenance.maintenance_id}`,
      { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
    );

    axios
      .all([partsAPIcall, laborAPIcall])
      .then(
        axios.spread((...responses) => {
          setPartsInfo(responses[0].data);
          setLaborInfo(responses[1].data);
          setCostDataReady(true);
        })
      )
      .catch((error) => {
        ConsoleHelper(error);
        setCostDataReady(true);
      });

    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [maintenance]);

  useEffect(() => {
    if (!costDataReady) {
      const cancelTokenSource = axios.CancelToken.source();
      let partsAPIcall = axios.get(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Parts/Get/Costs/Maintenance/${maintenance.maintenance_id}`,
        { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
      );
      let laborAPIcall = axios.get(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Labor/Get/Costs/Maintenance/${maintenance.maintenance_id}`,
        { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
      );

      axios
        .all([partsAPIcall, laborAPIcall])
        .then(
          axios.spread((...responses) => {
            setPartsInfo(responses[0].data);
            setLaborInfo(responses[1].data);
            setCostDataReady(true);
          })
        )
        .catch((error) => {
          ConsoleHelper(error);
          setCostDataReady(true);
        });

      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [costDataReady]);

  const onReload = () => {
    window.location.reload();
  };

  return (
    <div className="details-more-mobile">
      <div className="link-order p-d-flex">
        <Button
          className="p-button-link link-under"
          label={t("maintenancePanelIndex.page_title")}
          icon="pi pi-angle-right"
          iconPos="right"
          onClick={onReload}
        />
        <Button
          className="p-button-link link-under"
          label={maintenance.work_order}
          icon="pi pi-angle-right"
          iconPos="right"
          onClick={() => setMoreDetails(false)}
        />
        <Button className="p-button-link" label={detailsSection} />
      </div>
      {detailsSection !== t("general.parts_and_cost") && (
        <div className="no-style-btn p-my-3 p-mx-3">
          <Button
            label={t("general.back")}
            className="p-button-link"
            icon="pi pi-chevron-left"
            onClick={() => setMoreDetails(false)}
          />
        </div>
      )}
      {detailsSection === t("requestProgress.tab_title") && (
        <div className="p-mx-3 p-mt-5">
          <RequestProgress
            steps={progressSteps}
            contents={progressStepContent}
            activeStep={maintenance.status}
            layout="vertical"
          />
        </div>
      )}
      {detailsSection === t("general.parts_and_cost") && (
        <React.Fragment>
          <PartsLaborCostMobile partsInfo={partsInfo} laborInfo={laborInfo} />
          <TabView className="darkSubTab parts-cost-mobile">
            <TabPanel header={t("partsCost.parts_title").toUpperCase()}>
              <PartsCostTable
                request={maintenance}
                partsInfo={partsInfo}
                maintenanceID={maintenance.maintenance_id}
                costDataReady={costDataReady}
                setCostDataReady={setCostDataReady}
              />
            </TabPanel>
            <TabPanel header={t("laborCost.labor_title").toUpperCase()}>
              <LaborCostTable
                request={maintenance}
                laborInfo={laborInfo}
                maintenanceID={maintenance.maintenance_id}
                costDataReady={costDataReady}
                setCostDataReady={setCostDataReady}
              />
            </TabPanel>
          </TabView>
        </React.Fragment>
      )}
    </div>
  );
};

export default MaintenanceDetailsMoreMobile;
