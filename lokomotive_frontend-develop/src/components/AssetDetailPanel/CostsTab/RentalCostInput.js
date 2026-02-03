import React, { useState, useEffect } from "react";
import axios from "axios";
import { useDispatch, useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import CustomInputText from "../../ShareComponents/CustomInputText";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button5.scss";

export default function RentalCostInput({ vin, refresh }) {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { listCurrencies } = useSelector((state) => state.apiCallData);
  const [selectedType, setSelectedType] = useState(null);
  const [selectedID, setSelectedID] = useState(null);
  const [requestIdName, setRequestIdName] = useState(null);
  const [requestIdList, setRequestIdList] = useState(null);
  const [rentalTotalCost, setRentalTotalCost] = useState("");
  const [rentalCurrency, setRentalCurrency] = useState(null);
  const [rentalError, setRentalError] = useState(true);
  const [dropdownReset, setDropdownReset] = useState(false);
  const [dropdownIDReset, setDropdownIDReset] = useState(Date.now());
  const request_types = [{
    name: "Asset Rental",
    code: "asset_rental"
  }, {
    name: "Incident",
    code: "incident"
  }, {
    name: "Maintenance",
    code: "maintenance"
  }, {
    name: "Repair",
    code: "repair"
  }];

  useEffect(() => {
    if (selectedType) {
      setDropdownIDReset(Date.now())
      setRequestIdName(null);
      setRequestIdList(null);
      setSelectedID(null);

      if (selectedType.code !== "asset_rental") {
        let url;
        if (selectedType.code === "repair") {
          url = `/api/v1/Repair/VIN/${vin}`
          setRequestIdName("work_order");
        } else if (selectedType.code === "maintenance") {
          url = `/api/v1/Maintenance/VIN/${vin}`
          setRequestIdName("work_order");
        } else if (selectedType.code === "incident") {
          url = `/api/v1/Accident/VIN/${vin}`
          setRequestIdName("custom_id");
        }
  
        const cancelTokenSource = axios.CancelToken.source();
        axios
          .get(`
            ${Constants.ENDPOINT_PREFIX}${url}`, 
            { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
          )
          .then((res) => {
            setRequestIdList(res.data);
          })
          .catch((error) => {
            ConsoleHelper(error);
          });
  
        return () => {
          //Doing clean up work, cancel the asynchronous api call
          cancelTokenSource.cancel("cancel the asynchronous api call");
        };
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedType]);

  const submitClick = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let data = {
      total_cost: rentalTotalCost,
      currency: rentalCurrency.id
    }

    if (selectedType.code === "asset_rental") {
      data.VIN = vin
    }
    else if (selectedType.code === "incident") {
      data.accident = selectedID.accident_id;
    } else if (selectedType.code === "maintenance") {
      data.maintenance = selectedID.maintenance_id;
    } else if (selectedType.code === "repair") {
      data.repair = selectedID.repair_id;
    }
    handleSubmit(data);
  }

  const handleSubmit = (data) => {
    loadingAlert();
    axios
      .post(`
        ${Constants.ENDPOINT_PREFIX}/api/v1/Rental/Add/Cost`, data, getAuthHeader()
      )
      .then((res) => {
        successAlert("msg", t("costsTab.add_rental_success"));
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
        resetForm();
        refresh(Date.now);
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  }

  const resetForm = () => {
    setSelectedType(null);
    setRequestIdName(null);
    setRequestIdList(null);
    setSelectedID(null);
    setRentalCurrency(null);
    setRentalTotalCost("");
    setRentalError(true);
    setDropdownReset(!dropdownReset);
    setDropdownIDReset(Date.now());
  };

  useEffect(() => {
    if (selectedType) {
      if (selectedType.code !== "asset_rental") {
        if (selectedID && rentalTotalCost && rentalCurrency) {
          setRentalError(false);
        }
        else {
          setRentalError(true);
        }
      } else {
        if (rentalTotalCost && rentalCurrency) {
          setRentalError(false);
        }
        else {
          setRentalError(true);
        }
      }
    } else {
      setRentalError(true);
    }
  }, [selectedType, selectedID, rentalTotalCost, rentalCurrency]);

  const selectType = (type) => {
    let selected = request_types.find((v) => v.code === type);
    setSelectedType(selected);
  };

  const selectID = (id) => {
    let selected = requestIdList.find((v) => v[requestIdName] === id);
    setSelectedID(selected);
  };

  const selectRentalCurrency = (id) => {
    let selected = listCurrencies.find((v) => v.id === parseInt(id));
    setRentalCurrency(selected);
  };

  return (
    <React.Fragment>
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <FormDropdown
          label={t("costsTab.request_type")}
          onChange={selectType}
          options={request_types}
          dataReady={request_types}
          plain_dropdown
          leftStatus
          reset={dropdownReset}
        />
      </div>
      {selectedType && selectedType.code === "asset_rental" ?
        null
        :
        <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
          <FormDropdown
            label={t("costsTab.request_id")}
            onChange={selectID}
            options={
              requestIdList &&
              requestIdList.map((request) => ({
                name: `ID: ${request[requestIdName]}`,
                code: request[requestIdName],
              }))
            }
            loading={selectedType && !requestIdList}
            disabled={!requestIdList}
            dataReady={requestIdList}
            plain_dropdown
            leftStatus
            reset={dropdownIDReset}
          />
        </div>
      }
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <FormDropdown
          label={t("costsTab.currency")}
          reset={dropdownReset}
          onChange={selectRentalCurrency}
          options={
            listCurrencies &&
            listCurrencies.map((currencyType) => ({
              name: currencyType.code,
              code: currencyType.id,
            }))
          }
          loading={!listCurrencies}
          disabled={!listCurrencies}
          dataReady={listCurrencies}
          plain_dropdown
          leftStatus
        />
      </div>

      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.total_cost")}</label>
        <CustomInputText
          type="number"
          placeholder={t("costsTab.total_cost")}
          value={rentalTotalCost}
          onChange={(val) => setRentalTotalCost(parseFloat(val))}
          leftStatus
        />
      </div>

      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <div className="p-d-flex p-jc-center p-mt-3 p-mb-5">
          <div className="btn-5 disable-bg">
            <Button
              label={t("costsTab.button_new_rental")}
              icon={"pi pi-check"}
              disabled={rentalError}
              onClick={() => {
                submitClick();
              }}
            />
          </div>
        </div>
      </div>
    </React.Fragment>
  );
}
