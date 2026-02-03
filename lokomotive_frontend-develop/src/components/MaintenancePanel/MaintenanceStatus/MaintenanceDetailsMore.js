import React, { useState, useEffect } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { TabView, TabPanel } from "primereact/tabview";
import RequestProgress from "../../ShareComponents/RequestProgress";
import PartsLaborCostDetails from "../../RepairsPanel/PartsLaborCostDetails";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/ShareComponents/TabStyles/cornerTab.scss";
import "../../../styles/ShareComponents/DetailsMore.scss";

const MaintenanceDetailsMore = ({ maintenance, setMoreDetails }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [activeIndex, setActiveIndex] = useState(0);
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
          {t("maintenanceDetails.maintenance_more_details", { vin: maintenance.VIN })}
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
            <div className="section-view rounded p-p-5">
              <RequestProgress
                steps={progressSteps}
                activeStep={maintenance.status}
                contents={progressStepContent}
              />
            </div>
          </TabPanel>
          <TabPanel header={t("general.parts_and_cost").toUpperCase()}>
            <div className="section-view rounded">
              <PartsLaborCostDetails
                request={maintenance}
                partsInfo={partsInfo}
                laborInfo={laborInfo}
                maintenanceID={maintenance.maintenance_id}
                costDataReady={costDataReady}
                setCostDataReady={setCostDataReady}
              />
            </div>
          </TabPanel>
        </TabView>
      </div>
    </div>
  );
};

export default MaintenanceDetailsMore;
