import React from "react";
import "../../styles/ShareComponents/Error404.scss";
import Robot from "../../../src/images/robots/robot-404.png";

const Error404 = () => {
  return (
    <div className="error404">
      <div className="error404-display flex-cent">
        <p className="error404-num">4</p>
        <img className="error404-img" src={Robot} alt="Fleet-guru meditating" />
        <p className="error404-num">4</p>
      </div>
      <p className="error404-msg">It's not you. The page you were looking for disappeared.</p>
    </div>
  );
};

export default Error404;
