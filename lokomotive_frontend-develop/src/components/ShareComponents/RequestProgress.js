import React, { useState, useEffect } from "react";
import robotStep1 from "../../images/robots/stepper/robot_step_1.png";
import robotStep2 from "../../images/robots/stepper/robot_step_2.png";
import robotStep3 from "../../images/robots/stepper/robot_step_3.png";
import robotStep4 from "../../images/robots/stepper/robot_step_4.png";
import robotStep5 from "../../images/robots/stepper/robot_step_5.png";
import "../../styles/ShareComponents/RequestProgress.scss";

const RequestProgress = ({ steps, contents, activeStep, layout = "horizontal" }) => {
  const [activeIndex, setActiveIndex] = useState(0);
  const stepImages = [robotStep1, robotStep2, robotStep3, robotStep4, robotStep5, robotStep1, robotStep2, robotStep3, robotStep4];

  useEffect(() => {
    let index = steps.findIndex((step) => step.toLowerCase() === activeStep.toLowerCase());
    setActiveIndex(index);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeStep]);

  return (
    <React.Fragment>
      <div className={`request-progress request-progress-${layout}`}>
        {steps.map((step, index) => (
          <div
            key={index}
            className={`
              progress-event
              ${activeIndex === index ? "connector-extend" : ""}
            `}
          >
            {activeIndex === index && (
              <div className="progress-event-robot">
                <img src={stepImages[index]} alt="step-img" />
              </div>
            )}
            <div
              className={`
              progress-event-content
              ${activeIndex === index ? "content-active" : ""}`}
            >
              <div className="title">{step}</div>
              {activeIndex === index && <div className="details">{contents[index]}</div>}
            </div>
            <div className="progress-event-separator">
              <div
                className={`
                marker
                ${activeIndex > index ? "marker-active" : ""}
                ${activeIndex === index ? "marker-grow" : ""}`}
              />
              {index + 1 < steps.length && (
                <div
                  className={`
                  connector
                  ${activeIndex > index ? "connector-active" : ""}`}
                />
              )}
            </div>
          </div>
        ))}
      </div>
    </React.Fragment>
  );
};

export default RequestProgress;
