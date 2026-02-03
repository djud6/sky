export const calculationsConfig = {
  "scope1": {
    "North America": {
      "Aviation": {
        equationId: "NA_eq_1",
        equation: (inputs) => inputs.fuelUse * inputs.emissionFactor,
        inputs: [
          { key: "fuelUse", label: "Fuel Use (liters)", type: "number" },
          { key: "emissionFactor", label: "Emission Factor (kg CO₂/liter)", type: "number" },
        ],
        outputLabel: "Emissions (kg CO₂)"
      },
      "Marine": {
        equationId: "NA_eq_2",
        equation: (inputs) =>
          inputs.power * inputs.activity * inputs.emissionFactor * inputs.llaf,
        inputs: [
          { key: "power", label: "Engine Power (kW)", type: "number" },
          { key: "activity", label: "Engine Activity (hours)", type: "number" },
          { key: "emissionFactor", label: "Emission Factor (g/kWh)", type: "number" },
          { key: "llaf", label: "Low Load Adjustment Factor", type: "number" },
        ],
        outputLabel: "Emissions per vessel (g)"
      },
      "Railroad": {
        equations: {
          allocation: (inputs) =>
            inputs.fuelNational * (inputs.trackLengthLocal / inputs.trackLengthNational),
          emissions: (inputs, F_ci) => F_ci * inputs.emissionFactor,
        },
        inputs: [
          { key: "fuelNational", label: "National Fuel Consumption (liters)", type: "number" },
          { key: "trackLengthLocal", label: "Local Track Length (km)", type: "number" },
          { key: "trackLengthNational", label: "National Track Length (km)", type: "number" },
          { key: "emissionFactor", label: "Emission Factor (kg/liter)", type: "number" },
        ],
        outputLabel: "Emissions (kg)"
      }
    },
    "Europe": {
      "Marine": {
        equationId: "EU_eq_1",
        equation: (inputs) =>
          Object.keys(inputs.fuelMass).reduce((total, type) => {
            const Mi = inputs.fuelMass[type];
            const MiNC = inputs.nonCombusted[type] || 0;
            const EF = inputs.emissionFactors[type];
            return total + (Mi - MiNC) * EF;
          }, 0),
        inputs: [
          { key: "fuelMass", label: "Fuel Mass (tons)", type: "dict" },
          { key: "nonCombusted", label: "Non-combusted Fuel", type: "dict" },
          { key: "emissionFactors", label: "Emission Factors", type: "dict" },
        ],
        outputLabel: "Total CO₂ Emissions (kg)"
      }
    }
  }
};
