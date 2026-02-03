import React, { useContext } from "react";
import { GHGContext } from "../GasEmissionsCalculator";

const FleetSelector = () => {
  const { fleetType, setFleetType } = useContext(GHGContext);
  const fleetTypes = ["Aviation", "Marine", "Railroad", "Road"];

  return (
    <select
      className="form-control"
      autoComplete="off"
      id="fleetType"
      name="fleetType"
      value={fleetType}
      onChange={(event) => setFleetType(event.target.value)}
    >
      <option value="" disabled>
        Select fleet type
      </option>
      
    {/* fleet type = ft */}
      {fleetTypes.map((ft) => (
        <option key={ft} value={ft}>
          {ft}
        </option>
      ))}
    </select>
  );
};

export default FleetSelector;
