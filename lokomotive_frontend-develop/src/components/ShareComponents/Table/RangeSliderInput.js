import React from "react";
import { InputNumber } from "primereact/inputnumber";

const RangeSliderInput = ({
  minValue,
  maxValue,
  valueGap,
  setMinValue,
  setMaxValue,
  max,
  buffer,
}) => {
  const handleMinValueChange = (e) => {
    const newMinValue = parseInt(e.target.value);
    if (maxValue - newMinValue >= valueGap) {
      setMinValue(newMinValue);
    }
  };
  const handleMaxValueChange = (e) => {
    const newMaxValue = parseInt(e.target.value);
    if (newMaxValue <= e.target.max && newMaxValue - minValue >= valueGap) {
      setMaxValue(newMaxValue);
    }
  };
  const calculateLeftPercentage = () => {
    return (minValue / max) * 100;
  };
  const calculateRightPercentage = () => {
    return 100 - (maxValue / max) * 100;
  };
  return (
    <div>
      <div className="slider">
        <div
          className="progress"
          style={{
            left: `${calculateLeftPercentage()}%`,
            right: `${calculateRightPercentage()}%`,
          }}
        ></div>
        <div className="price-fields">
          <div className="field">
            <InputNumber
              className="min"
              value={minValue}
              onValueChange={(e) => {
                const newValue = e.target.value;
                if (newValue <= maxValue) {
                  setMinValue(newValue);
                }
              }}
            />

            <InputNumber
              className="max"
              value={maxValue}
              onValueChange={(e) => {
                const newValue = e.target.value;
                if (newValue >= minValue) {
                  setMaxValue(newValue);
                }
              }}
            />
          </div>
        </div>
      </div>
      <div className="range-input">
        <input
          type="range"
          className="range-min"
          min="0"
          max={max}
          value={minValue}
          step={valueGap}
          onChange={handleMinValueChange}
        />
        <input
          type="range"
          className="range-max"
          min="0"
          max={max}
          value={maxValue}
          step={valueGap}
          onChange={handleMaxValueChange}
        />
      </div>
    </div>
  );
};

export default RangeSliderInput;
