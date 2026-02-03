import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import { generalErrorAlert } from "../../ShareComponents/CommonAlert";
import AssetDetailsCardMobile from "../../AssetDetailPanel/AssetDetailsCardMobile";
import AssetDetailsMoreMobile from "../../AssetDetailPanel/AssetDetailsMoreMobile";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button4.scss";

const AssetDetailsMobile = ({
  isSupervisor,
  isOperator,
  asset,
  setSelectedAsset,
  setMobileDetails,
  forceUpdate,
  setForceUpdate,
}) => {
  const { t } = useTranslation();
  const [assetImgs, setAssetImgs] = useState([]);
  const [moreDetails, setMoreDetails] = useState(false);
  const [detailsSection, setDetailsSection] = useState(null);

  useEffect(() => {
    setAssetImgs([]);
    const cancelTokenSource = axios.CancelToken.source();

    let assetImages = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Get/Files/${asset.VIN}`,
      {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      }
    );

    axios
      .all([assetImages])
      .then(
        axios.spread((...responses) => {
          const assetFiles = !!responses[0] ? responses[0].data : [];
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
  }, [asset, forceUpdate]);

  const onBack = () => {
    setMobileDetails(false);
    setSelectedAsset(null);
  };

  return (
    <div>
      {moreDetails ? (
        <AssetDetailsMoreMobile
          asset={asset}
          isOperator={isOperator}
          detailsSection={detailsSection}
          setMoreDetails={setMoreDetails}
          setDetailsSection={setDetailsSection}
        />
      ) : (
        <div className="p-mx-3">
          <div className="no-style-btn p-my-3">
            <Button
              label={t("general.back")}
              className="p-button-link"
              icon="pi pi-chevron-left"
              onClick={() => onBack()}
            />
          </div>
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
  );
};

export default AssetDetailsMobile;
