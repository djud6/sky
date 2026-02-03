import React, { useContext } from "react";
import { GHGContext } from "../GasEmissionsCalculator";
import "../../../styles/GHGCalculator/GHGWelcome.scss";
import GHGNavBar from "./GHGNavBar";
import Gradient from "../../../images/background/welcome-gradient.png";

const GHGWelcome = () => {
  const { setPage } = useContext(GHGContext);

  const handleGetStarted = () => {
    setPage(2);
  };

  return (
    <div className="ghg-welcome">
      <div className="ghg-welcome__header">
        <h1 className="ghg-welcome__brand">LOKOMOTIVE</h1>
      </div>
      <img className="ghg-welcome__gradient" src={Gradient} />

      <div className="ghg-welcome__content">
        <h2 className="ghg-welcome__title">
          Estimate your fleet's <br /> greenhouse gas <br /> emissions in 3 steps
        </h2>

        <button className="ghg-welcome__button" onClick={handleGetStarted}>
          Let's go!
        </button>
      </div>
      <GHGNavBar />
    </div>
  );
};

export default GHGWelcome;
