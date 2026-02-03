import React from "react";
import { InputNumber } from "primereact/inputnumber";

const CostInput = ({ label, value, setError, setInput, currencyFor, error, loading }) => {
  return (
    <React.Fragment>
      <label>{label}</label>
      <div className="p-inputgroup">
        <InputNumber
          id="minmaxfraction"
          placeholder={label}
          value={value}
          onValueChange={(e) => {
            setError(false);
            setInput(e.value);
          }}
          mode="currency"
          currency={currencyFor ? currencyFor.code : "USD"}
          locale="en-US"
          className={error && !value ? "p-invalid" : ""}
          disabled={loading}
        />
      </div>
    </React.Fragment>
  );
};

export default CostInput;
