import React from "react";
import "../../styles/ShareComponents/InfoCard.scss";

// Content would be a component or div to fill the info card
const InfoCard = ({ children }) => {
  return (
    <div className="infoCard">
      <div className="infoCard-inner">{children}</div>
    </div>
  );
};

export default InfoCard;
