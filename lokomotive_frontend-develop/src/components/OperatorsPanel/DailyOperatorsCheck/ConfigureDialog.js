import React, { useState, useEffect } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { Dialog } from "primereact/dialog";
import { Button } from "primereact/button";
import { InputSwitch } from "primereact/inputswitch";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import GeneralRadio from "../../ShareComponents/GeneralRadio";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/OperatorsPanel/DailyOperatorsCheck.scss";

const ConfigureDialog = ({ checksDialog, setchecksDialog }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [configureMode, setConfigureMode] = useState(null);
  const [assetTypes, setAssetTypes] = useState(null);
  const [checksList, setChecksList] = useState(null);
  const [existChecksList, setExistChecksList] = useState(null);
  const [selectedAssetType, setSelectedAssetType] = useState(null);
  const [forceReset, setForceReset] = useState(Date.now());
  const subCheckTitles = ["lights", "fluids", "leaks", "safety_equipment"];
  const non_relative_data = [
    "id",
    "asset_type_name",
    "date_created",
    "date_updated",
    "created_by",
    "modified_by",
  ];

  useEffect(() => {
    if (checksDialog) {
      setConfigureMode(null);
      setAssetTypes(null);
      setSelectedAssetType(null);
      setChecksList(null);
      setExistChecksList(null);
    }
  }, [checksDialog]);

  useEffect(() => {
    if (configureMode !== null) {
      setForceReset(Date.now());
      setAssetTypes(null);
      setChecksList(null);
      setSelectedAssetType(null);
      setExistChecksList(null);

      const cancelTokenSource = axios.CancelToken.source();
      let url;
      if (configureMode) {
        url = `/api/v1/AssetType/List/Without/Checks`;
      } else {
        url = `/api/v1/AssetType/List/With/Checks`;
      }

      let getAssetTypes = axios.get(`${Constants.ENDPOINT_PREFIX}${url}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });

      let getChecksList = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetType/Checks/List`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });

      axios
        .all([getAssetTypes, getChecksList])
        .then(
          axios.spread((...responses) => {
            setAssetTypes(responses[0].data);
            setExistChecksList(responses[1].data);
          })
        )
        .catch((error) => {
          ConsoleHelper(error);
          setAssetTypes([]);
        });

      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
  }, [configureMode]);

  useEffect(() => {
    if (selectedAssetType) {
      if (configureMode) {
        let temp = existChecksList[0];
        Object.keys(temp).forEach((key) => {
          temp[key] = false;
        });
        setChecksList(temp);
      } else {
        const temp = existChecksList.filter((obj) => {
          return obj["asset_type_name"].toLowerCase() === selectedAssetType.name.toLowerCase();
        });
        setChecksList(temp[0]);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedAssetType]);

  const selectAssetType = (id) => {
    let selected = assetTypes.find((v) => v.id === parseInt(id));
    setSelectedAssetType(selected);
  };

  const handleAssetChecksUpdate = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });

    let data = checksList;
    let api_url;

    if (configureMode) {
      non_relative_data.forEach((item) => delete data[item]);
      data.asset_type_name = selectedAssetType.name;
      api_url = "/api/v1/AssetType/Checks/Add";

      handleSubmit(data, api_url);
    } else {
      data.asset_type_checks_id = checksList.id;
      non_relative_data.forEach((item) => delete data[item]);
      api_url = "/api/v1/AssetType/Checks/Update";

      handleSubmit(data, api_url);
    }
  };

  const handleSubmit = (data, url) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}${url}`, data, getAuthHeader())
      .then((res) => {
        successAlert("msg", t("configureChecks.success_add_msg"));
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
        resetForm();
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  const resetForm = () => {
    setConfigureMode(null);
    setForceReset(Date.now());
    setAssetTypes(null);
    setChecksList(null);
    setSelectedAssetType(null);
    setExistChecksList(null);
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label="Cancel"
          icon="pi pi-times"
          className="p-button-text"
          onClick={() => setchecksDialog(false)}
        />
        <Button
          label="Confirm"
          icon="pi pi-check"
          onClick={handleAssetChecksUpdate}
          disabled={configureMode === null || !selectedAssetType}
        />
      </div>
    );
  };

  return (
    <Dialog
      className="custom-main-dialog configure-checks-dialog"
      header={t("configureChecks.dialog_title")}
      visible={checksDialog}
      onHide={() => setchecksDialog(false)}
      style={{ width: "60vw" }}
      breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
      footer={renderFooter()}
    >
      
      <div className="p-field">
        <GeneralRadio
          classnames="font-weight-bold"
          value={configureMode}
          onChange={setConfigureMode}
          name={"configurechecks"}
          labels={[
            t("configureChecks.choose_asset_type_op"),
            t("configureChecks.add_new_one"),
            t("configureChecks.update_existing_one"),
          ]}
        />
        </div>
      <div className="p-field">
        <label className="font-weight-bold">{t("configureChecks.select_asset_type")}</label>
        <FormDropdown
          onChange={selectAssetType}
          options={
            assetTypes &&
            assetTypes.map((type) => ({
              name: type.name,
              code: type.id,
            }))
          }
          loading={configureMode !== null && !assetTypes}
          disabled={configureMode === null || !assetTypes}
          dataReady={assetTypes}
          plain_dropdown
          leftStatus
          reset={forceReset}
        />
      </div>
      <hr />
      {selectedAssetType && configureMode !== null && checksList && (
        <div className="check-items-form">
          <label className="font-weight-bold">{t("configureChecks.configure_checks")}</label>
          <div className="check-items-list">
            {Object.keys(checksList).map((name, i) => {
              return (
                !non_relative_data.includes(name) &&
                !(subCheckTitles.indexOf(name) > -1) && (
                  <div key={i} className="check-item p-my-1">
                    <label className="h6 form-tooltip">
                      {t(`configureChecks.${name}`)}
                      <Tooltip
                        label={name}
                        description={t(`lookupDailyCheckPanelIndex.tooltip_${name}`)}
                      />
                    </label>
                    <div className="switch-container">
                      <InputSwitch
                        checked={checksList[name]}
                        onChange={(e) => setChecksList({ ...checksList, [name]: e.value })}
                      />
                    </div>
                  </div>
                )
              );
            })}
          </div>
          <hr />
        </div>
      )}
    </Dialog>
  );
};

export default ConfigureDialog;
