import React, { useState, useEffect } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { TabView, TabPanel } from "primereact/tabview";
import RepairIssueDetails from "./RepairIssueDetails";
import PartsLaborCostDetails from "../PartsLaborCostDetails";
import WarrantyTable from "../../AssetDetailPanel/WarrantyTable";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import RequestProgress from "../../ShareComponents/RequestProgress";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/ShareComponents/TabStyles/cornerTab.scss";
import "../../../styles/ShareComponents/DetailsMore.scss";

const RepairDetailsMore = ({ repair, setMoreDetails, setDataReady }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [activeIndex, setActiveIndex] = useState(0);
  const [vehicle, setVehicle] = useState(null);
  const [costDataReady, setCostDataReady] = useState(false);
  const [partsInfo, setPartsInfo] = useState([]);
  const [laborInfo, setLaborInfo] = useState([]);
  const progressSteps = [
    t("requestProgress.waiting_for_vendor"),
    t("requestProgress.awaiting_approval"),
    t("requestProgress.approved"),
    t("requestProgress.scheduled"),
    t("requestProgress.waiting_on_parts"),
    t("requestProgress.under_repair"),
    t("requestProgress.waiting_for_pickup"),
    t("requestProgress.in_transit"),
    t("requestProgress.complete"),
    t("requestProgress.in_transit_to_client"),
    t("requestProgress.delivered"),
  ];
  const progressStepContent = [
    t("requestProgress.waiting_for_vendor_content"),
    t("requestProgress.awaiting_approval_content"),
    t("requestProgress.approved_content"),
    t("requestProgress.scheduled_content"),
    t("requestProgress.waiting_on_parts_content"),
    t("requestProgress.under_repair_content"),
    t("requestProgress.waiting_for_pickup_content"),
    t("requestProgress.in_transit_content"),
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

  const handleBack = () => {
    setMoreDetails(false);
  };

  return (
    <div className="detailsMore p-py-5 p-mt-5 p-d-flex p-ai-start">
      <Button
        label={t("general.back")}
        className="p-button-link p-button-back"
        icon="pi pi-chevron-left"
        onClick={handleBack}
      />
      <div className="p-mr-4 flex-grow-1 p-mx-3 w-75">
        <h4 className="text-white font-weight-bold p-mt-1 p-mb-3">
          {t("repairDetails.repair_more_details", { vin: repair.VIN })}
        </h4>
        <TabView
          activeIndex={activeIndex}
          className="custom-tab-corner w-100"
          onTabChange={(e) => {
            setActiveIndex(e.index);
            dispatch({ type: CTRL_AUDIO_PLAY, payload: "sub_tab" });
          }}
        >
          <TabPanel header={t("requestProgress.tab_title").toUpperCase()}>
            <div className="section-view p-p-5 rounded">
              <RequestProgress
                steps={progressSteps}
                contents={progressStepContent}
                activeStep={repair.status}
              />
            </div>
          </TabPanel>
          <TabPanel header={t("general.issue").toUpperCase()}>
            <div className="section-view rounded">
              <RepairIssueDetails repair_id={repair.repair_id} />
            </div>
          </TabPanel>
          <TabPanel header={t("general.warranty").toUpperCase()}>
            <div className="section-view rounded">
              {vehicle ? (
                <div className="p-p-3">
                  <WarrantyTable vin={vehicle.VIN} />
                </div>
              ) : (
                <FullWidthSkeleton height="300px" />
              )}
            </div>
          </TabPanel>
          <TabPanel header={t("general.parts_and_cost").toUpperCase()}>
            <div className="section-view rounded">
              {vehicle ? (
                vehicle.issues.length !== 0 ? (
                  <PartsLaborCostDetails
                    request={repair}
                    partsInfo={partsInfo}
                    laborInfo={laborInfo}
                    issues={repair.issues}
                    setDataReady={setDataReady}
                    costDataReady={costDataReady}
                    setCostDataReady={setCostDataReady}
                  />
                ) : null
              ) : (
                <FullWidthSkeleton height="300px" />
              )}
            </div>
          </TabPanel>
        </TabView>
      </div>
    </div>
  );
};

export default RepairDetailsMore;
