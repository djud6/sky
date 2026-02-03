import React from "react";
import { useTranslation } from "react-i18next";
import * as Constants from "../../constants";
import swal from "sweetalert";
import heic2any from "heic2any";

/**
 * File Upload Input Component
 *
 * @param {Array} images array of files
 * @param {Function} setImages func to set array of files
 * @param {Array} imageNames array of file names
 * @param {Function} setImageNames func to set array of file names
 * @param {String} fileTypes (optional, default = 'image/*') file type specifier
 * .jpg, .pdf, or .doc OR audio/*, video/*, image/*, example: fileTypes={".pdf,video/*,image/*"}
 * @param {Integer} maxNumberOfFiles (optional, default = 1) maximum number of files
 * @param {Integer} maxSize (optional, default = Constants) maximum size for file (in bytes)
 */

const FileUploadInput = ({
  images,
  setImages,
  imageNames,
  setImageNames,
  fileLoading,
  setFileLoading,
  fileTypes = "image/*, .heic",
  maxNumberOfFiles = 1,
  maxSize = Constants.MAX_FILE_SIZE,
  setPreviewFile,
  required = false,
}) => {
  const { t } = useTranslation();

  const numberOfFilesError = (maxNumberOfFiles, numberOfFiles) =>
    swal({
      title: t("general.error"),
      text: `Max number of files is ${maxNumberOfFiles}, you have ${numberOfFiles}`,
      icon: "error",
      buttons: { cancel: t("general.cancel") },
    });

  const sizeOfFilesError = (maxSize, currentMax) =>
    swal({
      title: t("general.error"),
      text: t("fileUploadInput.size_error_text", {
        maxSize: maxSize / 1024 / 1024,
        currentMax: (currentMax / 1024 / 1024).toFixed(2),
      }),
      icon: "error",
      buttons: { cancel: t("general.cancel") },
    });

  const checkFileSizes = (fileArray) => {
    let maxFileSize = 0;
    for (let i = 0; i < fileArray.length; i++) {
      if (fileArray[i].size > maxSize) maxFileSize = fileArray[i].size;
    }
    return maxFileSize;
  };

  const ImageUploadHandler = (event) => {
    let photoNameArray = [];
    setImages([]);
    setImageNames([]);

    const biggestFileSize = checkFileSizes(event.target.files);
    if (event.target.files.length > maxNumberOfFiles) {
      numberOfFilesError(maxNumberOfFiles, event.target.files.length);
    } else if (biggestFileSize > 0) {
      sizeOfFilesError(maxSize, biggestFileSize);
    } else {
      if (setPreviewFile) setPreviewFile([]);

      Object.keys(event.target.files).forEach((key) => {
        photoNameArray.push(String(event.target.files[key].name));

        if (event.target.files[key].name.toLowerCase().includes(".heic")) {
          if (setFileLoading) setFileLoading(true);
          heic2any({
            blob: event.target.files[key],
            toType: "image/jpeg",
            quality: 1,
          }).then(function (heicToJpgResult) {
            var file = new File(
              [heicToJpgResult],
              event.target.files[key].name.toLowerCase().replace(".heic", ".jpeg"),
              { type: "image/jpeg", lastModified: Date.now() }
            );
            setImages((preImgs) => [...preImgs, file]);

            if (setPreviewFile) {
              var reader = new FileReader();
              reader.readAsDataURL(heicToJpgResult);
              reader.onload = function () {
                var base64data = reader.result;
                setPreviewFile((preFiles) => [...preFiles, base64data]);
              };
            }
            if (Object.keys(event.target.files).length - 1 === parseInt(key)) {
              if (setFileLoading) setFileLoading(false);
            }
          });
        } else {
          setImages((preImgs) => [...preImgs, event.target.files[key]]);
          if (Object.keys(event.target.files).length - 1 === parseInt(key)) {
            if (setFileLoading) setFileLoading(false);
          }
          if (setPreviewFile) {
            const reader = new FileReader();
            reader.readAsDataURL(event.target.files[key]);
            reader.addEventListener("load", () => {
              const fileRead = reader.result;
              setPreviewFile((preFiles) => [...preFiles, fileRead]);
            });
          }
        }
      });
      setImageNames(photoNameArray.join(", "));
    }
  };

  return (
    <React.Fragment>
      <input
        name="file"
        type="file"
        className="custom-file-input"
        accept={fileTypes}
        onChange={ImageUploadHandler}
        multiple={maxNumberOfFiles > 1}
        required={required}
      />
      <label className="custom-file-label" htmlFor="customFile">
        {fileLoading ? (
          <div>
            <i className="pi pi-spin pi-spinner p-mr-2" />
            Converting File(s)...
          </div>
        ) : images.length === 0 ? (
          t("fileUploadInput.file_choose")
        ) : (
          imageNames
        )}
      </label>
    </React.Fragment>
  );
};

export default FileUploadInput;
