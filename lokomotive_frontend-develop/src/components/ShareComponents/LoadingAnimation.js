import React from "react";
import "../../styles/ShareComponents/loadingAnimation.scss";

const LoadingAnimation = ({ height = "350px" }) => {
  return (
    <div className="table-loader-container" style={{height: height}}>
      <div className="table-preloader">
        <div className="loading-line">
          <span className="line line-1" />
          <span className="line line-2" />
          <span className="line line-3" />
          <span className="line line-4" />
          <span className="line line-5" />
          <span className="line line-6" />
          <span className="line line-7" />
          <span className="line line-8" />
          <span className="line line-9" />
        </div>
        <div className="loading-text">Loading</div>
      </div>
    </div>
  )
}

export default LoadingAnimation;