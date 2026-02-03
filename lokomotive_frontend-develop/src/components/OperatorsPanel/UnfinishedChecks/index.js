import React, { useEffect, useState } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { Button } from "primereact/button";
import { faClipboardList } from "@fortawesome/free-solid-svg-icons";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import { loadingAlert, successAlert, errorAlert } from "../../ShareComponents/CommonAlert";
import OpCheckForm from "../DailyOperatorsCheck/OpCheckForm";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/helpers/button4.scss";
import "../../../styles/OperatorsPanel/UnfinishedChecks.scss";
import Placeholder from "./Placefolder";
import UnfinishedChecksTable from "./UnfinishedChecksTable";
import LoadingText from "./LoadingText";

const UnfinishedChecksPanel = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [checkItems, setCheckItems] = useState(null);
  const [checkDataReady, setCheckDataReady] = useState(false);
  const [operable, setOperable] = useState("");
  const [walkAroundInspection, setWalkAroundInspection] = useState("");
  const [damage, setDamage] = useState("");
  const [mileage, setMileage] = useState(null);
  const [hours, setHours] = useState(null);
  const [fuelLevel, setFuelLevel] = useState(0);
  const [disableButton, setDisableButton] = useState(true);
  const [validationWarningMsg, setValidationWarningMsg] = useState(null);
  const [validationSearch, setValidationSearch] = useState(false);
  const [checklistStatus, setChecklistStatus] = useState(false);
  const [checkFormItems, setCheckFormItems] = useState({});
  const [checkFormComments, setCheckFormComments] = useState({});
  const [submitClicked, setSubmitClicked] = useState(false);
  const [dataReady, setDataReady] = useState(false);
  const subCheckTitles = ["lights", "fluids", "leaks", "safety_equipment"];
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    setCheckDataReady(false);
    setCheckItems(null);
    const cancelTokenSource = axios.CancelToken.source();
    if (selectedAsset) {
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Get/Checks/${selectedAsset.VIN}`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          let checks = response.data;
          delete checks["id"];
          delete checks["asset_type_name"];
          delete checks["date_created"];
          delete checks["date_updated"];
          delete checks["created_by"];
          delete checks["modified_by"];
          setCheckDataReady(true);
          setCheckItems(checks);
        })
        .catch((error) => {
          setCheckDataReady(false);
        });
    }
    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [selectedAsset]);

  useEffect(() => {
    setOperable("");
    setWalkAroundInspection("");
    setDamage("");
    setMileage("");
    setHours("");
    setValidationWarningMsg(null);
    setCheckFormItems({});
    setCheckFormComments({});
    setChecklistStatus(false);
  }, [selectedAsset]);

  const handleSubmit = (event) => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    event.preventDefault();
    let commentArray = Object.keys(checkFormComments).map((name, i) => {
      return { comment: checkFormComments[name], check: name };
    });
    let operatorCheck = {
      data: {
        ...checkFormItems,
        damage: damage,
        VIN: selectedAsset.VIN,
        operable: operable,
        fuel: fuelLevel,
        ...(selectedAsset.hours_or_mileage.toLowerCase() === "both" && {
          mileage: parseFloat(mileage),
          hours: parseFloat(hours),
        }),
        ...(selectedAsset.hours_or_mileage.toLowerCase() === "mileage" && {
          mileage: parseFloat(mileage),
        }),
        ...(selectedAsset.hours_or_mileage.toLowerCase() === "hours" && {
          hours: parseFloat(hours),
        }),
      },
      comments: commentArray,
    };

    errors ? setSubmitClicked(true) : sendOperatorCheck(operatorCheck);
  };

  const errors = (function () {
    for (let item in checkFormItems) {
      if (!checkFormComments[item] && !checkFormItems[item]) return true;
    }
    return false;
  })();

  const sendOperatorCheck = (operatorCheck) => {
    loadingAlert();
    axios
      .post(
        `${Constants.ENDPOINT_PREFIX}/api/v1/DailyOperationalChecks/Add`,
        operatorCheck,
        getAuthHeader()
      )
      .then((response) => {
        successAlert("msg", t("lookupDailyCheckPanelIndex.submit_check_success"));
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
        setSelectedAsset(null);
        setDataReady(null);
      })
      .catch((error) => {
        errorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  useEffect(() => {
    if (selectedAsset && (mileage || hours)) {
      if (selectedAsset.hours_or_mileage.toLowerCase() === "both" && !hours) {
        setValidationWarningMsg("Please provide hours for auto-validation.");
      } else if (selectedAsset.hours_or_mileage.toLowerCase() === "both" && !mileage) {
        setValidationWarningMsg("Please provide mileage for auto-validation.");
      } else {
        const delayDebounceFn = setTimeout(() => {
          const cancelTokenSource = axios.CancelToken.source();
          setValidationSearch(true);
          setValidationWarningMsg(null);
          axios
            .post(
              `${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Validate/Usage`,
              {
                VIN: selectedAsset.VIN,
                mileage: parseFloat(mileage),
                hours: parseFloat(hours),
              },
              { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
            )
            .then((response) => {
              setValidationSearch(false);
            })
            .catch((error) => {
              setValidationWarningMsg(error.customErrorMsg);
              setValidationSearch(false);
              ConsoleHelper(error);
            });
          return () => {
            //Doing clean up work, cancel the asynchronous api call
            cancelTokenSource.cancel("cancel the asynchronous api call");
          };
        }, 1000);
        return () => clearTimeout(delayDebounceFn);
      }
    }
  }, [mileage, hours]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (selectedAsset) {
      for (var key in checkItems) {
        if (
          checkItems[key] &&
          key !== "fuel" &&
          !(subCheckTitles.indexOf(key) > -1) &&
          checkFormItems[key] !== true &&
          checkFormItems[key] !== false
        ) {
          setDisableButton(true);
          setChecklistStatus(false);
          break;
        } else {
          setChecklistStatus(true);

          if (selectedAsset.hours_or_mileage.toLowerCase() === "both" && (!mileage || !hours)) {
            setDisableButton(true);
          } else if (selectedAsset.hours_or_mileage.toLowerCase() === "hours" && !hours) {
            setDisableButton(true);
          } else if (selectedAsset.hours_or_mileage.toLowerCase() === "mileage" && !mileage) {
            setDisableButton(true);
          } else {
            setDisableButton(false);
          }
        }
      }
    }
  }, [selectedAsset, mileage, hours, checkFormItems]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="unfinished-checks-panel">
      {isMobile && (
        <QuickAccessTabs
          tabs={["Daily Check", "Unfinished", "Lookup"]}
          activeTab={"Unfinished"}
          urls={["/operators", "/operators/unfinished-checks", "/operators/lookup"]}
        />
      )}
      <PanelHeader icon={faClipboardList} text={t("unfinishedChecksPanel.panel_header")} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Daily Check", "Unfinished Checks", "Lookup"]}
          activeTab={"Unfinished Checks"}
          urls={["/operators", "/operators/unfinished-checks", "/operators/lookup"]}
        />
      )}
      {!isMobile ? (
        <div className="p-grid p-mt-3">
          {/*<div className="p-col-12 p-md-12 p-lg-6 p-xl-4 p-p-0"  >*/}
            <div className="unfinished-table" >
              <UnfinishedChecksTable
                setSelectedAsset={setSelectedAsset}
                dataReady={dataReady}
                setDataReady={setDataReady}
              />
            </div>
          {/*</div>*/}

            {selectedAsset ? (
              <div className="unfinished-checks-form" >
                <form onSubmit={handleSubmit}>
                  {checkDataReady ? (
                    <OpCheckForm
                      selectedTitle={`${t("lookupDailyCheckPanelIndex.create_oper_check_for_vin", {
                        vehicleVIN: selectedAsset.VIN,
                      })}`}
                      vehicle={selectedAsset}
                      operable={operable}
                      setOperable={setOperable}
                      walkAroundInspection={walkAroundInspection}
                      setWalkAroundInspection={setWalkAroundInspection}
                      damage={damage}
                      setDamage={setDamage}
                      mileage={mileage}
                      setMileage={setMileage}
                      hours={hours}
                      setHours={setHours}
                      fuelLevel={fuelLevel}
                      setFuelLevel={setFuelLevel}
                      disableButton={disableButton}
                      validationSearch={validationSearch}
                      validationWarningMsg={validationWarningMsg}
                      checklistStatus={checklistStatus}
                      checkFormItems={checkFormItems}
                      setCheckFormItems={setCheckFormItems}
                      checkFormComments={checkFormComments}
                      setCheckFormComments={setCheckFormComments}
                      submitClicked={submitClicked}
                      setSubmitClicked={setSubmitClicked}
                      checkItems={checkItems}
                    />
                  ) : (
                    <div className="loading-screen p-d-flex p-jc-center">
                      <LoadingText
                        text={t("unfinishedChecksPanel.get_check_detail_placeholder_text")}
                        spinnerColor={"#8D249899"}
                      />
                    </div>
                  )}
                </form>
              </div>
            ) : (
              <div className="unfinished-checks-form">
                <Placeholder dataReady={dataReady} />
              </div>
            )}

        </div>
      ) : !selectedAsset ? (
        <div className="p-mb-5">
          <UnfinishedChecksTable
            setSelectedAsset={setSelectedAsset}
            dataReady={dataReady}
            setDataReady={setDataReady}
          />
        </div>
      ) : (
        <div className="p-mx-3">
          <div className="no-style-btn p-mt-3">
            <Button
              label={t("general.back")}
              className="p-button-link"
              icon="pi pi-chevron-left"
              onClick={() => {
                setDataReady(false);
                setSelectedAsset(null);
              }}
            />
          </div>
          <form onSubmit={handleSubmit}>
            {checkDataReady ? (
              <OpCheckForm
                selectedTitle={`${t("lookupDailyCheckPanelIndex.create_oper_check_for_vin", {
                  vehicleVIN: selectedAsset.VIN,
                })}`}
                vehicle={selectedAsset}
                operable={operable}
                setOperable={setOperable}
                walkAroundInspection={walkAroundInspection}
                setWalkAroundInspection={setWalkAroundInspection}
                damage={damage}
                setDamage={setDamage}
                mileage={mileage}
                setMileage={setMileage}
                hours={hours}
                setHours={setHours}
                fuelLevel={fuelLevel}
                setFuelLevel={setFuelLevel}
                disableButton={disableButton}
                validationSearch={validationSearch}
                validationWarningMsg={validationWarningMsg}
                checklistStatus={checklistStatus}
                checkFormItems={checkFormItems}
                setCheckFormItems={setCheckFormItems}
                checkFormComments={checkFormComments}
                setCheckFormComments={setCheckFormComments}
                submitClicked={submitClicked}
                setSubmitClicked={setSubmitClicked}
                checkItems={checkItems}
              />
            ) : (
              <div className="loading-screen p-d-flex p-jc-center">
                <LoadingText
                  text={t("unfinishedChecksPanel.get_check_detail_placeholder_text")}
                  spinnerColor={"#8D249899"}
                />
              </div>
            )}
          </form>
        </div>
      )}
    </div>
  );
};

export default UnfinishedChecksPanel;
