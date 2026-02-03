import React from "react";
import { InputText } from "primereact/inputtext";
import { SelectButton } from 'primereact/selectbutton';
import Tooltip from "../Tooltip/Tooltip";
import { useTranslation } from "react-i18next";
import "./SelectComment.scss";

// labels is an array, first element is question label, subsequent elements are radio button labels
const SelectComment = ({
  value,
  onRadioChange,
  onCommentChange,
  comment,
  labels,
  fontStyle = "h5",
  tooltip,
  subitem,
  submitClicked,
}) => {
  const { t } = useTranslation();
  const options = [
    {name: labels[1] || t("general.yes"), value: true},
    {name: labels[2] || t("general.no"), value: false}
  ];

  return (
    <div className="p-mb-3 custom-select-comment">
      <label
        className={`${
          subitem
            ? "check-item-label p-mb-0 p-mt-2 " + fontStyle
            : "check-item-label p-mt-2 p-mb-0 " + fontStyle
        }`}
      >
        {labels[0]}
        <Tooltip
          hidden={!tooltip}
          label={tooltip ? tooltip.label : null}
          description={tooltip ? tooltip.description : null}
        />
      </label>
      <div className="p-d-flex p-flex-column op-ckeck-button">
        <div className="p-my-2">
          <SelectButton
            className="w-100"
            value={value}
            options={options} 
            onChange={(e) => onRadioChange(e.value)} 
            optionLabel="name"
          />
        </div>
        {value === true || value === false ? (
          <div>
            <InputText
              value={comment || ""}
              className={`p-inputtext-sm w-100 p-mb-2 ${value === false && submitClicked && !comment && "p-invalid"} ${
                !value && !comment && "border-danger"
              }`}
              placeholder={value === true ?
                t("lookupDailyCheckPanelIndex.comments_optional")
                :
                t("lookupDailyCheckPanelIndex.comments_required")
              }
              onChange={(e) => onCommentChange(e.target.value)}
            />
            {value === false && submitClicked && !comment && (
              <h5 className="p-error p-d-block">
                {t("lookupDailyCheckPanelIndex.comments_required_msg")}
              </h5>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default SelectComment;
