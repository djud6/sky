import { Skeleton } from "primereact/skeleton";
import "../../../styles/customSkeleton.scss";

const PageSkeleton = () => {
  return (
    <div>
      <div className="media panel-header">
        <Skeleton shape="circle" size="5rem">
          {""}
        </Skeleton>
        <div className="heading-div mt-2">
          <div className="media-body mx-2">
            <Skeleton height="2rem" width="25rem" className="p-mb-2" borderRadius="16px">
              {""}
            </Skeleton>
            <Skeleton width="10rem" borderRadius="16px" className="p-mb-2">
              {""}
            </Skeleton>
          </div>
        </div>
      </div>
      <div className="p-py-5">
        <Skeleton width="100%" height="180px">
          {""}
        </Skeleton>
      </div>
      <div>
        <Skeleton className="p-mb-2" width="100%" borderRadius="16px">
          {""}
        </Skeleton>
        <Skeleton className="p-mb-2" width="70%" borderRadius="16px">
          {""}
        </Skeleton>
      </div>
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

export default PageSkeleton;
