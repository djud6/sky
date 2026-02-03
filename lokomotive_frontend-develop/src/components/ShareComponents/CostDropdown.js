import React from "react";
import { Dropdown } from "primereact/dropdown";

const CostDropdown = ({
  label,
  value,
  options,
  setError,
  setSelection,
  dataReady,
  error,
  optionLabel = "name",
}) => {
  return (
    <React.Fragment>
      <label>{label}</label>
      <div className="p-inputgroup">
        <Dropdown
          value={value}
          options={options}
          onChange={(e) => {
            setError(false);
            setSelection(e.value);
          }}
          optionLabel={optionLabel}
          placeholder={label}
          disabled={!dataReady}
          className={error && !value ? "p-invalid" : ""}
        />
        {!dataReady ? (
          <span className="p-inputgroup-addon">
            <i className="pi pi-spin pi-spinner" />
          </span>
        ) : value ? (
          <span className="p-inputgroup-addon">
            <i className="pi pi-check" style={{ color: "green" }} />
          </span>
        ) : error ? (
          <span className="p-inputgroup-addon">
            <i className="pi pi-times" style={{ color: "red" }} />
          </span>
        ) : (
          <span className="p-inputgroup-addon">
            <i className="pi pi-clock" />
          </span>
        )}
      </div>
    </React.Fragment>
  );
};

export default CostDropdown;
