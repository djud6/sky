import React, { useEffect, useState } from "react";
import axios from "axios";
import swal from "sweetalert";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { faCalendarCheck } from "@fortawesome/free-solid-svg-icons";
import { getAuthHeader, getRolePermissions } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import WarningMsg from "../../ShareComponents/WarningMsg";
import { errorAlert, successAlert, loadingAlert } from "../../ShareComponents/CommonAlert";
import OpCheckForm from "./OpCheckForm";
import ConfigureDialog from "./ConfigureDialog";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import { Button } from "primereact/button";
import "../../../styles/OperatorsPanel/DailyOperatorsCheck.scss";

const DailyOperatorsCheckPanel = () => {
  const { t } = useTranslation();
  const [vehicle, setVehicle] = useState(null);
  const [checkItems, setCheckItems] = useState(null);
  const [dataReady, setDataReady] = useState(false);
  const [checksDialog, setchecksDialog] = useState(false);
  const [forceUpdate, setForceUpdate] = useState(Date.now());
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    setDataReady(false);
    setCheckItems(null);
    if (vehicle) {
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Get/Checks/${vehicle.VIN}`, {
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
          setDataReady(true);
          setCheckItems(checks);
        })
        .catch((error) => {
          setDataReady(false);
          errorAlert(error.customErrorMsg);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
  }, [vehicle]);

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["Daily Check", "Unfinished", "Lookup"]}
          activeTab={"Daily Check"}
          urls={["/operators", "/operators/unfinished-checks", "/operators/lookup"]}
        />
      )}
      <PanelHeader
        icon={faCalendarCheck}
        text={t("lookupDailyCheckPanelIndex.daily_operators_check")}
      />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Daily Check", "Unfinished Checks", "Lookup"]}
          activeTab={"Daily Check"}
          urls={["/operators", "/operators/unfinished-checks", "/operators/lookup"]}
        />
      )}
      <React.Fragment>
        <div className={`${isMobile ? "p-pb-4" : "p-mt-5"} flex-wrap search-configure-check`}>
          <div className="search-container">
            <VINSearch
              key={forceUpdate}
              onVehicleSelected={(v) => {
                if (!!v) setVehicle(v);
              }}
            />
          </div>
          {getRolePermissions().role.toLowerCase() !== "operator" && (
            <div className={`configure-container ml-auto ${isMobile ? "p-mr-2" : "p-mr-4"}`}>
              <Button
                className="p-button-rounded"
                label={!isMobile ? "Configure Checks" : ""}
                icon="pi pi-sliders-v"
                onClick={() => setchecksDialog(true)}
              />
            </div>
          )}
        </div>
        <ConfigureDialog checksDialog={checksDialog} setchecksDialog={setchecksDialog} />
        {vehicle &&
          !Array.isArray(vehicle) &&
          dataReady &&
          (vehicle.status.toLowerCase() !== "inoperative" ? (
            <div>
              <DailyOperatorCheckForm
                checkItems={checkItems}
                vehicle={vehicle}
                setForceUpdate={setForceUpdate}
                resetForm={setVehicle}
                selectedTitle={`${t("lookupDailyCheckPanelIndex.create_oper_check_for_vin", {
                  vehicleVIN: vehicle.VIN,
                })}`}
              />
            </div>
          ) : (
            <div className={`${isMobile ? "p-mx-3 p-mt-3" : ""}`}>
              <WarningMsg message={t("lookupDailyCheckPanelIndex.inoperative_warning_msg")} />
            </div>
          ))}
      </React.Fragment>
    </div>
  );
};

const DailyOperatorCheckForm = ({
  checkItems,
  vehicle,
  resetForm,
  selectedTitle,
  setForceUpdate,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
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

  const subCheckTitles = ["lights", "fluids", "leaks", "safety_equipment"];

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
  }, [vehicle]);

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
        VIN: vehicle.VIN,
        operable: operable,
        fuel: fuelLevel,
        ...(vehicle.hours_or_mileage.toLowerCase() === "both" && {
          mileage: parseFloat(mileage),
          hours: parseFloat(hours),
        }),
        ...(vehicle.hours_or_mileage.toLowerCase() === "mileage" && {
          mileage: parseFloat(mileage),
        }),
        ...(vehicle.hours_or_mileage.toLowerCase() === "hours" && { hours: parseFloat(hours) }),
      },
      comments: commentArray,
    };

    errors ? setSubmitClicked(true) : sendOperatorCheck(operatorCheck);
    setForceUpdate(Date.now());
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
        resetForm(null);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
      })
      .catch((error) => {
        errorAlert(error.customErrorMsg, operatorCheck);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  useEffect(() => {
    if (mileage || hours) {
      if (vehicle.hours_or_mileage.toLowerCase() === "both" && !hours) {
        setValidationWarningMsg("Please provide hours for auto-validation.");
      } else if (vehicle.hours_or_mileage.toLowerCase() === "both" && !mileage) {
        setValidationWarningMsg("Please provide mileage for auto-validation.");
      } else {
        const delayDebounceFn = setTimeout(() => {
          setValidationSearch(true);
          setValidationWarningMsg(null);
          axios
            .post(
              `${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Validate/Usage`,
              {
                VIN: vehicle.VIN,
                mileage: parseFloat(mileage),
                hours: parseFloat(hours),
              },
              getAuthHeader()
            )
            .then((response) => {
              setValidationSearch(false);
            })
            .catch((error) => {
              setValidationWarningMsg(error.customErrorMsg);
              setValidationSearch(false);
              ConsoleHelper(error);
            });
        }, 1000);
        return () => clearTimeout(delayDebounceFn);
      }
    }
  }, [mileage, hours]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
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

        if (vehicle.hours_or_mileage.toLowerCase() === "both" && (!mileage || !hours)) {
          setDisableButton(true);
        } else if (vehicle.hours_or_mileage.toLowerCase() === "hours" && !hours) {
          setDisableButton(true);
        } else if (vehicle.hours_or_mileage.toLowerCase() === "mileage" && !mileage) {
          setDisableButton(true);
        } else {
          setDisableButton(false);
        }
      }
    }
  }, [vehicle.hours_or_mileage, mileage, hours, checkFormItems]); // eslint-disable-line react-hooks/exhaustive-deps

  const errorAlert = (errorMsg, data) => {
    return swal({
      title: t("general.error"),
      text: errorMsg,
      icon: "error",
      buttons: { resend: t("general.try_again"), cancel: t("general.cancel") },
    }).then((value) => {
      if (value === "resend") sendOperatorCheck(data);
    });
  };

  if (!vehicle) return null;

  return (
    <div className="report-form-container p-mx-3">
      <form onSubmit={handleSubmit}>
        <OpCheckForm
          selectedTitle={selectedTitle}
          vehicle={vehicle}
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
      </form>
    </div>
  );
};

export default DailyOperatorsCheckPanel;
