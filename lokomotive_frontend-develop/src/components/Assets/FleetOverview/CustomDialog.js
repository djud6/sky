import React, { useState, useEffect } from "react";
import axios from "axios";
import { Dialog } from "primereact/dialog";
import { Button } from "primereact/button";
import "../../../styles/OperatorsPanel/DailyOperatorsCheck.scss";
import { ToggleButton } from "primereact/togglebutton";
import { capitalize } from "../../../helpers/helperFunctions";

const CustomDialog = ({ checksDialog, setchecksDialog }) => {
  const [checkedFilters, setCheckedFilters] = useState([]);
  const [eventTypeFilter, setEventTypeFilter] = useState([]);
  const [theAllFilter, setTheAllFilter] = useState(true);
  const [eventTypes, setEventTypes] = useState([]);

  const columns = [
    "unit number",
    "model number",
    "manufacturer",
    "company",
    "year of manufacture",
    "fuel type", 
    "license plate", 
    "parent asset", 
    "child asset", 
    "daily average hours", 
    "cost of ownership"
  ]

  useEffect(() => {
    if (checksDialog) {
      setEventTypes(columns);
    }
  }, [checksDialog]);

  const handleTheAllFilter = () => {
    const clearAllFilters = new Array(checkedFilters.length).fill(false);
    setCheckedFilters(clearAllFilters);
    setTheAllFilter(true);
    setEventTypeFilter([]);
  };

  const filtersHandler = (eventType, i) => {
    let copyOfCheckedFilters = [...checkedFilters];
    copyOfCheckedFilters[i] = !checkedFilters[i];
    setCheckedFilters(copyOfCheckedFilters);
    setTheAllFilter(false);
    let copyOfEventTypeFilter = [...eventTypeFilter];
    if (eventTypeFilter.includes(eventType)) {
      copyOfEventTypeFilter = copyOfEventTypeFilter.filter((type) => type !== eventType);
      setEventTypeFilter(copyOfEventTypeFilter);
      if (copyOfEventTypeFilter.length === 0) setTheAllFilter(!theAllFilter);
    } else {
      copyOfEventTypeFilter.push(eventType);
      setEventTypeFilter(copyOfEventTypeFilter);
    }
  };

  const filterButtons = eventTypes.map((eventType, i) => {
    return (
      <ToggleButton
        key={eventType + i}
        checked={checkedFilters[i]}
        onChange={() => filtersHandler(eventType, i)}
        onLabel={capitalize(eventType)}
        offLabel={capitalize(eventType)}
        onIcon=""
        offIcon=""
        className="p-mr-2 p-mb-2 p-button-rounded"
      />
    );
  });

  const add_extracolumns = () => {
    
    setchecksDialog(false)
  }

  const renderFooter = () => {
    return (
      <div>
        <Button
          label="Cancel"
          icon="pi pi-times"
          className="p-button-text"
          onClick={() => setchecksDialog(false)}
        />
        <Button
          label="Confirm"
          icon="pi pi-check"
          onClick={add_extracolumns}
        />
      </div>
    );
  };

  return (
    <Dialog
      className="custom-main-dialog configure-checks-dialog"
      header={"Custom Columns"}
      visible={checksDialog}
      onHide={() => setchecksDialog(false)}
      style={{ width: "60vw" }}
      breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
      footer={renderFooter()}
    >
      
      <div className="p-field">
            <ToggleButton
              checked={theAllFilter}
              onChange={handleTheAllFilter}
              onLabel="None"
              offLabel="None"
              onIcon=""
              offIcon=""
              className="p-mr-2 p-mb-2 p-button-rounded"
            />
            {filterButtons}
        </div>


    </Dialog>
  );
};

export default CustomDialog;