import React from "react";
import HomeIcon from "../../../images/icons/home.png";
import VehicleIcon from "../../../images/icons/vehicle.png";
import ToolsIcon from "../../../images/icons/tools.png";
import FuelIcon from "../../../images/icons/fuel.png";
import EnergyIcon from "../../../images/icons/energy.png";
import RecycleIcon from "../../../images/icons/recycle.png";
import SettingsIcon from "../../../images/icons/settings.png";

const GHGNavBar = () => {
  return (
    <div className="ghg-welcome__nav">
      <button className="ghg-welcome__nav-icon" aria-label="Home">
        <img src={HomeIcon} alt="Home icon" />
      </button>

      <button className="ghg-welcome__nav-icon" aria-label="Vehicle">
        <img src={VehicleIcon} alt="Vehicle icon" />
      </button>

      <button className="ghg-welcome__nav-icon" aria-label="Tools">
        <img src={ToolsIcon} alt="Tools icon" />
      </button>

      <button className="ghg-welcome__nav-icon" aria-label="Fuel">
        <img src={FuelIcon} alt="Fuel icon" />
      </button>

      <button className="ghg-welcome__nav-icon" aria-label="Energy">
        <img src={EnergyIcon} alt="Energy icon" />
      </button>

      <button className="ghg-welcome__nav-icon" aria-label="Recycle">
        <img src={RecycleIcon} alt="Recycle icon" />
      </button>

      <button className="ghg-welcome__nav-icon" aria-label="Settings">
        <img src={SettingsIcon} alt="Settings icon" />
      </button>
    </div>
  );
};

export default GHGNavBar;
