import React from "react";
import { RadioButton } from "primereact/radiobutton";
import Tooltip from "./Tooltip/Tooltip";
import "../../styles/ShareComponents/GeneralRadio.scss";

// labels is an array, first element is question label, subsequent elements are radio button labels
const GeneralRadio = ({ classnames, value, onChange, name, labels, fontStyle, tooltip }) => {
  return (
    <div className="custom-radio-btn">
      <label className={`check-item-label ${classnames ? classnames : ""} ${fontStyle ? fontStyle : ""}`}>
        {labels[0]}
        <Tooltip
          hidden={!tooltip}
          label={tooltip ? tooltip.label : null}
          description={tooltip ? tooltip.description : null}
        />
      </label>
      <div className="p-d-flex p-flex-wrap custom-button-style">
        <div className="p-d-flex p-ai-center">
          <RadioButton
            inputId={`${name}_option1`}
            value={value}
            name={name}
            checked={value === true && value !== ""}
            onChange={() => onChange(true)}
          />
          <label htmlFor={`${name}_option1`} className="mb-0 ml-2 mr-3">
            {labels[1] ? labels[1] : "Yes"}
          </label>
        </div>
        <div className="p-d-flex p-ai-center">
          <RadioButton
            inputId={`${name}_option2`}
            value={value}
            name={name}
            checked={value === false && value !== ""}
            onChange={() => onChange(false)}
          />
          <label htmlFor={`${name}_option2`} className="mb-0 ml-2 mr-3">
            {labels[2] ? labels[2] : "No"}
          </label>
        </div>
      </div>
    </div>
  );
};

export default GeneralRadio;
