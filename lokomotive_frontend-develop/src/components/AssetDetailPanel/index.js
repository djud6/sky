import React, { useState, useEffect } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";
import { useMediaQuery } from "react-responsive";
import { getAuthHeader, getRolePermissions } from "../../helpers/Authorization";
import * as Constants from "../../constants";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import AssetDetailsCard from "./AssetDetailsCard";
import AssetDetailsCardMobile from "./AssetDetailsCardMobile";
import AssetDetailsMore from "./AssetDetailsMore";
import AssetDetailsMoreMobile from "./AssetDetailsMoreMobile";
import { generalErrorAlert } from "../ShareComponents/CommonAlert";
import "../../styles/AssetDetailsPanel/AssetDetails.scss";

const AssetDetailPanel = () => {
  const { vin } = useParams();
  // const { unit_number} = useParams()
  const [asset, setAsset] = useState(null);
  const [assetImgs, setAssetImgs] = useState([]);
  const [isOperator, setIsOperator] = useState(false);
  const [isSupervisor, setIsSupervisor] = useState(false);
  const [moreDetails, setMoreDetails] = useState(false);
  const [detailsSection, setDetailsSection] = useState(null);
  const [forceUpdate, setForceUpdate] = useState(Date.now());
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    setAsset(null);
    setAssetImgs([]);
    setMoreDetails(false);
    setDetailsSection(null);
    const cancelTokenSource = axios.CancelToken.source();
    const rolePermissions = getRolePermissions();

    if (rolePermissions.role.toLowerCase() === "operator") setIsOperator(true);
    else setIsOperator(false);

    if (rolePermissions.role.toLowerCase() === "supervisor") setIsSupervisor(true);
    else setIsSupervisor(false);

    let assetDetails = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/AssetsByLast/VIN/UnitNumber/${vin}`,
      {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      }
    );
    let assetImages = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Get/Files/${vin}`, {
      ...getAuthHeader(),
      cancelToken: cancelTokenSource.token,
    });

    axios
      .all([assetDetails, assetImages])
      .then(
        axios.spread((...responses) => {
          const details = !!responses[0] ? responses[0].data : null;
          setAsset(details[0]);

          const assetFiles = !!responses[1] ? responses[1].data : [];
          const assetImgs = assetFiles.filter((file) => file.file_purpose === "asset-image");
          assetImgs.map((image) => {
            image.itemImageSrc = image.file_url;
            image.thumbnailImageSrc = image.file_url;
            image.alt = image.file_name;
            image.title = image.file_name;
            return image;
          });
          setAssetImgs(assetImgs);
        })
      )
      .catch((err) => {
        generalErrorAlert(err.customErrorMsg);
        ConsoleHelper(err);
      });

    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [vin, forceUpdate]);

  return (
    <div className="asset-details-container">
      {isMobile ? (
        <div className="mobile-container">
          {moreDetails ? (
            <AssetDetailsMoreMobile
              asset={asset}
              detailsSection={detailsSection}
              setMoreDetails={setMoreDetails}
              setDetailsSection={setDetailsSection}
              setForceUpdate={setForceUpdate}
            />
          ) : (
            <div className="details-card p-pt-5 p-px-2">
              <AssetDetailsCardMobile
                isSupervisor={isSupervisor}
                isOperator={isOperator}
                asset={asset}
                assetImgs={assetImgs}
                setMoreDetails={setMoreDetails}
                setDetailsSection={setDetailsSection}
                setForceUpdate={setForceUpdate}
              />
            </div>
          )}
        </div>
      ) : (
        <div className="desktop-container p-d-flex p-jc-around p-flex-wrap p-mt-5">
          <div className="left-container">
            <AssetDetailsCard
              vin={vin}
              asset={asset}
              assetImgs={assetImgs}
              isOperator={isOperator}
              isSupervisor={isSupervisor}
              setForceUpdate={setForceUpdate}
            />
          </div>
          <div className="right-container">
            <AssetDetailsMore
              asset={asset}
              isOperator={isOperator}
              setForceUpdate={setForceUpdate}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default AssetDetailPanel;
