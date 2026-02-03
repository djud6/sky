import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Dropdown } from "primereact/dropdown";
import "../../../styles/ShareComponents/Forms/FormDropdown.scss";

const FormDropdown = ({
  reset,
  label,
  defaultValue,
  onChange,
  onFocus,
  options = null,
  loading,
  custom_width,
  plain_dropdown,
  disabled,
  dataReady,
  leftStatus,
  placeholder,
  panelclassnames,
  itemTemplate,
  classnames,
}) => {
  const [selected, setSelected] = useState("");
  const [open, isOpen] = useState(false);
  const { t } = useTranslation();

  useEffect(() => {
    if (defaultValue && dataReady) {
      setSelected(defaultValue);
    }
  }, [defaultValue, dataReady]);

  let childCount;
  useEffect(() => {
    if (reset !== "disabled") {
      setSelected("");
    }
  }, [reset]);

  if (options) {
    childCount = options.length;
  }

  const handleOpen = () => {
    isOpen(!open);
  };

  return (
    <div
      className={`form-group FORMDROP row align-self-center
        ${selected ? "activated-styles" : "default-styles"} 
        ${leftStatus ? "left-status" : ""} 
        ${custom_width ? "w-75" : ""}
        ${classnames ? classnames : ""}`}
    >
      {label ? (
        <div className="col-4">
          <label className="col-form-label">{label}</label>
        </div>
      ) : null}
      <div className={`p-inputgroup ${plain_dropdown ? "col-12" : "col-8"}`}>
        <Dropdown
          panelClassName={`dropdown-content-form ${
            navigator.userAgent && navigator.userAgent.indexOf("Windows") !== -1 && "p-ml-2"
          } ${panelclassnames}`}
          className={`${open ? "focused" : ""} ${loading ? "loading" : ""} ${
            selected ? "activated-styles-inner " : "default-styles-inner"
          }`}
          value={selected}
          options={options}
          onChange={(event) => {
            setSelected(event.value);
            onChange(event.value.code);
          }}
          onFocus={(event) => {
            if (onFocus) {
              onFocus(event);
            }
          }}
          optionLabel="name"
          placeholder={`
            ${
              placeholder
                ? placeholder
                : childCount !== 0
                ? t("formDropdown.default")
                : t("formDropdown.no_results")
            }
          `}
          disabled={disabled || childCount === 0}
          onShow={handleOpen}
          onHide={handleOpen}
          itemTemplate={itemTemplate}
        />
      </div>
    </div>
  );
};

//todo: use loading prop to render spinner instead of the chevron down
export default FormDropdown;
