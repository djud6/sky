import React, { useState, useEffect } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { useTranslation } from "react-i18next";
import { getAuthHeader } from "../../../helpers/Authorization";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import CustomInputText from "../../ShareComponents/CustomInputText";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button2.scss";
import "../../../styles/dialogStyles.scss";

const OtherEquipmentType = ({
  otherModel,
  setOtherModel,
  otherFuel,
  setOtherFuel,
  otherEngine,
  setOtherEngine,
}) => {
  const { t } = useTranslation();
  return (
    <React.Fragment>
      <div className="p-field">
        <label className="h6">{t("assetRequest.add_model_number")}</label>
        <CustomInputText
          type="text"
          value={otherModel}
          onChange={setOtherModel}
          placeholder={t("general.required")}
          leftStatus
        />
      </div>
      <div className="p-field">
        <label className="h6">{t("assetRequest.fuel_type")}</label>
        <CustomInputText
          type="text"
          value={otherFuel}
          onChange={setOtherFuel}
          placeholder={t("general.optional")}
          leftStatus
        />
      </div>
      <div className="p-field">
        <label className="h6">{t("assetRequest.engine")}</label>
        <CustomInputText
          type="text"
          value={otherEngine}
          onChange={setOtherEngine}
          placeholder={t("general.optional")}
          leftStatus
        />
      </div>
    </React.Fragment>
  );
};

