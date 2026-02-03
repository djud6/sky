import React from "react";
import { InputTextarea } from "primereact/inputtextarea";
import "../../styles/ShareComponents/CustomTextArea.scss";

const CustomTextArea = ({ value, placeholder="", onChange, rows, leftStatus }) => {
  return (
    <div className={`custom-input-area ${leftStatus ? "left-status" : ""}`}>
      <InputTextarea
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        rows={rows}
      />
    </div>
  )
}

export default CustomTextArea;