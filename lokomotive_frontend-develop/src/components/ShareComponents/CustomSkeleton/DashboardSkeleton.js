import React from "react";
import { Skeleton } from "primereact/skeleton";

const DashboardSkeleton = () => {
  return (
    <div>
      <div className="p-pt-5 p-d-flex p-jc-around">
        <Skeleton width="30%" height="300px">
          {""}
        </Skeleton>
        <Skeleton width="30%" height="300px">
          {""}
        </Skeleton>
        <Skeleton width="30%" height="300px">
          {""}
        </Skeleton>
      </div>
      <div className="p-pt-5 p-d-flex p-jc-around">
        <Skeleton width="97%" height="400px">
          {""}
        </Skeleton>
      </div>
      <div className="p-pt-5 p-d-flex p-jc-around">
        <Skeleton width="97%" height="400px">
          {""}
        </Skeleton>
      </div>
    </div>
  );
};

export default DashboardSkeleton;
