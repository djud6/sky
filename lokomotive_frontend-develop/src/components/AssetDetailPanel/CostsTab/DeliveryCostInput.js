import React, { useState, useEffect } from "react";
import axios from "axios";
import { useDispatch, useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import CustomInputText from "../../ShareComponents/CustomInputText";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";

const DeliveryCostInput = ({ vin, refresh }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { listCurrencies } = useSelector((state) => state.apiCallData);
  const [deliveryCost, setDeliveryCost] = useState("");
  const [taxes, setTaxes] = useState("");
  const [totalCost, setTotalCost] = useState("");
  const [selectedType, setSelectedType] = useState(null);
  const [selectedID, setSelectedID] = useState(null);
  const [requestIdName, setRequestIdName] = useState(null);
  const [requestIdList, setRequestIdList] = useState(null);
  const [currency, setCurrency] = useState(null);
  const [dropdownIDReset, setDropdownIDReset] = useState(Date.now());
  const [dropdownReset, setDropdownReset] = useState(Date.now());
  const request_types = [{
    name: "Repair",
    code: "repair"
  }, {
    name: "Maintenance",
    code: "maintenance"
  }, {
    name: "Disposal",
    code: "disposal"
  }];

  useEffect(() => {
    if (selectedType) {
      setDropdownIDReset(Date.now())
      setRequestIdName(null);
      setRequestIdList(null);
      setSelectedID(null);

      let url;
      if (selectedType.code === "repair") {
        url = `/api/v1/Repair/Complete/List`
        setRequestIdName("work_order");
      } else if (selectedType.code === "maintenance") {
        url = `/api/v1/Maintenance/VIN/${vin}`
        setRequestIdName("work_order");
      } else if (selectedType.code === "disposal") {
        url = `/api/v1/AssetDisposal/List`
        setRequestIdName("custom_id");
      }

      const cancelTokenSource = axios.CancelToken.source();
      axios
        .get(`
          ${Constants.ENDPOINT_PREFIX}${url}`, 
          { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
        )
        .then((res) => {
          let idList = res.data.filter((request) => 
            request.VIN === vin && request.status === "delivered"
          );
          setRequestIdList(idList);
        })
        .catch((error) => {
          ConsoleHelper(error);
        });

      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedType]);

  useEffect(() => {
    let autoCalculate = 
      parseFloat(deliveryCost ? deliveryCost : "0") + 
      parseFloat(taxes ? taxes : "0");

    setTotalCost(autoCalculate);
  }, [deliveryCost, taxes]);

  const submitClick = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let data = {
      price: deliveryCost,
      taxes: taxes,
      total_cost: totalCost,
      currency: currency.id
    }

    if (selectedType.code === "repair") {
      data.repair = selectedID.repair_id;
    } else if (selectedType.code === "maintenance") {
      data.maintenance = selectedID.maintenance_id;
    } else if (selectedType.code === "disposal") {
      data.disposal = selectedID.id;
    }
    handleSubmit(data);
  }

  const handleSubmit = (data) => {
    loadingAlert();
    axios
      .post(`
        ${Constants.ENDPOINT_PREFIX}/api/v1/Delivery/Add/Cost`, data, getAuthHeader()
      )
      .then((res) => {
        successAlert("msg", t("costsTab.add_delivery_success"));
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
    setDeliveryCost("");
    setTaxes("");
    setTotalCost("");
    setSelectedType("");
    setSelectedID("");
    setRequestIdName(null);
    setRequestIdList(null);
    setCurrency(null);
    setDropdownIDReset(Date.now());
    setDropdownReset(Date.now());
  };

  const selectType = (type) => {
    let selected = request_types.find((v) => v.code === type);
    setSelectedType(selected);
  };

  const selectID = (id) => {
    let selected = requestIdList.find((v) => v[requestIdName] === id);
    setSelectedID(selected);
  };

  const selectCurrency = (id) => {
    let selected = listCurrencies.find((v) => v.id === parseInt(id));
    setCurrency(selected);
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
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.delivery_submit_label")}</label>
        <CustomInputText
          type="number"
          value={deliveryCost}
          onChange={(val) => setDeliveryCost(parseFloat(val))}
          className="w-100"
          leftStatus
        />
      </div>
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.taxes")}</label>
        <CustomInputText
          type="number"
          value={taxes}
          onChange={(val) => setTaxes(parseFloat(val))}
          className="w-100"
          leftStatus
        />
      </div>
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <label>{t("costsTab.total_cost")}</label>
        <CustomInputText
          type="number"
          value={totalCost}
          onChange={(val) => setTotalCost(parseFloat(val))}
          className="w-100"
          leftStatus
        />
      </div>
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <FormDropdown
          label={t("costsTab.currency")}
          onChange={selectCurrency}
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
          reset={dropdownReset}
        />
      </div>
      <div className="p-field p-col-12 p-lg-10 p-xl-6 p-p-2">
        <div className="p-d-flex p-jc-center p-mt-3 p-mb-5">
          <div className="btn-5 disable-bg">
            <Button
              label={t("costsTab.button_new_delivery")}
              icon={"pi pi-check"}
              disabled={
                !selectedType ||
                !selectedID ||
                !deliveryCost || 
                !taxes ||
                !totalCost ||
                !currency
              }
              onClick={() => submitClick()}
            />
          </div>
        </div>
      </div>
    </React.Fragment>
  )
}

export default DeliveryCostInput;