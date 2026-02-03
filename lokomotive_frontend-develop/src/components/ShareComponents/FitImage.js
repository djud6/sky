import React from "react";

/**
 * A responsive and auto fit image component, also avoid 0 height/width issue
 *
 * @param {string} mode fit pattern, either fit or fill
 * @param {string} src image url
 */

const FitImage = ({ mode = "fit", src, height = "100%", width = "100%", style, ...props }) => {
  let modes = {
    fill: "cover",
    fit: "contain",
  };
  let size = modes[mode] || "contain";

  let defaultsStyle = {
    height: height,
    width: width,
    backgroundColor: "gray",
    backgroundImage: `url("${src}")`,
    backgroundSize: size,
    backgroundPosition: "center center",
    backgroundRepeat: "no-repeat",
    borderRadius:"5px"
  };

  return <div {...props} style={{ ...defaultsStyle, ...style }} />;
};

export default FitImage;
