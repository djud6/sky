import React from "react";

const SecondaryInfoView = ({ titles, values }) => {
  return (
    <div>
      <div className="p-d-flex p-flex-column p-flex-md-row">
        <div className="p-p-2 flex-fill">
          {titles.map((title, index) => {
            if (index % 2 === 0) {
              return (
                <div className="p-d-flex" key={index}>
                  <div className="mr-auto p-p-2 text-uppercase font-weight-bold">{title}</div>
                  <div className="p-p-2">{values[index]}</div>
                </div>
              );
            }
            return null;
          })}
        </div>
        <div className="p-p-2 flex-fill">
          {titles.map((title, index) => {
            if (index % 2) {
              return (
                <div className="p-d-flex" key={index}>
                  <div className="mr-auto p-2 text-uppercase font-weight-bold">{title}</div>
                  <div className="p-p-2">{values[index]}</div>
                </div>
              );
            }
            return null;
          })}
        </div>
      </div>
    </div>
  );
};

export default SecondaryInfoView;