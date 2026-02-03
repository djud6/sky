import React from "react";
import { AiOutlineInfoCircle } from "react-icons/ai";
import ReactTooltip from "react-tooltip";
import RobotImage from "../../../images/robots/robot-hi.png";
import "../../../styles/ShareComponents/Tooltip/Tooltip.scss";

const Tooltip = ({ label, description, hidden, size = 18, styles = {} }) => {
  return (
    <div hidden={hidden} className="pl-2" style={{ display: "inline", ...styles }}>
      <AiOutlineInfoCircle size={size} data-tip data-for={label} />
      <ReactTooltip id={label} place="right">
      <div className="tool-tip-content">
          <div className="robot-image">
            <img src={RobotImage} alt="placeholder" width="43" height="55" />
          </div>
          <div className="description">{description}</div>
        </div>
      </ReactTooltip>
    </div>
  );
};

export default Tooltip;
