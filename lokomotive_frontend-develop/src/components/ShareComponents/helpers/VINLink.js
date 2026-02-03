import React from 'react';
import {useHistory} from 'react-router-dom';

const VINLink = ({ vin, classnames }) => {
  let history = useHistory();
  return (
    <a
      className={`${classnames ? classnames : ""}`}
      href="/#" 
      onClick={(e) => {
        e.preventDefault();
        history.push(`/asset-details/${vin}`);
      }}
    >
      {vin}
    </a>
  );
};

export default VINLink;
