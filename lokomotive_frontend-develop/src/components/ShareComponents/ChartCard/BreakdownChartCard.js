import React from "react";
import SolidGaugeChart from "./SolidGaugeChart";
import { useTranslation } from "react-i18next";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";
import { time } from "@amcharts/amcharts4/core";

const BreakdownChartCard = ({
  chartParams,
  title,
  innerRadius = 80,
  legend = true,
  size = "10px",
  legendPosition = "right",
  legendValign = "top",
  oneYearTimePeriod,
  isMobile,
}) => {
  const { t } = useTranslation();
  if (!!!chartParams) return null;
  // Prepare data
  let labels = chartParams.map((chartParam) => chartParam.label);
  let colors = ["#1A76C4", "#32D500", "#9e16c7", "#e60b1a", "#f2fa05", "#84403e", "#83a7a0", "#93d2b4", "#f5f689", "#1b011c", "#36c017", "#210deb", "#404040", ];
  let timePeriod = oneYearTimePeriod ? t("general.chart_time_span_year"): t("general.chart_time_span");
  return (
    <div className="fleet-card chart-card-container">
      <h2 className={`text-white ${!isMobile && "ml-5 mt-3"} ${isMobile && "h5 text-center"}`}>
        {title}
      </h2>
      <h4
        style={!isMobile ? { marginRight: "21.5%"} : { fontSize: "small" }}
        className={`position-relative text-white ${isMobile ? "text-center mt-3" : "text-left ml-5"}`}
      >
        {timePeriod}
      </h4>
      <div className="row no-gutters align-items-center">
        <div className="col align-self-center">
          <div style={{padding: "2em"}}>
            <SolidGaugeChart
              data={chartParams}
              labels={labels}
              colors={colors}
              centerText={title}
              titleText={title}
              size={size}
              legendPosition={legendPosition}
              legendValign={legendValign}
              innerRadius={innerRadius}
              legend={legend}
              isMobile={isMobile}
            />
          </div>
        </div>
      </div>
      
    </div>
  );
};

export default BreakdownChartCard;
