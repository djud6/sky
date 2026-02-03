import React, { useState } from "react";
import { Button } from "primereact/button";
import { useTranslation } from "react-i18next";
import "../../styles/chartLegend.scss";

const ChartLegend = ({ legendRef, chartId, toggleLegend }) => {
  const { t } = useTranslation();
  const [flip, setFlip] = useState(false);

  return (
    <React.Fragment>
      <Button
        label={t("general.show_legend")}
        className="p-button-link p-mb-2 legend-link"
        onClick={(e) => {
          document.getElementById(chartId).style.display = flip ? "none" : "block";
          setFlip((fl) => !fl);
          e.target.innerText = !flip ? t("general.hide_legend") : t("general.show_legend");
          toggleLegend(chartId);
        }}
      />
      <div id={chartId} className="legend-dialog">
        <div ref={legendRef} />
      </div>
    </React.Fragment>
  );
};

export default ChartLegend;
