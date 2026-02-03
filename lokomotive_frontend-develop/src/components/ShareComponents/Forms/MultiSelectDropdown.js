import React, { useState } from "react";
import { MultiSelect } from "primereact/multiselect";
import "../../../styles/ShareComponents/CustomMultiSelect.scss";

const MultiSelectDropdown = ({
  style = null,
  classNames,
  value,
  options,
  onChange,
  filterMatchMode = "startsWith",
  optionLabel = "name",
  maxSelectedLabels = 7,
  selectionLimit = null,
  selectedItemsLabel = `{0} items selected`,
  itemTemplate = null,
  panelHeaderTemplate = null,
  panelFooterTemplate = null,
  display = "comma",
  leftStatus,
  disabled,
  placeholder,
}) => {
  const [open, setOpen] = useState(false);

  const handleOpen = () => {
    setOpen(!open);
  };

  return (
    <div className="custom-multi-select" style={style}>
      <MultiSelect
        className={` 
          ${classNames ? classNames : ""} 
          ${open ? "focused" : null}
          ${value.length !== 0 ? "activated-icon" : ""}
          ${leftStatus ? "left-status" : ""}
        `}
        panelClassName="custom-multi-dropdown"
        value={value}
        options={options}
        onChange={onChange}
        filter
        filterMatchMode={filterMatchMode}
        optionLabel={optionLabel}
        maxSelectedLabels={maxSelectedLabels}
        selectionLimit={selectionLimit}
        selectedItemsLabel={selectedItemsLabel}
        itemTemplate={itemTemplate}
        panelHeaderTemplate={panelHeaderTemplate}
        panelFooterTemplate={panelFooterTemplate}
        disabled={disabled}
        display={display}
        onShow={handleOpen}
        onHide={handleOpen}
        placeholder={placeholder}
      />
    </div>
  );
};

export default MultiSelectDropdown;
