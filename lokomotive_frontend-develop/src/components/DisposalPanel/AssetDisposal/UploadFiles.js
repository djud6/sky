import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import FileUploadInput from "../../ShareComponents/FileUploadInput";
import CardWidget from "../../ShareComponents/CardWidget";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import LoadingAnimation from "../../ShareComponents/LoadingAnimation";
import "../../../styles/helpers/fileInput.scss";

const UploadFiles = ({
  vin,
  vinImage,
  setVinImage,
  vinImageName,
  setVinImageName,
  mileageImage,
  setMileageImage,
  mileageImageName,
  setMileageImageName,
  vinImagePreview,
  setVinImagePreview,
  mileageImagePreview,
  setMileageImagePreview,
  otherDocs,
  setOtherDocs,
  otherDocsName,
  setOtherDocsName,
}) => {
  const { t } = useTranslation();
  const [fileLoading1, setFileLoading1] = useState(false);
  const [fileLoading2, setFileLoading2] = useState(false);
  const [fileLoading3, setFileLoading3] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  return (
    <React.Fragment>
      <div className="p-sm-12 p-md-12 p-lg-6 p-xl-6 upload-files-input">
        <h5 className="header form-tooltip">
          {t("removalPanel.upload_file_title", { VIN: vin })}
          <Tooltip
            label={"title-tooltip"}
            description={t("removalPanel.upload_file_title_tooltip")}
          />
        </h5>
        <div className="w-100">
          <CardWidget status={vinImage.length !== 0} blueBg>
            <label className="h6">
              {t("removalPanel.upload_vin_image")}
            </label>
            <div className="custom-file input-files-container">
              <FileUploadInput
                images={vinImage}
                setImages={setVinImage}
                imageNames={vinImageName}
                setImageNames={setVinImageName}
                fileLoading={fileLoading1}
                setFileLoading={setFileLoading1}
                maxNumberOfFiles={1}
                setPreviewFile={setVinImagePreview}
              />
            </div>
          </CardWidget>
          <CardWidget status={mileageImage.length !== 0} blueBg>
            <label className="h6">
              {t("removalPanel.upload_mileage_image")}
            </label>
            <div className="custom-file input-files-container">
              <FileUploadInput
                images={mileageImage}
                setImages={setMileageImage}
                imageNames={mileageImageName}
                setImageNames={setMileageImageName}
                fileLoading={fileLoading2}
                setFileLoading={setFileLoading2}
                maxNumberOfFiles={2}
                setPreviewFile={setMileageImagePreview}
              />
            </div>
          </CardWidget>
          <CardWidget status={otherDocs.length !== 0} blueBg>
            <label className="h6 form-tooltip">
              {t("removalPanel.upload_other_doc")}
              <Tooltip
                label={"upload-tooltip"}
                description={t("reportIssuePanel.upload-tooltip")}
              />
            </label>
            <div className="custom-file input-files-container">
              <FileUploadInput
                images={otherDocs}
                setImages={setOtherDocs}
                imageNames={otherDocsName}
                setImageNames={setOtherDocsName}
                fileLoading={fileLoading3}
                setFileLoading={setFileLoading3}
                fileTypes=".doc,.docx,.pdf,image/*,.heic"
                maxNumberOfFiles={20}
              />
            </div>
          </CardWidget>
        </div>
      </div>
      {!isMobile ? (
        <div className="p-sm-12 p-md-12 p-lg-6 p-xl-6">
          {(vinImage.length !== 0 || mileageImage.length !== 0) && (
            <div className="p-d-flex p-flex-column upload-files-preview">
              <label className="h4">{t("general.image_preview")}</label>
              <div className="p-d-flex p-jc-start image-section">
                {(vinImage.length !== 0 || mileageImage.length !== 0) && (vinImagePreview.length === 0 && mileageImagePreview.length === 0) ?
                  <div className="w-100">
                    <LoadingAnimation height={"230px"} />
                  </div>
                  :
                  <React.Fragment>
                    {vinImagePreview[0] ? (
                      <div className="p-mb-5 image-style">
                        <img width="100%" src={vinImagePreview[0]} alt="vin_image_preview" />
                      </div>
                    ) : null}
                    {mileageImagePreview[0] ? (
                      <div className="p-mb-5 image-style">
                        <img width="100%" src={mileageImagePreview[0]} alt="mileage_image_preview" />
                      </div>
                    ) : null}
                    {mileageImagePreview[1] ? (
                      <div className="p-mb-5 image-style">
                        <img width="100%" src={mileageImagePreview[1]} alt="hours_image_preview" />
                      </div>
                    ) : null}
                  </React.Fragment>
                }
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="w-100 p-mx-3">
          {(vinImagePreview.length !== 0 || mileageImagePreview.length !== 0) && (
            <div className="p-d-flex p-flex-column upload-files-preview">
              <label className="h4">{t("general.image_preview")}</label>
              <div className="p-d-flex p-jc-start image-section">
                {vinImagePreview[0] ? (
                  <div className="p-mb-5 image-style">
                    <img width="100%" src={vinImagePreview[0]} alt="vin_image_preview" />
                  </div>
                ) : null}
                {mileageImagePreview[0] ? (
                  <div className="p-mb-5 image-style">
                    <img width="100%" src={mileageImagePreview[0]} alt="mileage_image_preview" />
                  </div>
                ) : null}
                {mileageImagePreview[1] ? (
                  <div className="p-mb-5 image-style">
                    <img width="100%" src={mileageImagePreview[1]} alt="hours_image_preview" />
                  </div>
                ) : null}
              </div>
            </div>
          )}
        </div>
      )}
    </React.Fragment>
  );
};

export default UploadFiles;
