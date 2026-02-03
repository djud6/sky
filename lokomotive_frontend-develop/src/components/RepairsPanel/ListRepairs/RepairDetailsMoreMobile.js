import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { TabView, TabPanel } from "primereact/tabview";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import RepairIssueDetails from "./RepairIssueDetails";
import PartsCostTable from "../PartsCostTable";
import LaborCostTable from "../LaborCostTable";
import WarrantyTable from "../../AssetDetailPanel/WarrantyTable";
import RequestProgress from "../../ShareComponents/RequestProgress";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import PartsLaborCostMobile from "../PartsLabourCostMobile";
import "../../../styles/helpers/button4.scss";
import "../../../styles/ShareComponents/DetailsMoreMobile.scss";

const RepairDetailsMoreMobile = ({ repair, detailsSection, setMoreDetails, setDataReady }) => {
  const { t } = useTranslation();
  const [vehicle, setVehicle] = useState(null);
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
    t("requestProgress.in_transit_to_vendor_content_" + Boolean(repair.vendor_transport_to_vendor)),
    t("requestProgress.at_vendor_content"),
    t("requestProgress.complete_content"),
    t("requestProgress.in_transit_to_client_content_" + Boolean(repair.vendor_transport_to_client)),
    t("requestProgress.delivered_content"),
  ];

  useEffect(() => {
    setVehicle(null);
    setCostDataReady(false);
    setPartsInfo([]);
    setLaborInfo([]);

    const cancelTokenSource = axios.CancelToken.source();
    if (repair.issues.length === 0) {
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Get/Details/ID/${repair.repair_id}`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          setVehicle(response.data);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
    } else if (repair.issues.length !== 0) {
      let issuesArray = [];
      repair.issues.forEach((issue, i) => {
        issuesArray.push(issue.issue_id);
      });

      let partsAPIcall = axios.post(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Parts/Get/Costs/Issues`,
        { issue_ids: issuesArray },
        { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
      );

      let laborAPIcall = axios.post(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Labor/Get/Costs/Issues`,
        { issue_ids: issuesArray },
        { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
      );
      let vehicleAPIcall = axios.get(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Get/Details/ID/${repair.repair_id}`,
        {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        }
      );

      axios
        .all([partsAPIcall, laborAPIcall, vehicleAPIcall])
        .then(
          axios.spread((...responses) => {
            setPartsInfo(responses[0].data);
            setLaborInfo(responses[1].data);
            setVehicle(responses[2].data);
            setCostDataReady(true);
          })
        )
        .catch((error) => {
          ConsoleHelper(error);
          setCostDataReady(true);
        });
    }
    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [repair]);

  useEffect(() => {
    if (!costDataReady) {
      setVehicle(null);
      setPartsInfo([]);
      setLaborInfo([]);

      const cancelTokenSource = axios.CancelToken.source();
      if (repair.issues.length === 0) {
        axios
          .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Get/Details/ID/${repair.repair_id}`, {
            ...getAuthHeader(),
            cancelToken: cancelTokenSource.token,
          })
          .then((response) => {
            setVehicle(response.data);
          })
          .catch((error) => {
            ConsoleHelper(error);
          });
      } else if (repair.issues.length !== 0) {
        let issuesArray = [];
        repair.issues.forEach((issue, i) => {
          issuesArray.push(issue.issue_id);
        });

        let partsAPIcall = axios.post(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Parts/Get/Costs/Issues`,
          { issue_ids: issuesArray },
          { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
        );

        let laborAPIcall = axios.post(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Labor/Get/Costs/Issues`,
          { issue_ids: issuesArray },
          { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
        );
        let vehicleAPIcall = axios.get(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Get/Details/ID/${repair.repair_id}`,
          {
            ...getAuthHeader(),
            cancelToken: cancelTokenSource.token,
          }
        );

        axios
          .all([partsAPIcall, laborAPIcall, vehicleAPIcall])
          .then(
            axios.spread((...responses) => {
              setPartsInfo(responses[0].data);
              setLaborInfo(responses[1].data);
              setVehicle(responses[2].data);
              setCostDataReady(true);
            })
          )
          .catch((error) => {
            ConsoleHelper(error);
            setCostDataReady(true);
          });
      }
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
          label={t("repairsPanelIndex.repairs")}
          icon="pi pi-angle-right"
          iconPos="right"
          onClick={onReload}
        />
        <Button
          className="p-button-link link-under"
          label={repair.work_order}
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
      <div className="sub-sections">
        {detailsSection === t("requestProgress.tab_title") && (
          <div className="p-mx-3 p-my-5">
            <RequestProgress
              steps={progressSteps}
              contents={progressStepContent}
              activeStep={repair.status}
              layout="vertical"
            />
          </div>
        )}
        {detailsSection === t("general.issue") && (
          <RepairIssueDetails repair_id={repair.repair_id} />
        )}
        {detailsSection === t("general.warranty") && (
          <div className="p-mb-5">
            <WarrantyTable vin={repair.VIN} />
          </div>
        )}
        {detailsSection === t("general.parts_and_cost") &&
          (vehicle ? (
            vehicle.issues.length !== 0 ? (
              <React.Fragment>
                <PartsLaborCostMobile partsInfo={partsInfo} laborInfo={laborInfo} />
                <TabView className="darkSubTab parts-cost-mobile">
                  <TabPanel header={t("partsCost.parts_title").toUpperCase()}>
                    <PartsCostTable
                      request={repair}
                      partsInfo={partsInfo}
                      issues={repair.issues}
                      costDataReady={costDataReady}
                      setCostDataReady={setCostDataReady}
                    />
                  </TabPanel>
                  <TabPanel header={t("laborCost.labor_title").toUpperCase()}>
                    <LaborCostTable
                      request={repair}
                      laborInfo={laborInfo}
                      issues={repair.issues}
                      costDataReady={costDataReady}
                      setCostDataReady={setCostDataReady}
                    />
                  </TabPanel>
                </TabView>
              </React.Fragment>
            ) : null
          ) : (
            <div className="p-mt-3">
              <FullWidthSkeleton height="450px" />
            </div>
          ))}
      </div>
    </div>
  );
};

export default RepairDetailsMoreMobile;
