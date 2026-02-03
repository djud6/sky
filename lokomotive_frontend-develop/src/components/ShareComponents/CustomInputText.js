import React, { useRef, useEffect } from "react";
import { InputText } from "primereact/inputtext";
import "../../styles/ShareComponents/CustomInputText.scss";

const CustomInputText = ({
  classnames,
  type,
  placeholder = "",
  value,
  onChange,
  leftStatus,
  keyfilter,
}) => {
  const inputBox = useRef(null);

  useEffect(() => {
    const currInputBox = inputBox.current;
    if (currInputBox) {
      const classList = currInputBox.classList;
      if (value) {
        classList.add("p-filled");
      } else {
        classList.remove("p-filled");
      }
    }
  }, [value]);

  return (
    <div
      className={`
      custom-input-text
      ${leftStatus ? "left-status" : ""} 
      ${classnames ? classnames : ""}`}
    >
      <InputText
        type={type}
        placeholder={placeholder}
        value={value}
        keyfilter={keyfilter}
        onChange={(e) => onChange(e.target.value)}
        ref={inputBox}
      />
    </div>
  );
};

export default CustomInputText;