const AddNewEquipType = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [onDialogOpen, setOnDialogOpen] = useState(false);
  const [assetTypes, setAssetTypes] = useState(null);
  const [selectedAssetType, setSelectedAssetType] = useState(null);
  const [manufacturers, setManufacturers] = useState(null);
  const [selectedManufacturer, setSelectedManufacturer] = useState(null);
  const [otherAssetType, setOtherAssetType] = useState("");
  const [otherManufacturer, setOtherManufacturer] = useState("");
  const [otherModel, setOtherModel] = useState("");
  const [otherFuel, setOtherFuel] = useState("");
  const [otherEngine, setOtherEngine] = useState("");
  const [assetDataReady, setAssetDataReady] = useState(false);
  const [manuDataReady, setManuDataReady] = useState(false);
  const [formFilled, setFormFilled] = useState(false);

  useEffect(() => {
    if (onDialogOpen && !assetTypes) {
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/List`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          const assetTypesResponse = [{ id: 99999, name: "Other" }].concat(response.data);
          setAssetTypes(assetTypesResponse);
          setAssetDataReady(true);
        })
        .catch((err) => {
          ConsoleHelper(err);
        });
      return () => {
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [onDialogOpen]);

  useEffect(() => {
    if (selectedAssetType && selectedAssetType.name !== "Other") {
      setManuDataReady(false);
      setManufacturers(null);
      setSelectedManufacturer(null);
      const cancelTokenSource = axios.CancelToken.source();
      let assetId = selectedAssetType.id;
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/${assetId}/Manufacturers`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          const manufacturersResponse = [{ id: 99999, name: "Other" }].concat(response.data);
          setManufacturers(manufacturersResponse);
          setManuDataReady(true);
        })
        .catch((err) => {
          ConsoleHelper(err);
        });
      return () => {
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
  }, [selectedAssetType]);

  useEffect(() => {
    if (selectedAssetType && otherModel) {
      if (selectedAssetType.name === "Other") {
        if (!otherAssetType || !otherManufacturer) setFormFilled(false);
        else setFormFilled(true);
      } else if (!selectedManufacturer) {
        setFormFilled(false);
      } else if (selectedManufacturer && selectedManufacturer.name === "Other") {
        if (!otherManufacturer) setFormFilled(false);
        else setFormFilled(true);
      } else {
        setFormFilled(true);
      }
    } else {
      setFormFilled(false);
    }
  }, [selectedAssetType, otherAssetType, selectedManufacturer, otherManufacturer, otherModel]);

  const selectAssetType = (id) => {
    let selected = assetTypes.find((v) => v.id === parseInt(id));
    setSelectedAssetType(selected);
  };

  const selectManufacturer = (id) => {
    let selected = manufacturers.find((v) => v.id === parseInt(id));
    setSelectedManufacturer(selected);
  };

  const handleSubmitNewType = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let newEquipmentType = {
      ...(selectedAssetType.name !== "Other"
        ? { asset_type: selectedAssetType.name }
        : { asset_type: otherAssetType }),
      ...(selectedManufacturer && selectedManufacturer.name !== "Other"
        ? { manufacturer: selectedManufacturer.name }
        : { manufacturer: otherManufacturer }),
      model_number: otherModel,
      ...(otherEngine && { engine: otherEngine }),
      ...(otherFuel && { fuel_name: otherFuel }),
    };
    handleSubmit(newEquipmentType);
  };

  const handleSubmit = (data) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/EquipmentType/Add`, data, getAuthHeader())
      .then((res) => {
        successAlert();
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
        setOnDialogOpen(false);
      })
      .catch((error) => {
        ConsoleHelper(error);
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label={t("general.cancel")}
          icon="pi pi-times"
          className="p-button-text"
          onClick={() => setOnDialogOpen(false)}
        />
        <Button
          label={t("general.submit")}
          icon="pi pi-check"
          disabled={!formFilled}
          onClick={handleSubmitNewType}
        />
      </div>
    );
  };

  return (
    <div>
      <div className="btn-2">
        <Button
          label={t("assetRequest.add_equipment_button")}
          icon="pi pi-plus-circle"
          onClick={() => setOnDialogOpen(true)}
        />
      </div>
      <Dialog
        className="custom-main-dialog"
        header={t("assetRequest.dialog_title")}
        visible={onDialogOpen}
        footer={renderFooter()}
        style={{ width: "50vw" }}
        breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
        onHide={() => setOnDialogOpen(false)}
      >
        <div className="p-field">
          <label className="h6">{t("assetRequest.asset_label")}</label>
          <FormDropdown
            onChange={selectAssetType}
            options={
              assetTypes &&
              assetTypes.map((type) => ({
                name: type.name,
                code: type.id,
              }))
            }
            loading={!assetDataReady}
            disabled={!assetDataReady}
            dataReady={assetDataReady}
            plain_dropdown
            leftStatus
          />
        </div>
        {selectedAssetType && selectedAssetType.name === "Other" ? (
          <div className="p-field">
            <label className="h6">{t("assetRequest.add_asset_type")}</label>
            <CustomInputText
              type="text"
              value={otherAssetType}
              onChange={setOtherAssetType}
              placeholder={t("general.required")}
              leftStatus
            />
          </div>
        ) : null}
        {selectedAssetType && selectedAssetType.name !== "Other" ? (
          <div className="p-field">
            <label className="h6">{t("assetRequest.manufacturer_label")}</label>
            <FormDropdown
              onChange={selectManufacturer}
              options={
                manufacturers &&
                manufacturers.map((manufacturer) => ({
                  name: manufacturer.name,
                  code: manufacturer.id,
                }))
              }
              loading={!manuDataReady && selectedAssetType}
              disabled={!manuDataReady || !selectedAssetType}
              dataReady={manuDataReady}
              plain_dropdown
              leftStatus
              reset={manuDataReady && "disabled"}
            />
          </div>
        ) : null}
        {(selectedAssetType && selectedAssetType.name === "Other") ||
        (selectedManufacturer && selectedManufacturer.name === "Other") ? (
          <div className="p-field">
            <label className="h6">{t("assetRequest.add_manufacturer")}</label>
            <CustomInputText
              type="text"
              value={otherManufacturer}
              onChange={setOtherManufacturer}
              placeholder={t("general.required")}
              leftStatus
            />
          </div>
        ) : null}
        <OtherEquipmentType
          otherModel={otherModel}
          setOtherModel={setOtherModel}
          otherFuel={otherFuel}
          setOtherFuel={setOtherFuel}
          otherEngine={otherEngine}
          setOtherEngine={setOtherEngine}
        />
      </Dialog>
    </div>
  );
};

export default AddNewEquipType;
