import React, { useContext, useMemo } from "react";
import { GHGContext } from "../GasEmissionsCalculator";
import { calculationsConfig } from "../../../constants/calculationsConfig";

const InputsForm = () => {
  const { scope, continent, fleetType, inputs, setInputs } = useContext(GHGContext);

  // Memoizes the current configuration
  const config = useMemo(() => {
    return calculationsConfig?.[scope]?.[continent]?.[fleetType] || null;
  }, [scope, continent, fleetType]);

  if (!config) {
    return <p>No configuration available for this selection.</p>;
  }

  const handleChange = (key, value) => {
    setInputs((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  return (
    <form className="flex flex-col gap-3">
      {config.inputs.map((input) => (
        <div key={input.key}>
          <label htmlFor={input.key} className="block font-medium">
            {input.label}
          </label>
          <input
            id={input.key}
            type={input.type}
            value={inputs[input.key] || ""}
            onChange={(e) => handleChange(input.key, e.target.value)}
            className="form-control"
          />
        </div>
      ))}
    </form>
  );
};

export default InputsForm;
