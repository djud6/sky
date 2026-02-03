import React from "react";
import "./CustomSkeleton.css";

const CustomSkeleton = ({ width, height, borderRadius, className }) => {
  const style = {
    width: width || "100%",
    height: height || "1rem",
    borderRadius: borderRadius || "4px",
    backgroundColor: "#e0e0e0",
    animation: "pulse 1.5s infinite",
    ...className
  };
  return <div style={style} />;
};

export default CustomSkeleton;