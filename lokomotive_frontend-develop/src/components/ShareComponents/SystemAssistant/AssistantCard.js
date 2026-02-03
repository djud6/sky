import React, { useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import robotOn from "../../../images/menu/topbar_menu_robot_on.png";
import "../../../styles/ShareComponents/SystemAssistant/AssistantCard.scss";

const AssistantCard = ({ step, setStep, title, content, image, setAssistantStatus }) => {
  const { t } = useTranslation();
  const totalSteps = 5;

  const usePrevious = (value) => {
    const ref = useRef();
    useEffect(() => {
      ref.current = value;
    });
    return ref.current;
  };

  const onNext = () => {
    if (step !== totalSteps) setStep(step + 1);
    else setAssistantStatus(false);
  };

  const prevStep = usePrevious(step);

  return (
    <React.Fragment>
      <div className={`fleetguru-son ${step === totalSteps ? "son-show" : "son-hide"}`}>
        <img src={robotOn} alt="" />
      </div>
      <div
        className={`assistant-card p-d-flex p-flex-column 
        ${
          prevStep < step || prevStep === undefined
            ? `assistant-card-${step}`
            : `assistant-card-reverse-${step}`
        }`}
      >
        <div className="assistant-header p-d-flex p-jc-end">
          <Button icon="pi pi-times" onClick={() => setAssistantStatus(false)} />
        </div>
        <div className="assistant-content p-d-flex">
          <div className="fleet-guru-img">
            <img src={image} alt="fleet_guru" />
          </div>
          <div className="content-details p-d-flex p-flex-column">
            <div className="title">{title}</div>
            <div className="content">{content}</div>
          </div>
        </div>
        <div className="assistant-dot-btn p-d-flex">
          {[...Array(totalSteps)].map((e, i) => {
            return (
              <div
                key={i}
                className={`dot-btn ${step === i + 1 ? "dot-btn-active" : ""}`}
                onClick={() => setStep(i + 1)}
              />
            );
          })}
        </div>
        <div className="assistant-footer p-d-flex p-jc-between">
          <Button
            label={t("general.previous").toUpperCase()}
            icon="pi pi-arrow-left"
            disabled={step === 1}
            onClick={() => setStep(step - 1)}
          />
          <Button
            label={`${
              step === totalSteps
                ? t("general.done").toUpperCase()
                : t("general.next").toUpperCase()
            }`}
            icon="pi pi-arrow-right"
            iconPos="right"
            onClick={() => onNext()}
          />
        </div>
      </div>
    </React.Fragment>
  );
};

export default AssistantCard;
