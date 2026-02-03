import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import AssistantCard from "./AssistantCard";
import RobotHi from "../../../images/robots/robot-hi.png";
import RobotHandout from "../../../images/robots/robot-handout.png";
import "../../../styles/ShareComponents/SystemAssistant/SystemAssistant.scss";

const SystemAssistant = ({ setAssistantStatus }) => {
  const { t } = useTranslation();
  const [step, setStep] = useState(1);

  return (
    <div className={`assistant-overlay assistant-overlay-${step} opac`}>
      <AssistantCard
        step={step}
        setStep={setStep}
        title={t(`fleetGuruAssistant.title_step_${step}`)}
        content={t(`fleetGuruAssistant.content_step_${step}`)}
        image={step === 1 ? RobotHi : RobotHandout}
        setAssistantStatus={setAssistantStatus}
      />
    </div>
  )
}

export default SystemAssistant;