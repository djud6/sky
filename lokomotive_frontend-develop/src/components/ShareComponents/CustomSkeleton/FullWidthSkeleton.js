import React from "react";
import { useTranslation } from "react-i18next";
import "../../../styles/ShareComponents/FullWidthSkeleton/FullWidthSkeleton.scss";

const FullWidthSkeleton = ({ width = "100%", height, error }) => {
  const { t } = useTranslation();
  return (
    <div className="p-2 w-100 h-100">
      <div
        style={{ height: height, width: width }}
        className={`p-d-flex p-jc-around skeleton-outer-container ${error ? "error-container" : ""}`}
      >
        <div className="animated-skeleton-container d-flex flex-column justify-content-center align-items-center p-5">
          <div className={`mx-3 mb-2 ${error ? "fleetguru-error" : "fleetguru-animated"}`} />
          <div className="mx-3 text-container d-flex flex-column">
            <div className={`text-center ${error ? "error-text" : "placeholder-text"}`}>
              {error
                ? t("general.unexpected_error").toUpperCase()
                : t("general.loading").toUpperCase()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FullWidthSkeleton;
