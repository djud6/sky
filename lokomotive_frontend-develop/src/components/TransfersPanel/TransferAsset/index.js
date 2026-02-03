import React, { useState, useEffect } from "react";
import axios from "axios";
import swal from "sweetalert";
import { useDispatch, useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { useParams, useHistory } from "react-router-dom";
import { Button } from "primereact/button";
import { faExchangeAlt } from "@fortawesome/free-solid-svg-icons";
import { getAuthHeader } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import WarningMsg from "../../ShareComponents/WarningMsg";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import CustomTextArea from "../../ShareComponents/CustomTextArea";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import MultiSelectDropdown from "../../ShareComponents/Forms/MultiSelectDropdown";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import CardWidget from "../../ShareComponents/CardWidget";
import FileUploadInput from "../../ShareComponents/FileUploadInput";
import { loadingAlert, errorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button1.scss";
import "../../../styles/helpers/fileInput.scss";
import "../../../styles/TransferPanel/TransferAsset/TransferAsset.scss";

const AssetTransferPanel = () => {
  const { t } = useTranslation();
  const { vin } = useParams();
  const history = useHistory();
  const dispatch = useDispatch();
  const { listLocations } = useSelector((state) => state.apiCallData);
  const [selectedTransferLocation, setSelectedTransferLocation] = useState(null);
  const [dropdownReset, setDropdownReset] = useState(false);
  const [transferDescription, setTransferDescription] = useState("");
  const [assetVin, setAssetVin] = useState(vin ? vin : null);
  const [asset, setAsset] = useState(history.location.state?.vehicle);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const [otherDocs, setOtherDocs] = useState([]);
  const [otherDocsName, setOtherDocsName] = useState([]);
  const [forceUpdate, setForceUpdate] = useState(Date.now());

  const [selectedChildren, setSelectedChildren] = useState([]);

  const changeChildren = (e) => {
    setSelectedChildren(e.value);
  };

  const resetForm = () => {
    setAssetVin(null);
    setForceUpdate(Date.now());
    setSelectedTransferLocation(null);
    setSelectedChildren(null);
    setTransferDescription("");
    setOtherDocs([]);
    setOtherDocsName([]);
    setDropdownReset(!dropdownReset);
  };

  useEffect(() => {
    if (asset && !assetVin) {
      setAssetVin(asset.VIN);
    }
    if (!asset) setAssetVin(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [asset]);

  const sendTransferRequest = (transferData) => {
    loadingAlert();
    const headers = getAuthHeader();
    headers.headers["Content-Type"] = "application/json";
    const requestConfig = {
      method: "post",
      url: `${Constants.ENDPOINT_PREFIX}/api/v1/Transfer/Create`,
      ...headers,
      data: transferData,
    };
    axios(requestConfig)
      .then(() => {
        successAlert();
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
      })
      .catch((error) => {
        ConsoleHelper(error);
        errorAlert(error.customErrorMsg, sendTransferRequest);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  let formFilled = false;
  if (selectedTransferLocation && transferDescription.length > 0) formFilled = true;

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });

    let set = new Set();
    let selectedChidrenStr = '&%&';
    for (var i = 0; i < selectedChildren.length; i++) {
      if (!set.has(selectedChildren[i].name)) {
          selectedChidrenStr = selectedChidrenStr + selectedChildren[i].name + '&%&'
          set.add(selectedChildren[i].name);
      }
    }

    let transferData = new FormData();
    if (formFilled) {
      transferData.append(
        "data",
        JSON.stringify({
          transfer_data: {
            VIN: assetVin,
            destination_location: selectedTransferLocation.location_id,
            justification: transferDescription,
            is_disposal: false,
            attached_children: selectedChidrenStr,
          },
          // TODO: Replace the placeholder info for approval_data
          approval_data: {
            title: "Transfer Approval",
            description: "This is an approval made for testing purposes.",
          },
        })
      );

      let file_specs = {
        file_info: [],
      };

      for (let i = 0; i < otherDocs.length; i++) {
        file_specs.file_info.push({ file_name: otherDocs[i].name, purpose: "other" });
      }

      for (let i = 0; i < otherDocs.length; i++) {
        transferData.append("files", otherDocs[i]);
      }
      transferData.append("file_specs", JSON.stringify(file_specs));

      sendTransferRequest(transferData);
    }
  };

  const successAlert = () => {
    return swal({
      title: t("general.success"),
      text: t("assetTransferPanel.asset_transfer_request_submitted"),
      icon: "success",
      buttons: {
        return: t("assetTransferPanel.transfers_list"),
        assetTransfers: t("general.new_request"),
      },
    }).then((value) => {
      switch (value) {
        case "return":
          history.push("/transfers/list");
          break;
        case "assetTransfers":
          resetForm();
          break;
        default:
          resetForm();
      }
    });
  };

  const selectTransferLocation = (id) => {
    let selected = listLocations.find((v) => v.location_id === parseInt(id));
    setSelectedTransferLocation(selected);
  };

  return (
    <div>
      {isMobile && (
        <QuickAccessTabs
          tabs={["Map", "Transfers", "Request"]}
          activeTab={"Request"}
          urls={["/transfers", "/transfers/list", "/transfers/asset-transfer"]}
        />
      )}
      <PanelHeader icon={faExchangeAlt} text={"Transfer an Asset"} />
      {!isMobile && (
        <QuickAccessTabs
          tabs={["Transfer Map", "List Transfers", "Transfer Asset"]}
          activeTab={"Transfer Asset"}
          urls={["/transfers", "/transfers/list", "/transfers/asset-transfer"]}
        />
      )}
      <div className={`${isMobile ? "p-pb-4" : "p-mt-5"}`}>
        {!vin && (
          <VINSearch
            key={forceUpdate}
            onVehicleSelected={(v) => {
              Array.isArray(v) && v.length === 0 ? setAsset(null) : setAsset(v);
            }}
          />
        )}
      </div>
      {assetVin ? (
        asset && !asset.has_transfer ? (
          <div className="transfer-form-container">
            <div className="inner-container">
              <h4 className="title">
                {t("assetTransferPanel.asset_transfer_for_vin", { vin: assetVin })}
              </h4>
              <form id="request-form" onSubmit={handleSubmit}>
                {!isMobile ? (
                  <React.Fragment>
                    <div className="p-d-flex">
                      <div className="form-q">
                        <label>{t("assetTransferPanel.transfer_location")}</label>
                      </div>
                      <div className="form-a">
                        <FormDropdown
                          onChange={selectTransferLocation}
                          options={
                            listLocations &&
                            listLocations.map((location) => ({
                              name: location.location_name,
                              code: location.location_id,
                            }))
                          }
                          loading={!listLocations}
                          disabled={!listLocations}
                          plain_dropdown
                          leftStatus
                        />
                      </div>
                    </div>
                    <div className="p-d-flex" style={{marginBottom: '15px'}}>
                      <div className="form-q">
                        <label>{t("assetTransferPanel.transfer_children")}</label>
                      </div>
                      <div className="form-a">
                        <MultiSelectDropdown
                          value={selectedChildren}
                          onChange={changeChildren}
                          options={asset.children.map(
                            children => ({name: children})
                          )}
                          filterMatchMode = "contains"
                          leftStatus
                          maxSelectedLabels={3}
                          selectedItemsLabel = "{0} Children selected"
                          placeholder = {"Select Option"}
                        />
                      </div>
                    </div>
                    <div className="p-d-flex">
                      <div className="form-q">
                        <label className="col-form-label">
                          {t("assetTransferPanel.transfer_justification")}
                        </label>
                      </div>
                      <div className="form-a">
                        <CustomTextArea
                          rows={5}
                          cols={30}
                          value={transferDescription}
                          onChange={setTransferDescription}
                          autoResize
                          leftStatus
                        />
                      </div>
                    </div>
                    <div className="p-d-flex p-mt-2">
                      <div className="form-q">
                        <label>{t("assetTransferPanel.transfer_files")}</label>
                      </div>
                      <div className="form-a">
                        <div className="custom-file input-files-container">
                          <FileUploadInput
                            images={otherDocs}
                            setImages={setOtherDocs}
                            imageNames={otherDocsName}
                            setImageNames={setOtherDocsName}
                            fileTypes=".pdf,.doc,.docx"
                            maxNumberOfFiles={20}
                          />
                        </div>
                      </div>
                    </div>
                  </React.Fragment>
                ) : (
                  <div className="mobile-form">
                    <CardWidget status={selectedTransferLocation} blueBg>
                      <div className="p-d-flex p-flex-column">
                        <label>{t("assetTransferPanel.transfer_location")}</label>
                        <div className="w-100">
                          <FormDropdown
                            onChange={selectTransferLocation}
                            options={
                              listLocations &&
                              listLocations.map((location) => ({
                                name: location.location_name,
                                code: location.location_id,
                              }))
                            }
                            loading={!listLocations}
                            disabled={!listLocations}
                            plain_dropdown
                          />
                        </div>
                      </div>
                    </CardWidget>
                    <CardWidget status={selectedChildren} blueBg>
                      <div className="p-d-flex p-flex-column">
                        <label>{t("assetTransferPanel.transfer_children")}</label>
                        <div className="w-100">
                          <MultiSelectDropdown
                            value={selectedChildren}
                            onChange={changeChildren}
                            options={asset.children.map(
                              children => ({name: children})
                            )}
                            filterMatchMode = "contains"
                            leftStatus
                            maxSelectedLabels={3}
                            selectedItemsLabel = "{0} Children selected"
                            placeholder = {"Select Option"}
                          />
                        </div>
                      </div>
                    </CardWidget>
                    <CardWidget status={transferDescription} blueBg>
                      <label>{t("assetTransferPanel.transfer_justification")}</label>
                      <div className="w-100">
                        <CustomTextArea
                          rows={5}
                          cols={30}
                          value={transferDescription}
                          onChange={setTransferDescription}
                          autoResize
                        />
                      </div>
                    </CardWidget>
                    <CardWidget status={otherDocs.length > 0} blueBg>
                      <label>{t("assetTransferPanel.transfer_files")}</label>
                      <div className="custom-file input-files-container">
                        <FileUploadInput
                          images={otherDocs}
                          setImages={setOtherDocs}
                          imageNames={otherDocsName}
                          setImageNames={setOtherDocsName}
                          fileTypes=".pdf,.doc,.docx"
                          maxNumberOfFiles={20}
                        />
                      </div>
                    </CardWidget>
                  </div>
                )}
                <div className={`btn-1 p-d-flex p-my-5 ${isMobile ? "p-jc-center" : "p-jc-end"}`}>
                  <Button
                    label={t("assetTransferPanel.request_transfer")}
                    className=""
                    disabled={!formFilled}
                  />
                </div>
              </form>
            </div>
          </div>
        ) : (
          <div className={`${isMobile ? "p-mt-3" : ""}`}>
            <WarningMsg message={t("assetTransferPanel.transfer_warning_msg")} />
          </div>
        )
      ) : null}
    </div>
  );
};

export default AssetTransferPanel;
