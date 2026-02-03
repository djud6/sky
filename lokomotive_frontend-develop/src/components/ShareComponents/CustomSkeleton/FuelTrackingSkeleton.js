import React from "react";
import FullWidthSkeleton from "./FullWidthSkeleton";

const FuelTrackingSkeleton = () => {
  return (
    <div>
      <div className="p-pt-5 p-d-flex p-jc-around">
        <FullWidthSkeleton height="500px">{""}</FullWidthSkeleton>
      </div>
    </div>
  );
};

export default FuelTrackingSkeleton;
