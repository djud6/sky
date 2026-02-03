import moment from 'moment';
import ConsoleHelper from "../../../helpers/ConsoleHelper"

const TimeZoneDate = (date) => {
  //Getting local date
  const todayDate = moment().format("YYYY-MM-DD");
  //Converting recieved date
  const currentDate = moment(date, "YYYY-MM-DD");
  //Calculating date difference
  const delta = Number(moment.duration(currentDate.diff(todayDate)).asDays().toFixed());
  delta > 0 && ConsoleHelper(`Provided Date is from future (+${delta} days)! Adjusting to current date`)
  //If the date is from future then return current date
  return (
    delta > 0 ? todayDate._i : currentDate._i
    )
}

export default TimeZoneDate;
