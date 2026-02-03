import React from "react";
import { ProgressSpinner } from 'primereact/progressspinner';

const Spinner = ({ children }) => {
  return (
    <div className="text-center m-4">
      <ProgressSpinner style={{width: '60px', height: '60px', marginTop: "16px"}} strokeWidth="5" />
      {children}
    </div>
  )
};

export default Spinner;