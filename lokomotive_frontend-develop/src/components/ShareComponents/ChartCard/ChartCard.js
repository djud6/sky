import React, { useState, useEffect, useRef } from "react";
import Tooltip from "../Tooltip/Tooltip";
import { useTranslation } from "react-i18next";
import { isMobileDevice } from "../../../helpers/helperFunctions";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";

/**
 * Share chart card component with title and description
 *
 * @param {String} title table column header title array (REQUIRED)
 * @param {String} description Chart Description (shown as subtitle)
 * @param {Object} filter Filter component for the chart
 */

// Description not currently being used with v4 design
const ChartCard = ({
  children,
  title,
  subTitle,
  innerDetails,
  filter,
  flexbox,
  tooltipName,
  moreSpace = null,
}) => {
  const cardRef = useRef(<div />);
  const isMobile = isMobileDevice();
  const [width, setWidth] = useState(null);
  const { t } = useTranslation();

  useEffect(() => {
    setWidth(cardRef.current.offsetWidth);
  }, [cardRef.current.offsetHeight]);

  return (
    <div
      className={`overflow-hidden rounded w-100 chart-card-container ${
        isMobile ? "p-pt-2" : "p-pt-3"
      }`}
      ref={cardRef}
    >
      <div className="row no-gutters pt-2 pb-2 justify-content-start fleet-card-title form-tooltip">
        <div className="col-11">
          <h5 className="text-uppercase chart-card-title drag-handle" style={{ display: "inline" }}>
            {title}
          </h5>
          {tooltipName && (
            <Tooltip
              label={tooltipName}
              description={t(`general.tooltip_${tooltipName}`)}
              styles={{ verticalAlign: "super" }}
            />
          )}

          {subTitle && (
            <div>
              <h6
                className="text-uppercase chart-card-subtitle drag-handle"
                style={{ display: "inline" }}
              >
                {subTitle}
              </h6>
            </div>
          )}
          {innerDetails}
        </div>
      </div>
      <div
        className={`chart-filter ml-auto mt-3 col-12 d-flex justify-content-end ${
          width > 300 && filter ? "col-md-4" : "col-md-7"
        } `}
      >
        {filter}
      </div>

      {!moreSpace ? <br /> : null}
      <div className={`${flexbox ? "chartCard-flexbox" : ""} chart-content`}>{children}</div>
    </div>
  );
};

export default ChartCard;
