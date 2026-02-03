import React from "react";
import { InputNumber } from "primereact/inputnumber";
import "../../styles/ShareComponents/CustomInputText.scss";

const CustomInputNumber = ({
  placeholder = "",
  value,
  onChange,
  leftStatus,
  className,
  mode,
  minFractionDigits,
  maxFractionDigits,
  min,
  max,
  suffix,
  style,
}) => {
  return (
    <div className={`custom-input-text ${leftStatus ? "left-status" : ""}`}>
      <InputNumber
        placeholder={placeholder}
        className={className}
        value={value}
        onChange={(e) => onChange(e.value)}
        mode={mode}
        minFractionDigits={minFractionDigits}
        maxFractionDigits={maxFractionDigits}
        min={min}
        max={max}
        suffix={suffix}
        style={style}
      />
    </div>
  );
};

export default CustomInputNumber;
