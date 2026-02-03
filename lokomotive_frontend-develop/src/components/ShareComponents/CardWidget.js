import React from "react";
import "../../styles/ShareComponents/CardWidget.scss";

const CardWidget = ({ children, status, YN, blueBg, lightBg }) => {
  return (
    <div
      className={`cardWid card no-gutter widget-overview-box 
        ${YN ? "YNCard" : "none"}
        ${status ? "widget-overview-box-3" : "widget-overview-box-4"}
        ${blueBg ? "blue-bg" : ""}
        ${lightBg ? "light-bg" : ""}
      `}
    >
      <div className="p-d-flex p-flex-column">{children}</div>
    </div>
  );
};

export default CardWidget;
