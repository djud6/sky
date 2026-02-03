import React, { useState, useEffect } from "react";
import axios from "axios";
import swal from "sweetalert";
import * as Constants from "../../../constants";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import Table from "../../ShareComponents/Table/Table";
import { Button } from "primereact/button";
import { RadioButton } from "primereact/radiobutton";
import { getAuthHeader } from "../../../helpers/Authorization";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import AssetTable from "./AssetTable";
import "../../../styles/helpers/button2.scss";
import "../../../styles/helpers/button5.scss";
import "../../../styles/helpers/radiobutton.scss";

const LinkedAssets = ({ asset, setForceUpdate }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [dataReady, setDataReady] = useState(false);
  const [children, setChildren] = useState([]);
  const [onAddAsset, setOnAddAsset] = useState(false);
  const [selectedRelation, setSelectedRelation] = useState(null);
  const [selectedAssets, setSelectedAssets] = useState([]);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (!dataReady) {
      setChildren([]);
      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Get/Children/${asset.VIN}`, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((response) => {
          let relations = response.data;
          relations.map((data) => {
            data.relation = t("motherChildAsset.child");
            return data;
          });
          if (asset.parent) {
            relations.unshift({ VIN: asset.parent, relation: t("motherChildAsset.parent") });
          }
          setChildren(relations);
          setDataReady(true);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    // eslint-disable-next-line
  }, [asset.VIN, dataReady]);

  const resetForm = () => {
    if (selectedRelation === t("motherChildAsset.parent")) {
      asset.parent = selectedAssets[0]["VIN"];
    }
    setDataReady(false);
    setForceUpdate(Date.now());
    setOnAddAsset(false);
    setSelectedRelation(null);
    setSelectedAssets([]);
  };

  const resetTable = (selectedAsset) => {
    if (selectedAsset.relation === t("motherChildAsset.parent")) {
      asset.parent = null;
    }
    setDataReady(false);
  };

  const handleLinkAssets = () => {
    let data;
    let endpoint;
    if (selectedRelation === t("motherChildAsset.parent")) {
      endpoint = "/api/v1/Assets/Set/Parent";
      data = {
        VIN: asset.VIN,
        parent_VIN: selectedAssets[0]["VIN"],
      };
      handleSubmit(data, endpoint);
    } else if (selectedRelation === t("motherChildAsset.child")) {
      endpoint = "/api/v1/Assets/Add/Children";
      const children = selectedAssets.map((asset) => asset.VIN);
      data = {
        parent_VIN: asset.VIN,
        child_VINs: children,
      };
      handleSubmit(data, endpoint);
    }
  };

  const handleSubmit = (data, endpoint) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}${endpoint}`, data, getAuthHeader())
      .then((res) => {
        successAlert("msg", t("motherChildAsset.link_success_msg"));
        resetForm();
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        ConsoleHelper(error);
      });
  };

  const handleDeleteClick = (selectedAsset) => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "warning_alert" });
    warningAlert(selectedAsset);
  };

  const handleDelete = (selectedAsset) => {
    let data;
    let endpoint;
    if (selectedAsset.relation === t("motherChildAsset.parent")) {
      endpoint = "/api/v1/Assets/Remove/Parent";
      data = {
        VIN: asset.VIN,
      };
      handleDeleteSubmit(selectedAsset, data, endpoint);
      setForceUpdate(Date.now());
    } else if (selectedAsset.relation === t("motherChildAsset.child")) {
      endpoint = "/api/v1/Assets/Remove/Children";
      data = {
        child_VINs: [selectedAsset.VIN],
      };
      handleDeleteSubmit(selectedAsset, data, endpoint);
      setForceUpdate(Date.now());
    }
  };

  const handleDeleteSubmit = (selectedAsset, data, endpoint) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}${endpoint}`, data, getAuthHeader())
      .then((res) => {
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
        successAlert("msg", t("motherChildAsset.delete_success_msg"));
        resetTable(selectedAsset);
      })
      .catch((error) => {
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        generalErrorAlert(error.customErrorMsg);
        ConsoleHelper(error);
      });
  };

  const warningAlert = (selectedAsset) => {
    return swal({
      title: t("general.warning"),
      text: t("motherChildAsset.delete_warning_msg"),
      icon: "warning",
      buttons: {
        return: t("general.continue"),
        cancel: t("general.cancel"),
      },
    }).then((value) => {
      if (value === "return") {
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
        handleDelete(selectedAsset);
      }
    });
  };

  let tableHeaders = [
    {
      header: t("general.vin"),
      colFilter: { field: "VIN" },
    },
    {
      header: t("motherChildAsset.relation"),
      colFilter: { field: "relation", filterOptions: { filterAs: "dropdown" } },
    },
  ];

  let tableData = null;

  if (!!children) {
    tableData = children.map((child) => {
      return {
        id: child.VIN,
        dataPoint: child,
        cells: [
          child.VIN,
          <div className="w-100 p-d-flex p-ai-center p-jc-center">
            <div className="p-mr-3">{child.relation}</div>
            <div key={asset.VIN} className="p-d-flex">
              <Button
                icon="pi pi-lock-open"
                className="p-button-rounded p-button-warning"
                onClick={() => handleDeleteClick(child)}
              />
            </div>
          </div>,
        ],
      };
    });
  }

  return (
    <div className={`linked-asset-container ${!isMobile ? "p-mt-5" : "p-mt-3"}`}>
      <div className="p-mb-5">
        <div className="section-table">
          {!onAddAsset ? (
            <React.Fragment>
              <div className="btn-1 p-mr-4 p-my-3 p-d-flex p-jc-end">
                <Button
                  label={t("motherChildAsset.add_more")}
                  icon="pi pi-plus"
                  onClick={() => setOnAddAsset(true)}
                />
              </div>
              <div className="darkTable">
                <Table
                  tableHeaders={tableHeaders}
                  tableData={tableData}
                  dataReady={dataReady}
                  globalSearch={false}
                  rows={5}
                />
              </div>
            </React.Fragment>
          ) : (
            <div className="add-asset">
              <div className="close-btn p-d-flex p-jc-between">
                <h5>Add Parent/Child Asset</h5>
                <Button icon="pi pi-times" onClick={() => setOnAddAsset(false)} />
              </div>
              <div className="add-assets-form p-mt-3">
                <div className="add-assets-q p-d-flex p-flex-wrap p-ai-center">
                  <div className="label-container">
                    <label className="h5">Linked Asset Relation</label>
                  </div>
                  <div className="p-d-flex input-container">
                    <div className="darkRadio">
                      {!asset.parent && (
                        <div className="p-field-radiobutton p-mr-3 p-mb-0">
                          <RadioButton
                            inputId="op_parent"
                            name="relation"
                            value={t("motherChildAsset.parent")}
                            onChange={(e) => setSelectedRelation(e.value)}
                            checked={selectedRelation === t("motherChildAsset.parent")}
                          />
                          <label className="p-m-0 p-m-2" htmlFor="op_parent">
                            {t("motherChildAsset.parent")}
                          </label>
                        </div>
                      )}
                    </div>
                    <div className="darkRadio">
                      <div className="p-field-radiobutton p-mr-3 p-mb-0">
                        <RadioButton
                          inputId="op_child"
                          name="relation"
                          value={t("motherChildAsset.child")}
                          onChange={(e) => setSelectedRelation(e.value)}
                          checked={selectedRelation === t("motherChildAsset.child")}
                        />
                        <label className="p-m-0 p-m-2" htmlFor="op_child">
                          {t("motherChildAsset.child")}
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="add-assets-q p-d-flex p-flex-wrap p-mt-3">
                  <div className="label-container">
                    <label className="h5 p-mt-2">Search Assets</label>
                  </div>
                  <AssetTable
                    selectedAssets={selectedAssets}
                    setSelectedAssets={setSelectedAssets}
                    relation={selectedRelation}
                  />
                </div>
                <div className="btn-5 p-mt-5 p-mb-4 p-d-flex p-jc-center">
                  <Button
                    label={t("motherChildAsset.confirm_button")}
                    disabled={!selectedRelation || selectedAssets.length === 0}
                    onClick={handleLinkAssets}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LinkedAssets;
