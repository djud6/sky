import React, { useState, useEffect } from "react";
import axios from "axios";
import swal from "sweetalert";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { capitalize } from "../../../helpers/helperFunctions";
import { Button } from "primereact/button";
import { Checkbox } from "primereact/checkbox";
import CardWidget from "../../ShareComponents/CardWidget";
import WarningMsg from "../../ShareComponents/WarningMsg";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import CustomInputText from "../../ShareComponents/CustomInputText";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import "../../../styles/tooltipStyles.scss";
import "../../../styles/helpers/button2.scss";

const AddMaintenanceRuleDialog = ({
  vehicle,
  maintenanceTypes,
  rule = null,
  setForceUpdateTable,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [maintenanceType, setMaintenanceType] = useState(
    rule
      ? maintenanceTypes.filter((item) => item.inspection_name === rule.inspection_type)[0].id
      : null
  );
  const [selectedMileage, setSelectedMileage] = useState(rule ? rule.mileage_cycle : "");
  const [selectedHours, setSelectedHours] = useState(rule ? rule.hour_cycle : "");
  const [selectedDuration, setSelectedDuration] = useState(
    rule && rule.time_cycle !== -1 ? rule.time_cycle : ""
  );
  // eslint-disable-next-line no-unused-vars
  const [selectedApplyToSimilar, setSelectedApplyToSimilar] = useState(false);
  const [selectedSpan, setSelectedSpan] = useState(null);
  const [defaultSpan, setDefaultSpan] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const spanOptions = ["days", "months", "years"].map((el) => ({ name: el, code: el }));

  useEffect(() => {
    const def = spanOptions.find((el) => el.code === "days");
    setDefaultSpan(def);
    setSelectedSpan(def.code);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedSpan === "days") {
      setSelectedDuration(rule && rule.time_cycle !== -1 ? rule.time_cycle : "");
    } else {
      setSelectedDuration("");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSpan]);

  const handleSave = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    if (
      !maintenanceType ||
      (vehicle.hours_or_mileage.toLowerCase() === "hours" &&
        !selectedHours &&
        (!selectedSpan || (selectedSpan && !selectedDuration))) ||
      (vehicle.hours_or_mileage.toLowerCase() === "mileage" &&
        !selectedMileage &&
        (!selectedSpan || (selectedSpan && !selectedDuration))) ||
      (vehicle.hours_or_mileage.toLowerCase() === "both" &&
        !selectedHours &&
        !selectedMileage &&
        (!selectedSpan || (selectedSpan && !selectedDuration)))
    ) {
      swal(
        t("maintenanceForecastPanel.alert_emptyError_title"),
        t("maintenanceForecastPanel.alert_emptyError_text"),
        "error"
      );
      return;
    }

    const headers = getAuthHeader();
    headers.headers["Content-Type"] = "application/json";
    const requestConfig = {
      method: "post",
      url: `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Forecast/Rule/Add`,
      ...headers,
      data: {
        data: {
          VIN: vehicle.VIN,
          inspection_type: maintenanceType,
          ...(["hours", "both"].includes(vehicle.hours_or_mileage.toLowerCase()) &&
            selectedHours && {
              hour_cycle: parseInt(selectedHours),
            }),
          ...(["mileage", "both"].includes(vehicle.hours_or_mileage.toLowerCase()) &&
            selectedMileage && {
              mileage_cycle: parseInt(selectedMileage),
            }),
          ...(selectedDuration &&
            selectedSpan === "days" && { time_cycle: parseInt(selectedDuration) }),
          ...(selectedDuration &&
            selectedSpan === "months" && { time_cycle: parseInt(selectedDuration) * 30 }),
          ...(selectedDuration &&
            selectedSpan === "years" && { time_cycle: parseInt(selectedDuration) * 365 }),
        },
        apply_to_similar_type: selectedApplyToSimilar,
      },
    };
    loadingAlert();
    axios(requestConfig)
      .then(() => {
        successAlert();
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
        setForceUpdateTable(Date.now);
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  return (
    <React.Fragment>
      {!isMobile ? (
        <React.Fragment>
          <div className="form-title">
            <h5 className="p-text-uppercase">
              {!!rule
                ? t("maintenanceForecastPanel.editing_existing_rule")
                : t("maintenanceForecastPanel.creating_new_rule")}{" "}
              - {t("maintenanceForecastPanel.vin_label")}: {vehicle.VIN} - {vehicle.asset_type}
            </h5>
          </div>
          <div className="rule-form">
            <form>
              <div className="p-d-flex p-jc-between">
                <label className="form-tooltip">
                  {t("general.inspection_type")}
                  <Tooltip
                    label={"type-select"}
                    description={t("maintenanceForecastPanel.tooltip_type_define")}
                  />
                </label>
                {!!rule ? (
                  <div className="w-50 p-d-flex p-align-center">
                    <h4 className="text-white">{rule.inspection_type}</h4>
                  </div>
                ) : (
                  <div className="w-50">
                    <FormDropdown
                      onChange={setMaintenanceType}
                      options={
                        maintenanceTypes &&
                        maintenanceTypes.map((type) => ({
                          name: type.inspection_name,
                          code: type.id,
                        }))
                      }
                      loading={!maintenanceTypes}
                      disabled={!!rule}
                      plain_dropdown
                      leftStatus
                    />
                  </div>
                )}
              </div>
              <div className="subtitle">
                <label className="p-mt-3 form-tooltip">
                  {t("maintenanceForecastPanel.cycle_period_label")}
                  <Tooltip
                    label={"cycle-period"}
                    description={t("maintenanceForecastPanel.tooltip_cycle_select")}
                  />
                </label>
              </div>
              {vehicle.hours_or_mileage.toLowerCase() === "hours" ||
              vehicle.hours_or_mileage.toLowerCase() === "both" ? (
                <div className="p-d-flex p-jc-between p-ai-center p-mt-3 sub-form">
                  <label>{t("maintenanceForecastPanel.hours_label")}</label>
                  <div className="w-50">
                    <CustomInputText
                      type="text"
                      value={selectedHours}
                      onChange={setSelectedHours}
                      keyfilter={/^\d*\.?\d*$/}
                      leftStatus
                    />
                  </div>
                </div>
              ) : null}
              {vehicle.hours_or_mileage.toLowerCase() === "mileage" ||
              vehicle.hours_or_mileage.toLowerCase() === "both" ? (
                <div className="p-d-flex p-jc-between p-ai-center p-mt-3 sub-form">
                  <label>{t("maintenanceForecastPanel.mileage_label")}</label>
                  <div className="w-50">
                    <CustomInputText
                      type="text"
                      value={selectedMileage}
                      onChange={setSelectedMileage}
                      keyfilter={/^\d*\.?\d*$/}
                      leftStatus
                    />
                  </div>
                </div>
              ) : null}
              <div className="p-d-flex p-jc-between p-ai-center p-mt-3 sub-form">
                <FormDropdown
                  classnames="mb-0"
                  defaultValue={defaultSpan}
                  onChange={setSelectedSpan}
                  options={spanOptions}
                  loading={!spanOptions.length}
                  dataReady={spanOptions.length}
                  plain_dropdown
                  leftStatus
                />
                <div className="w-50">
                  <CustomInputText
                    type="text"
                    value={selectedDuration}
                    onChange={setSelectedDuration}
                    leftStatus
                    keyfilter={/^\d*\.?\d*$/}
                  />
                </div>
              </div>
              <div className="p-d-flex p-jc-end p-mt-3 sub-form apply-similar">
                <div className="w-50 p-d-flex">
                  <Checkbox
                    onChange={(e) => setSelectedApplyToSimilar(e.checked)}
                    checked={selectedApplyToSimilar}
                  />
                  <div className="apply-text">
                    {t("maintenanceForecastPanel.apply_to_all_label")}
                  </div>
                  <Tooltip
                    label={"tooltip-all"}
                    description={t("maintenanceForecastPanel.tooltip_apply_all")}
                  />
                </div>
              </div>
            </form>
          </div>
          <div className="p-d-flex p-jc-end p-mb-4 p-mt-5">
            <div className="w-50 btn-2 save-rule-btn">
              <Button
                className="w-100"
                label={t("maintenanceForecastPanel.button_save")}
                onClick={handleSave}
              />
            </div>
          </div>
          <WarningMsg
            message={
              "Disclaimer: You are responsible for any deviation from recommended manufacturer maintenance cycles"
            }
          />
        </React.Fragment>
      ) : (
        <div className="p-mx-3">
          <div className="form-title p-my-3">
            <h5 className="p-text-uppercase">
              {!!rule
                ? t("maintenanceForecastPanel.editing_existing_rule")
                : t("maintenanceForecastPanel.creating_new_rule")}
            </h5>
            <h6 className="p-text-uppercase">
              {t("maintenanceForecastPanel.vin_label")}: {vehicle.VIN} - {vehicle.asset_type}
            </h6>
          </div>
          <div className="rule-form">
            <form>
              <CardWidget status={maintenanceType}>
                <label className="h6 form-tooltip">
                  {t("general.inspection_type")}
                  {!isMobile && (
                    <Tooltip
                      label={"type-select"}
                      description={t("maintenanceForecastPanel.tooltip_type_define")}
                    />
                  )}
                </label>
                {!!rule ? (
                  <h5 className="text-white p-m-0">{rule.inspection_type}</h5>
                ) : (
                  <div className="w-100">
                    <FormDropdown
                      onChange={setMaintenanceType}
                      options={
                        maintenanceTypes &&
                        maintenanceTypes.map((type) => ({
                          name: type.inspection_name,
                          code: type.id,
                        }))
                      }
                      loading={!maintenanceTypes}
                      disabled={!!rule}
                      plain_dropdown
                    />
                  </div>
                )}
              </CardWidget>
              {vehicle.hours_or_mileage.toLowerCase() === "hours" ||
              vehicle.hours_or_mileage.toLowerCase() === "both" ? (
                <CardWidget status={selectedHours}>
                  <label className="h6">{t("maintenanceForecastPanel.hours_label_mobile")}</label>
                  <CustomInputText
                    type="text"
                    value={selectedHours}
                    onChange={setSelectedHours}
                    keyfilter={/^\d*\.?\d*$/}
                  />
                </CardWidget>
              ) : null}
              {vehicle.hours_or_mileage.toLowerCase() === "mileage" ||
              vehicle.hours_or_mileage.toLowerCase() === "both" ? (
                <CardWidget status={selectedMileage}>
                  <label className="h6">{t("maintenanceForecastPanel.mileage_label_mobile")}</label>
                  <CustomInputText
                    type="text"
                    value={selectedMileage}
                    onChange={setSelectedMileage}
                    keyfilter={/^\d*\.?\d*$/}
                  />
                </CardWidget>
              ) : null}
              <CardWidget status={selectedDuration}>
                <label className="h6">{t("maintenanceForecastPanel.select_span_mobile")}</label>
                <div className="w-100 mb-3">
                  <FormDropdown
                    defaultValue={defaultSpan}
                    onChange={setSelectedSpan}
                    options={spanOptions}
                    loading={!spanOptions.length}
                    dataReady={spanOptions.length}
                    plain_dropdown
                    leftStatus
                  />
                </div>
                <label className="h6">
                  {t("maintenanceForecastPanel.span_label_mobile", {
                    span_option: capitalize(selectedSpan),
                  })}
                </label>
                <CustomInputText
                  type="text"
                  value={selectedDuration}
                  onChange={setSelectedDuration}
                  keyfilter={/^\d*\.?\d*$/}
                />
              </CardWidget>
              <div className="apply-similar p-d-flex p-ai-center p-mb-3">
                <Checkbox
                  onChange={(e) => setSelectedApplyToSimilar(e.checked)}
                  checked={selectedApplyToSimilar}
                />
                <div className="apply-text">{t("maintenanceForecastPanel.apply_to_all_label")}</div>
                <Tooltip
                  label={"tooltip-all-mobile"}
                  description={t("maintenanceForecastPanel.tooltip_apply_all")}
                />
              </div>
            </form>
          </div>
          <WarningMsg
            message={
              "Disclaimer: You are responsible for any deviation from recommended manufacturer maintenance cycles"
            }
          />
          <div className="p-d-flex p-jc-end p-mt-4 p-mb-5">
            <div className="w-100 btn-2 save-rule-btn">
              <Button
                className="w-100"
                label={t("maintenanceForecastPanel.button_save")}
                onClick={handleSave}
              />
            </div>
          </div>
        </div>
      )}
    </React.Fragment>
  );
};

export default AddMaintenanceRuleDialog;
