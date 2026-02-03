import React from "react";
import PropTypes from "prop-types";
import CurrentDate from "./CurrentDate";
import { useMediaQuery } from "react-responsive";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import "../../../styles/ShareComponents/PanelHeader.scss";

const PanelHeader = ({ icon, text, currentDate, disableBg, mobileBg }) => {
  const isBigScreen = useMediaQuery({ query: '(min-width: 520px)' });

  return (
    <div className={`media panel-header p-d-flex p-flex-column ${disableBg ? "disable-bg" : ""} ${mobileBg ? "mobile-bg" : ""}`}>
      <div className="p-d-flex p-ai-center">
        <FontAwesomeIcon icon={icon} size={isBigScreen ? "3x" : "2x"} color="white" />
        <div className="heading-div">
          <div className="media-body mx-3">
            <h1 className="heading text-uppercase panel-text text-white p-m-0">{text}</h1>
          </div>
        </div>
      </div>
      {isBigScreen && currentDate !== "disabled" &&
        <h5 className="panel-date text-white p-mt-3 p-mb-2">{currentDate === undefined ? CurrentDate() : currentDate}</h5>
      }
    </div>
  );
};

PanelHeader.propTypes = {
  text: PropTypes.string.isRequired,
  currentDate: PropTypes.string,
};

export default PanelHeader;