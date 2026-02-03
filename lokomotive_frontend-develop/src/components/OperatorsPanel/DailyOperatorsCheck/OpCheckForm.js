import React from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { InputText } from "primereact/inputtext";
import { Button } from "primereact/button";
import { Slider } from "primereact/slider";
import { RadioButton } from "primereact/radiobutton";
import ChecklistItem from "../../ShareComponents/ChecklistItem";
import CardWidget from "../../ShareComponents/CardWidget";
import WarningMsg from "../../ShareComponents/WarningMsg";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import RadioComment from "../../ShareComponents/RadioComment";
import SelectComment from "../../ShareComponents/SelectComment/SelectComment";
import "../../../styles/helpers/button1.scss";
import "../../../styles/OperatorsPanel/OpCheckForm.scss";

const OpCheckForm = ({
  selectedTitle,
  vehicle,
  operable,
  setOperable,
  walkAroundInspection,
  setWalkAroundInspection,
  damage,
  setDamage,
  mileage,
  setMileage,
  hours,
  setHours,
  fuelLevel,
  setFuelLevel,
  disableButton,
  validationSearch,
  validationWarningMsg,
  checklistStatus,
  checkFormItems,
  setCheckFormItems,
  checkFormComments,
  setCheckFormComments,
  submitClicked,
  setSubmitClicked,
  checkItems,
}) => {
  const { t } = useTranslation();
  const isBigScreen = useMediaQuery({ query: "(min-width: 769px)" });
  const pysicalDamages = [
    { name: t("lookupDailyCheckPanelIndex.pysical_damage_major"), key: "M" },
    { name: t("lookupDailyCheckPanelIndex.pysical_damage_cosmetic"), key: "C" },
    { name: t("lookupDailyCheckPanelIndex.pysical_no_damage"), key: "N" },
  ];
  const subCheckTitles = ["lights", "fluids", "leaks", "safety_equipment"];
  const subCheckItems = [
    "headlights",
    "backup_lights",
    "trailer_light_cord",
    "oil",
    "transmission_fluid",
    "steering_fluid",
    "hydraulic_fluid",
    "brake_fluid",
    "hydraulic_hoses",
    "trailer_air_lines",
    "other_leaks",
    "fire_extinguisher",
  ];

  let isItemsCheckDisplayed = false;
  for (const item in checkItems) {
    isItemsCheckDisplayed = checkItems[item] || isItemsCheckDisplayed;
  }

  return (
    <div className={`op-check-form ${isBigScreen ? "p-mt-5" : "p-mt-2"}`}>
      <h4>{selectedTitle}</h4>
      <h5 className="p-mb-5">{`[${t("general.asset_type")}: ${vehicle.asset_type}]`}</h5>
      <ChecklistItem
        value={operable}
        onChange={setOperable}
        name={"operableRadio"}
        labels={[t("lookupDailyCheckPanelIndex.is_the_asset_operable")]}
        status={operable !== "" ? true : false}
      />
      {operable === false && (
        <div className="p-mt-5 p-d-flex p-jc-center btn-1">
          <Link
            to={{
              pathname: "/issues/new",
              query: { vehicle: vehicle },
            }}
            className="no-underline"
          >
            <Button label={t("lookupDailyCheckPanelIndex.report_new_issue_btn")} />
          </Link>
        </div>
      )}
      {operable && (
        <ChecklistItem
          value={walkAroundInspection}
          onChange={setWalkAroundInspection}
          name={"walkAroundRadio"}
          labels={[t("lookupDailyCheckPanelIndex.was_walk_around_inspection_performed")]}
          status={walkAroundInspection !== "" ? true : false}
        />
      )}
      {walkAroundInspection === false && operable === true && (
        <WarningMsg message={t("lookupDailyCheckPanelIndex.complete_walk_around_inspection")} />
      )}
      {operable && walkAroundInspection && (
        <CardWidget status={damage} YN>
          <label className="h5">{t("lookupDailyCheckPanelIndex.physical_damage")}</label>
          <div className="p-d-flex p-flex-wrap">
            {pysicalDamages.map((status) => {
              return (
                <div key={status.key} className="p-d-flex p-ai-center p-my-1">
                  <RadioButton
                    inputId={status.key}
                    name="pysical_damage"
                    value={status}
                    onChange={(e) => setDamage(e.value)}
                    checked={damage.key === status.key}
                  />
                  <label className="mb-0 ml-2 mr-3" htmlFor={status.key}>
                    {status.name}
                  </label>
                </div>
              );
            })}
          </div>
        </CardWidget>
      )}
      {damage.name === t("lookupDailyCheckPanelIndex.pysical_damage_major") &&
        walkAroundInspection === true &&
        operable === true && (
          <div className="btn-1 p-mt-3 p-d-flex p-jc-center p-mt-4 p-mb-5">
            <Link
              to={{
                pathname: "/issues/new",
                query: { vehicle: vehicle },
              }}
              className="no-underline"
            >
              <Button label={t("lookupDailyCheckPanelIndex.report_new_issue_btn")} />
            </Link>
          </div>
        )}
      {operable &&
        walkAroundInspection &&
        damage &&
        damage.name !== t("lookupDailyCheckPanelIndex.pysical_damage_major") && (
          <div className="check-list form-tooltip">
            <br />
            {isItemsCheckDisplayed && (
              <React.Fragment>
                <h4 className="p-mb-3">{t("lookupDailyCheckPanelIndex.visual_op_check")}</h4>
                <CardWidget status={checklistStatus}>
                  {Object.keys(checkItems).map((name, i) => {
                    return checkItems[name] && name === "fuel" ? (
                      <div key={`${name}${i}`}>
                        <label className="h5 p-mt-2 font-weight-bold">
                          {t(`lookupDailyCheckPanelIndex.${name}`)}: {fuelLevel}%
                          <Tooltip
                            label={name}
                            description={t(`lookupDailyCheckPanelIndex.tooltip_${name}`)}
                          />
                        </label>
                        {isBigScreen ? (
                          <div className="p-pl-1 p-pt-2 p-pb-4" style={{ width: "300px" }}>
                            <Slider
                              value={fuelLevel}
                              onChange={(e) => setFuelLevel(e.value)}
                              step={25}
                            />
                          </div>
                        ) : (
                          <div className="p-pl-1 p-pt-2 p-pb-4 w-100">
                            <Slider
                              value={fuelLevel}
                              onChange={(e) => setFuelLevel(e.value)}
                              step={25}
                            />
                          </div>
                        )}
                      </div>
                    ) : checkItems[name] && subCheckTitles.indexOf(name) > -1 ? (
                      <label
                        key={`${name}${i}`}
                        className="h4 p-mt-3 font-weight-bold list-subtitle"
                      >
                        {t(`lookupDailyCheckPanelIndex.${name}`)}
                        <Tooltip
                          label={name}
                          description={t(`lookupDailyCheckPanelIndex.tooltip_${name}`)}
                        />
                      </label>
                    ) : checkItems[name] && subCheckItems.indexOf(name) > -1 ? (
                      isBigScreen ? (
                        <RadioComment
                          key={`${name}${i}`}
                          value={checkFormItems[name]}
                          name={`${name}RadioOPCheck`}
                          comment={checkFormComments[name]}
                          labels={[
                            t(`lookupDailyCheckPanelIndex.${name}`),
                            t("lookupDailyCheckPanelIndex.satisfactory"),
                            t("lookupDailyCheckPanelIndex.unsatisfactory"),
                          ]}
                          onRadioChange={(v) => setCheckFormItems({ ...checkFormItems, [name]: v })}
                          onCommentChange={(c) => {
                            setSubmitClicked(false);
                            setCheckFormComments({ ...checkFormComments, [name]: c });
                          }}
                          submitClicked={submitClicked}
                        />
                      ) : (
                        <div key={`${name}${i}`} className="mobile-check-list">
                          <SelectComment
                            subitem
                            fontStyle="h5"
                            value={checkFormItems[name]}
                            name={`${name}RadioOPCheck`}
                            comment={checkFormComments[name]}
                            labels={[
                              t(`lookupDailyCheckPanelIndex.${name}`),
                              t("lookupDailyCheckPanelIndex.satisfactory"),
                              t("lookupDailyCheckPanelIndex.unsatisfactory"),
                            ]}
                            onRadioChange={(v) =>
                              setCheckFormItems({ ...checkFormItems, [name]: v })
                            }
                            onCommentChange={(c) => {
                              setSubmitClicked(false);
                              setCheckFormComments({ ...checkFormComments, [name]: c });
                            }}
                            submitClicked={submitClicked}
                          />
                        </div>
                      )
                    ) : checkItems[name] ? (
                      isBigScreen ? (
                        <div key={`${name}${i}`} className="p-my-1">
                          <RadioComment
                            tooltip={{
                              label: name,
                              description: t(`lookupDailyCheckPanelIndex.tooltip_${name}`),
                            }}
                            value={checkFormItems[name]}
                            comment={checkFormComments[name]}
                            name={`${name}RadioOPCheck`}
                            labels={[
                              t(`lookupDailyCheckPanelIndex.${name}`),
                              t("lookupDailyCheckPanelIndex.satisfactory"),
                              t("lookupDailyCheckPanelIndex.unsatisfactory"),
                            ]}
                            onRadioChange={(v) =>
                              setCheckFormItems({ ...checkFormItems, [name]: v })
                            }
                            onCommentChange={(c) => {
                              setSubmitClicked(false);
                              setCheckFormComments({ ...checkFormComments, [name]: c });
                            }}
                            submitClicked={submitClicked}
                          />
                        </div>
                      ) : (
                        <div key={`${name}${i}`} className="mobile-check-list">
                          <SelectComment
                            tooltip={{
                              label: name,
                              description: t(`lookupDailyCheckPanelIndex.tooltip_${name}`),
                            }}
                            fontStyle="h5"
                            value={checkFormItems[name]}
                            comment={checkFormComments[name]}
                            name={`${name}RadioOPCheck`}
                            labels={[
                              t(`lookupDailyCheckPanelIndex.${name}`),
                              t("lookupDailyCheckPanelIndex.satisfactory"),
                              t("lookupDailyCheckPanelIndex.unsatisfactory"),
                            ]}
                            onRadioChange={(v) =>
                              setCheckFormItems({ ...checkFormItems, [name]: v })
                            }
                            onCommentChange={(c) => {
                              setSubmitClicked(false);
                              setCheckFormComments({ ...checkFormComments, [name]: c });
                            }}
                            submitClicked={submitClicked}
                          />
                        </div>
                      )
                    ) : null;
                  })}
                </CardWidget>
              </React.Fragment>
            )}
            <div>
              {vehicle.hours_or_mileage.toLowerCase() === "mileage" ||
              vehicle.hours_or_mileage.toLowerCase() === "both" ? (
                <CardWidget status={mileage ? true : false}>
                  <label className="h5">{t("general.mileage")}</label>
                  <span className="p-input-icon-right w-100">
                    {validationSearch ? <i className="pi pi-spin pi-spinner" /> : null}
                    <InputText
                      className="w-100"
                      placeholder={t("general.enter_mileage")}
                      onChange={(e) => setMileage(e.target.value)}
                      keyfilter={/^\d*\.?\d*$/}
                      disabled={validationSearch}
                    />
                  </span>
                </CardWidget>
              ) : null}
              {vehicle.hours_or_mileage.toLowerCase() === "hours" ||
              vehicle.hours_or_mileage.toLowerCase() === "both" ? (
                <CardWidget status={hours ? true : false}>
                  <label className="h5">{t("general.hours")}</label>
                  <span className="p-input-icon-right w-100">
                    {validationSearch ? <i className="pi pi-spin pi-spinner" /> : null}
                    <InputText
                      className="w-100"
                      placeholder={t("general.enter_hours")}
                      onChange={(e) => setHours(e.target.value)}
                      keyfilter={/^\d*\.?\d*$/}
                      disabled={validationSearch}
                    />
                  </span>
                </CardWidget>
              ) : null}
              {validationWarningMsg && (
                <div className="p-mt-3">
                  <WarningMsg message={validationWarningMsg} sm />
                </div>
              )}
              <div>
                <div className="p-mt-5 p-mb-5 p-pb-5">
                  {submitClicked && (
                    <div className="p-d-flex p-jc-center p-mb-2">
                      <h6 className="p-error p-d-block">
                        {t("lookupDailyCheckPanelIndex.comments_required_warning_msg")}
                      </h6>
                    </div>
                  )}
                  <div className="btn-1 p-d-flex p-jc-center">
                    <Button
                      type="submit"
                      disabled={disableButton || validationSearch}
                      label={t("lookupDailyCheckPanelIndex.submit_operator_check_btn")}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
    </div>
  );
};

export default OpCheckForm;
