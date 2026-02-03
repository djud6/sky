import React, { useState, useEffect } from "react";
import axios from "axios";
import { useSelector } from "react-redux";
import { getAuthHeader } from "../../helpers/Authorization";
import * as Constants from "../../constants";
import FormDropdown from "../ShareComponents/Forms/FormDropdown";
import CustomInputText from "../ShareComponents/CustomInputText";
import FileUploadInput from "../ShareComponents/FileUploadInput";
import { loadingAlert, successAlert, generalErrorAlert } from "../ShareComponents/CommonAlert";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import "../../styles/dialogStyles.scss";
import CustomTextArea from "../ShareComponents/CustomTextArea";

const UpdateAssetDetail = ({ vehicle, dialogStatus, setDialogStatus, setForceUpdate }) => {
  const { t } = useTranslation();
  const { listBusinessUnits } = useSelector((state) => state.apiCallData);
  const statusOptions = [
    {
      name: t("general.status_active"),
      code: "Active",
    },
    {
      name: t("general.status_inoperative"),
      code: "Inoperative",
    },
    {
      name: t("general.status_disposedOf"),
      code: "Disposed-of",
    },
  ];
  const defaultS = statusOptions.find((option) => option.code === vehicle.status);
  const [selectedStatus, setSelectedStatus] = useState(defaultS);
  const [defaultBusinessUnit, setDefaultBusinessUnit] = useState(null);
  const [selectedBusinessUnit, setSelectedBusinessUnit] = useState(null);
  const [images, setImages] = useState([]);
  const [imageNames, setImageNames] = useState([]);

  const [fileLoading, setFileLoading] = useState(false);

  const [assetInfo, setAssetInfo] = useState({
    license_plate: vehicle.license_plate || "",
    mileage: vehicle.mileage.toString(),
    hours: vehicle.hours.toString(),
    asset_description: vehicle.asset_description,
    custom_fields:vehicle.custom_fields
  });

  useEffect(() => {
    if (vehicle) {
      setAssetInfo({
        license_plate: vehicle.license_plate || "",
        mileage: vehicle.mileage.toString(),
        hours: vehicle.hours.toString(),
        asset_description: vehicle.asset_description,
        custom_fields:vehicle.custom_fields

      });

      const defaultS = statusOptions.find((option) => option.code === vehicle.status);
      setSelectedStatus(defaultS);


      const filteredBusinessUnits = listBusinessUnits.filter((unit) => {
        return unit.name === vehicle.businessUnit;
      });
      let reformatBusinessU = {};
      if (filteredBusinessUnits && filteredBusinessUnits.length > 0) {
        reformatBusinessU = {
          name: filteredBusinessUnits[0].name,
          code: filteredBusinessUnits[0].business_unit_id,
        };
        setDefaultBusinessUnit(reformatBusinessU);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicle]);

  const selectBusinessUnit = (id) => {
    let selected = listBusinessUnits.find((v) => v.business_unit_id === parseInt(id));
    setSelectedBusinessUnit(selected);
  };

  const handleAssetUpdate = () => {
    let assetUpdateData = {
      VIN: vehicle.VIN,
      ...(assetInfo.license_plate && { license_plate: assetInfo.license_plate }),
      ...((vehicle.hours_or_mileage.toLowerCase() === "mileage" ||
        vehicle.hours_or_mileage.toLowerCase() === "both") &&
        assetInfo.mileage && { mileage: assetInfo.mileage }),
      ...((vehicle.hours_or_mileage.toLowerCase() === "hours" ||
        vehicle.hours_or_mileage.toLowerCase() === "both") &&
        assetInfo.hours && { hours: assetInfo.hours }),
      ...(selectedStatus && { status: selectedStatus.code }),
      ...(selectedBusinessUnit && { business_unit: selectedBusinessUnit.business_unit_id }),
      ...(assetInfo.asset_description && { asset_description: assetInfo.asset_description }),
      ...(assetInfo.custom_fields && { custom_fields: assetInfo.custom_fields }),

    };

    let assetImagesData;
    if (images.length !== 0) {
      assetImagesData = new FormData();

      let file_specs = {
        file_info: [],
      };
      for (let i = 0; i < images.length; i++) {
        file_specs.file_info.push({ file_name: images[i].name, purpose: "asset-image" });
      }
      for (let i = 0; i < images.length; i++) {
        assetImagesData.append("files", images[i]);
      }
      assetImagesData.append("file_specs", JSON.stringify(file_specs));
    }

    handleUpdateSubmit(assetUpdateData, assetUpdateData.VIN, assetImagesData);
  };

  const handleUpdateSubmit = (data, imagesData) => {
    loadingAlert();
    axios
      .post(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Update/`,
          data,
          getAuthHeader())
      .then((res) => {
        if (images.length !== 0) {
          axios
            .post(
              `${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Add/Support/Files/${vehicle.VIN}`,
              imagesData,
              getAuthHeader()
            )
            .then((res) => {
              successAlert(t("updateAsset.update_asset"));
              setDialogStatus(false);
              setForceUpdate(Date.now());
            })
            .catch((error) => {
              ConsoleHelper(error);
              generalErrorAlert(error.customErrorMsg);
            });
        } else {
          successAlert(t("updateAsset.update_asset"));
          setDialogStatus(false);
          setForceUpdate(Date.now());
        }
      })
      .catch((error) => {
        ConsoleHelper(error);
        generalErrorAlert(error.customErrorMsg);
      });
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label="Cancel"
          icon="pi pi-times"
          className="p-button-text"
          onClick={() => setDialogStatus(false)}
        />
        <Button
          label="Confirm"
          icon="pi pi-check"
          onClick={handleAssetUpdate}
          disabled={fileLoading}
        />
      </div>
    );
  };

  const selectStatus = (code) => {
    let selected = statusOptions.find((op) => op.code === code);
    setSelectedStatus(selected);
  };

  return (
    <React.Fragment>
      <Dialog
        className="custom-main-dialog"
        header={t("updateAsset.update_asset_title")}
        visible={dialogStatus}
        onHide={() => setDialogStatus(false)}
        style={{ width: "50vw" }}
        breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
        footer={renderFooter()}
      >
        <div className="p-field">
          <label className="h6">{t("fleetPanel.license_plate_label")}</label>
          <CustomInputText
            className="w-100"
            value={assetInfo["license_plate"]}
            onChange={(val) => setAssetInfo({ ...assetInfo, license_plate: val })}
            leftStatus
          />
        </div>
        <div className="p-field">
          <label className="h6">{t("assetRequest.business_unit")}</label>
          <div className="w-100">
            <FormDropdown
              onChange={selectBusinessUnit}
              options={
                listBusinessUnits &&
                listBusinessUnits.map((businessUnit) => ({
                  name: businessUnit.name,
                  code: businessUnit.business_unit_id,
                }))
              }
              defaultValue={defaultBusinessUnit}
              loading={!defaultBusinessUnit}
              disabled={!defaultBusinessUnit}
              dataReady={defaultBusinessUnit}
              plain_dropdown
              leftStatus
              reset={"disabled"}
            />
          </div>
        </div>
        <div className="p-field">
          <label>{t("assetDetailPanel.asset_status")}</label>
          <FormDropdown
            onChange={selectStatus}
            options={statusOptions}
            defaultValue={selectedStatus}
            dataReady={selectedStatus}
            plain_dropdown
            leftStatus
            reset={"disabled"}
          />
        </div>
        {vehicle.hours_or_mileage.toLowerCase() === "mileage" ||
        vehicle.hours_or_mileage.toLowerCase() === "both" ? (
          <div className="p-field">
            <label className="h6">{t("general.mileage")}</label>
            <CustomInputText
              className="w-100"
              value={assetInfo["mileage"]}
              onChange={(val) => setAssetInfo({ ...assetInfo, mileage: val })}
              keyfilter={/^\d*\.?\d*$/}
              leftStatus
            />
          </div>
        ) : null}
        {vehicle.hours_or_mileage.toLowerCase() === "hours" ||
        vehicle.hours_or_mileage.toLowerCase() === "both" ? (
          <div className="p-field">
            <label className="h6">{t("general.hours")}</label>
            <CustomInputText
              className="w-100"
              value={assetInfo["hours"]}
              onChange={(val) => setAssetInfo({ ...assetInfo, hours: val })}
              keyfilter={/^\d*\.?\d*$/}
              leftStatus
            />
          </div>
        ) : null}
            <div className="p-field">
            <label className="h6">{t("general.description")}</label>
            <CustomTextArea
             className="w-100"
             rows={5}
             value={assetInfo["asset_description"]}
             onChange={(val) => setAssetInfo({ ...assetInfo, asset_description: val })}
             leftStatus
            />
            </div>
        <div className="p-field">
          <label className="h6">{t("general.custom_fields")}</label>
          {/*<CustomTextArea*/}
          {/*    className="w-100"*/}
          {/*    rows={5}*/}
          {/*    value={assetInfo.custom_fields.field1.value}*/}
          {/*    onChange={(val) => setAssetInfo({*/}
          {/*      ...assetInfo,*/}
          {/*      custom_fields: {*/}
          {/*        ...assetInfo.custom_fields,*/}
          {/*        field1: {*/}
          {/*          ...assetInfo.custom_fields.field1,*/}
          {/*          value: val,*/}
          {/*        },*/}
          {/*      },*/}
          {/*    })}*/}
          {/*    leftStatus*/}
          {/*/>*/}
        </div>
        <div className="p-field">
          <label>{t("assetDetailPanel.add_asset_images")}</label>
          <div className="custom-file input-files-container">
            <FileUploadInput
              images={images}
              setImages={setImages}
              imageNames={imageNames}
              setImageNames={setImageNames}
              fileLoading={fileLoading}
              setFileLoading={setFileLoading}
              fileTypes="image/*, .heic"
              maxNumberOfFiles={20}
            />
          </div>
        </div>
      </Dialog>
    </React.Fragment>
  );
};

export default UpdateAssetDetail;
