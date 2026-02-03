import React from "react";
import "../../styles/ShareComponents/ChecklistItem.scss";
import CardWidget from "./CardWidget";
import GeneralRadio from "./GeneralRadio";
// labels is an array, first element is question label, subsequent elements are radio button labels
const ChecklistItem = ({ value, onChange, name, labels, fontStyle = "h5", status, tooltip }) => {
  return (
    <CardWidget YN status={status}>
      <GeneralRadio
        value={value}
        onChange={onChange}
        name={name}
        labels={labels}
        fontStyle={fontStyle}
        tooltip={tooltip}
      />
    </CardWidget>
  );
};

export default ChecklistItem;
