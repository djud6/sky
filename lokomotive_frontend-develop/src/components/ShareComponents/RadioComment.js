import React from "react";
import { RadioButton } from "primereact/radiobutton";
import { InputText } from "primereact/inputtext";
import Tooltip from "./Tooltip/Tooltip";
import { useTranslation } from "react-i18next";

// labels is an array, first element is question label, subsequent elements are radio button labels
const RadioComment = ({
  value,
  onRadioChange,
  onCommentChange,
  name,
  comment,
  labels,
  fontStyle = "h5",
  tooltip,
  subitem,
  submitClicked,
}) => {
  const { t } = useTranslation();
  return (
    <div className={`${subitem ? "p-d-flex p-mb-2 p-flex-wrap" : ""}`}>
      <label
        className={`${
          subitem
            ? "p-d-flex p-ai-center p-mb-0 p-mr-3 " + fontStyle
            : "font-weight-bold p-mt-2 p-mb-0 " + fontStyle
        }`}
      >
        {labels[0]}
        <Tooltip
          hidden={!tooltip}
          label={tooltip ? tooltip.label : null}
          description={tooltip ? tooltip.description : null}
        />
      </label>
      <div className="p-d-flex p-flex-wrap p-py-2">
        <div className="p-d-flex p-ai-center">
          <RadioButton
            inputId={`${name}_option1`}
            value={value}
            name={name}
            checked={value === true}
            onChange={() => onRadioChange(true)}
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
            checked={value === false}
            onChange={() => onRadioChange(false)}
          />
          <label htmlFor={`${name}_option2`} className="mb-0 ml-2 mr-3">
            {labels[2] ? labels[2] : "No"}
          </label>
          <div>
            {(value === true || value === false) && (
              <InputText
                value={comment || ""}
                className={`p-inputtext-sm p-mr-3 ${submitClicked && !comment && "p-invalid"} ${
                  !value && !comment && "border-danger"
                }`}
                placeholder={
                  value
                    ? t("lookupDailyCheckPanelIndex.comments_optional")
                    : t("lookupDailyCheckPanelIndex.comments_required")
                }
                onChange={(e) => onCommentChange(e.target.value)}
              />
            )}
            {submitClicked && !comment && !value && (
              <small className="p-error p-d-block">
                {t("lookupDailyCheckPanelIndex.comments_required")}
              </small>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RadioComment;
