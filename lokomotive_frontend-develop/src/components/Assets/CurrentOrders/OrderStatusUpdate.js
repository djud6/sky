import React, { useState, useEffect, useMemo } from "react";
import axios from "axios";
import { useDispatch, useSelector } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { useTranslation } from "react-i18next";
import { getAuthHeader } from "../../../helpers/Authorization";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import CustomInputText from "../../ShareComponents/CustomInputText";
import AdditionalAlert from "../../ShareComponents/AdditionalAlert";
import RatingDialog from "../../ShareComponents/RatingDialog";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";

const OrderStatusUpdate = ({ request, dialogOpen, setDialogOpen, setDataReady }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { listJobSpecs, listCurrencies, listLocations, listBusinessUnits } = useSelector(
    (state) => state.apiCallData
  );
  const [selectedStatus, setSelectedStatus] = useState(null);
  const [vinNumber, setVinNumber] = useState("");
  const [jobSpec, setJobSpec] = useState("");
  const [confirmAlert, setConfirmAlert] = useState(false);
  const [deliveryCost, setDeliveryCost] = useState("");
  const [taxes, setTaxes] = useState("");
  const [totalCost, setTotalCost] = useState("");
  const [currency, setCurrency] = useState(null);
  const [isRatingFormShown, setIsRatingFormShown] = useState(false);
  const [ratingData, setRatingData] = useState({});

  const statusOptions = useMemo(() => {
    let options = [];
    if (!request.vendor) {
      options = [
        {
          name: t("requestProgress.awaiting_approval"),
          code: "awaiting approval",
        },
        {
          name: t("requestProgress.approved"),
          code: "approved",
        },
        {
          name: t("requestProgress.ordered"),
          code: "ordered",
        },
        {
          name: t("requestProgress.built"),
          code: "built",
        },
        {
          name: t("requestProgress.in_transit_to_client"),
          code: "in transit - to client",
        },
        {
          name: t("requestProgress.delivered"),
          code: "delivered",
        },
        {
          name: t("requestProgress.cancelled"),
          code: "cancelled",
        },
      ].filter((el) => el.code !== request.status?.toLowerCase());
    } else {
      if (request.status?.toLowerCase() === "awaiting approval") {
        options = [
          {
            name: t("requestProgress.cancelled"),
            code: "cancelled",
          },
        ];
      } else if (request.status?.toLowerCase() === "approved") {
        options = [
          {
            name: t("requestProgress.ordered"),
            code: "ordered",
          },
          {
            name: t("requestProgress.cancelled"),
            code: "cancelled",
          },
        ];
      } else if (request.status?.toLowerCase() === "in transit - to client") {
        options = [
          {
            name: t("requestProgress.delivered"),
            code: "delivered",
          },
        ];
      }
    }

    return options;
  }, [request, t]);

  useEffect(() => {
    let autoCalculate =
      parseFloat(deliveryCost ? deliveryCost : "0") + parseFloat(taxes ? taxes : "0");

    setTotalCost(autoCalculate);
  }, [deliveryCost, taxes]);

  const selectJobSpecification = (id) => {
    let selected = listJobSpecs.find((v) => v.job_specification_id === parseInt(id));
    setJobSpec(selected.name);
  };

  const handleUpdateStatus = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });

    let selectedBU = listBusinessUnits.find((bu) => bu.name === request.business_unit);
    let loc = listLocations.find((location) => location.location_id === selectedBU.location);

    if (selectedStatus === "delivered") {
      setConfirmAlert(false);
      let newAssetInfo = {
        VIN: vinNumber,
        model_number: request.model_number,
        manufacturer: request.manufacturer,
        location_name: loc.location_name,
        business_unit_name: request.business_unit,
        job_specification: jobSpec,
      };
      handleSubmit(newAssetInfo, request.id);
    }
  };

  const handleSubmit = (newAssetInfo, request_id) => {
    if (selectedStatus === "delivered") {
      if (vinNumber === "" || jobSpec === "") {
        generalErrorAlert(t("assetOrderDetails.submit_error_msg"));
      } else {
        loadingAlert();
        axios
          .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Add`, newAssetInfo, getAuthHeader())
          .then(() => {
            axios
              .post(
                `${Constants.ENDPOINT_PREFIX}/api/v1/AssetRequest/Update/Status`,
                {
                  asset_request_id: request_id,
                  status: "delivered",
                  vin: vinNumber,
                },
                getAuthHeader()
              )
              .then(() => {
                checkDeliveryCost();
              })
              .catch((error) => {
                onHide();
                generalErrorAlert(error.customErrorMsg);
                dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
                ConsoleHelper(error);
              });
          })
          .catch((error) => {
            generalErrorAlert(error.customErrorMsg);
            dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
            ConsoleHelper(error);
          });
      }
    } else {
      loadingAlert();
      axios
        .post(
          `${Constants.ENDPOINT_PREFIX}/api/v1/AssetRequest/Update/Status`,
          {
            asset_request_id: request_id,
            status: selectedStatus,
          },
          getAuthHeader()
        )
        .then(() => {
          onHide();
          refreshData(request);
        })
        .catch((error) => {
          generalErrorAlert(error.customErrorMsg);
          dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
          ConsoleHelper(error);
        });
    }
  };

  const getVendorRatingInfo = () => {
    const serviceType = "asset request";
    if (request.vendor) {
      setIsRatingFormShown(true);
      setRatingData({
        vendor_name: request.vendor_name,
        service_type: serviceType,
        request_status: selectedStatus,
        request_id: request.custom_id,
      });
    }
  };

  const checkDeliveryCost = () => {
    if (deliveryCost && taxes && currency) {
      onHide();
      axios
        .post(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Delivery/Add/Cost`,
          {
            asset_request: request.id,
            price: deliveryCost,
            taxes: taxes,
            total_cost: totalCost,
            currency: currency.id,
          },
          getAuthHeader()
        )
        .then(() => {
          refreshData(request);
        })
        .catch((error) => {
          onHide();
          setDataReady(false);
          generalErrorAlert(error.customErrorMsg);
          dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
          ConsoleHelper(error);
        });
    } else {
      onHide();
      refreshData(request);
    }
  };

  const refreshData = (data) => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
    successAlert("msg", t("assetRequestPanel.success_update_status"), () => {
      if (selectedStatus === "delivered") {
        getVendorRatingInfo();
      } else {
        setDataReady(false);
      }
    });
  };

  const onCancelChange = () => {
    setConfirmAlert(false);
  };

  const selectStatus = (status) => {
    setSelectedStatus(status);
  };

  const selectCurrency = (id) => {
    let selected = listCurrencies.find((v) => v.id === parseInt(id));
    setCurrency(selected);
  };

  const onHide = () => {
    setDialogOpen(false);
    setSelectedStatus(null);
    setVinNumber("");
    setJobSpec("");
  };
  let dialogFooter = (
    <Button
      label={t("general.submit")}
      icon="pi pi-check"
      onClick={() => {
        if (selectedStatus === "delivered") setConfirmAlert(true);
        else handleSubmit(false, request.id);
      }}
      disabled={!selectedStatus}
    />
  );

  const submitVendorRating = (rating, feedback) => {
    const cancelTokenSource = axios.CancelToken.source();
    loadingAlert();
    setRatingData((prev) => {
      prev["rating"] = rating;
      prev["feedback"] = feedback;
      return prev;
    });

    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api-vendor/v1/Ratings/Add`, ratingData, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then(() => {
        setIsRatingFormShown(false);
        setDataReady(false);
        successAlert("msg", t("general.rating_update_success"));
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  return (
    <div>
      <Dialog
        className="custom-main-dialog"
        header="Confirmation"
        visible={dialogOpen}
        footer={dialogFooter}
        onHide={onHide}
        style={{ width: "50vw" }}
        breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
      >
        <div className="p-field">
          <label className="h6">{t("general.update_status")}</label>
          <FormDropdown
            className="w-100"
            onChange={selectStatus}
            options={statusOptions}
            dataReady={statusOptions.length !== 0 ? true : false}
            plain_dropdown
            leftStatus
            reset={"disabled"}
          />
        </div>
        {selectedStatus === "delivered" && (
          <React.Fragment>
            <div className="p-field">
              <label className="h6">{t("general.vin_num")}</label>
              <CustomInputText
                className="w-100"
                value={vinNumber}
                onChange={setVinNumber}
                leftStatus
              />
            </div>
            <div className="p-field">
              <label className="h6">{t("assetOrderDetails.job_specification")}</label>
              <FormDropdown
                onChange={selectJobSpecification}
                options={
                  listJobSpecs &&
                  listJobSpecs.map((jobSpec) => ({
                    name: jobSpec.name,
                    code: jobSpec.job_specification_id,
                  }))
                }
                loading={!listJobSpecs}
                disabled={!listJobSpecs}
                plain_dropdown
                leftStatus
              />
            </div>
          </React.Fragment>
        )}
        {selectedStatus && selectedStatus === "delivered" && (
          <React.Fragment>
            <hr />
            <h4>{"Delivery Cost Form (Optional)"}</h4>
            <div className="p-field">
              <label>{t("costsTab.delivery_cost")}</label>
              <CustomInputText
                type="number"
                value={deliveryCost}
                onChange={(val) => setDeliveryCost(parseFloat(val))}
                className="w-100"
                leftStatus
              />
            </div>
            <div className="p-field">
              <label>{t("costsTab.taxes")}</label>
              <CustomInputText
                type="number"
                value={taxes}
                onChange={(val) => setTaxes(parseFloat(val))}
                className="w-100"
                leftStatus
              />
            </div>
            <div className="p-field">
              <label>{t("costsTab.total_cost")}</label>
              <CustomInputText
                type="number"
                value={totalCost}
                onChange={(val) => setTotalCost(parseFloat(val))}
                className="w-100"
                leftStatus
              />
            </div>
            <div className="p-field">
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
              />
            </div>
          </React.Fragment>
        )}
      </Dialog>
      {confirmAlert && (
        <AdditionalAlert
          title={t("additionalAlert.confirm_alert_title")}
          text={t("assetOrderDetails.confirm_alert_text")}
          warningMsg={t("additionalAlert.confirm_alert_title")}
          confirmBtn={t("additionalAlert.confirm_yes")}
          cancelBtn={t("additionalAlert.cancel_no")}
          onConfirm={handleUpdateStatus}
          onCancel={onCancelChange}
        />
      )}

      {isRatingFormShown && (
        <RatingDialog
          headerTitle={t("general.rate_vendor")}
          data={ratingData}
          btn1Label={t("general.skip")}
          btn1Action={() => {
            setDataReady(false);
          }}
          btn2Action={(rating, feedback) => {
            submitVendorRating(rating, feedback);
          }}
        />
      )}
    </div>
  );
};

export default OrderStatusUpdate;
