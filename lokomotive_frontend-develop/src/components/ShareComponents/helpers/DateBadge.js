import React from 'react';
import moment from 'moment';

const DateBadge = ({ currentDate, dateRange, disableGreen }) => {
  let colorClass;
  const getDayDifference = () => {
    const todayDate = moment().format("YYYY-MM-DD");
    //if estimated date is not stated - no color needed
    if (currentDate === null) {
      return 2;
    }
    const estDeliveryDate = moment(currentDate, "YYYY-MM-DD");
    return Number(moment.duration(estDeliveryDate.diff(todayDate)).asDays().toFixed());
  };
  // when Expected Delivery Date is tmrw or today - Orange badge; When Expected date is passed - red badge; else - no color
  const delta = getDayDifference();
  if (delta >= dateRange && !disableGreen) {
    colorClass = "badge-success";
  } else if (delta >= dateRange && disableGreen) {
    colorClass = "badge-warning";
  }
  if (delta < dateRange && delta >= 0) colorClass = "badge-warning";
  if (delta < 0) colorClass = "badge-danger";

  return (
    <span className={`badge badge-pill ${colorClass}`}>
      {currentDate}
    </span>
  )
}

export default DateBadge;
