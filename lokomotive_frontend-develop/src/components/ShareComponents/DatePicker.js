// /* global $ */
import React from "react";
import "react-datepicker/dist/react-datepicker.css";
import "../../styles/ShareComponents/datePicker.scss";
import { Calendar } from "primereact/calendar";
import { useTranslation } from "react-i18next";

const DatePicker = ({ onChange, initialDate, minDate = null, maxDate = null, leftStatus }) => {
  const { t } = useTranslation();
  return (
    <div className={`custom-datepicker ${leftStatus ? "left-status" : ""}`}>
      <Calendar
        className={`cal ${initialDate ? "cal-active" : null}`}
        panelClassName="dropdown-content-cal"
        showIcon
        showButtonBar
        value={initialDate}
        minDate={minDate}
        maxDate={maxDate}
        onChange={(e) => onChange(e.value)}
        placeholder={t("formDropdown.datetime")}
      />
    </div>
  );
};

export default DatePicker;
