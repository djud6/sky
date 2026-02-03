import React, { useState, useEffect, useMemo } from "react";
import axios from "axios";
import moment from "moment";
import { useSelector } from "react-redux";
import { useDispatch } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import DatePicker from "../../ShareComponents/DatePicker";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import RatingDialog from "../../ShareComponents/RatingDialog";
import CustomInputText from "../../ShareComponents/CustomInputText";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";

const RepairStatusUpdate = ({
  repair,
  completeDialogStatus,
  setCompleteDialogStatus,
  setSelectedRepair,
  setRepairRequests,
  setDataReady,
  category,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { listCurrencies } = useSelector((state) => state.apiCallData);
  const [selectedStatus, setSelectedStatus] = useState(null);
  const [repairCompleteDate, setRepairCompleteDate] = useState(new Date());
  const [deliveryCost, setDeliveryCost] = useState("");
  const [isRatingFormShown, setIsRatingFormShown] = useState(false);
  const [ratingData, setRatingData] = useState({});
  const [taxes, setTaxes] = useState("");
  const [totalCost, setTotalCost] = useState("");
  const [currency, setCurrency] = useState(null);
  const statusOptions = useMemo(() => [
    {
      name: t("requestProgress.cancelled"),
      code: "cancelled",
    },
    {
      name: t("requestProgress.denied"),
      code: "denied",
    },
    {
      name: t("requestProgress.awaiting_approval"),
      code: "awaiting approval",
    },
    {
      name: t("requestProgress.approved"),
      code: "approved",
    },
    {
      name: t("requestProgress.scheduled"),
      code: "schedule",
    },
    {
      name: t("requestProgress.waiting_on_parts"),
      code: "waiting on parts",
    },
    {
      name: t("requestProgress.under_repair"),
      code: "under repair",
    },
    {
      name: t("requestProgress.waiting_for_pickup"),
      code: "waiting for pickup",
    },
    {
      name: t("requestProgress.in_transit"),
      code: "in transit",
    },
    {
      name: t("requestProgress.complete"),
      code: "complete",
    },
    {
      name: t("requestProgress.delivered"),
      code: "delivered",
    },
  ], [t]);

  useEffect(() => {
    let autoCalculate =
      parseFloat(deliveryCost ? deliveryCost : "0") + parseFloat(taxes ? taxes : "0");

    setTotalCost(autoCalculate);
  }, [deliveryCost, taxes]);

  const handleRepairComplete = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });

    let updateData;
    if (repair.status === "in transit - to client") {
      updateData = {
        repair_id: repair.repair_id,
        status: "delivered",
        date_delivered: moment(repairCompleteDate).format("YYYY-MM-DD HH:mm:ss.SSS"),
      };
    } else {
      updateData = {
        repair_id: repair.repair_id,
        status: selectedStatus,
        ...(selectedStatus === "delivered" && {
          date_delivered: moment(repairCompleteDate).format("YYYY-MM-DD HH:mm:ss.SSS"),
        }),
      };
    }

    handleSubmit(updateData);
  };

  const handleSubmit = (data) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Update/Status`, data, getAuthHeader())
      .then(() => {
        if (repair.status === "in transit - to client" || selectedStatus === "delivered") {
          checkDeliveryCost(data);
        } else {
          onHide();
          refreshData(data);
        }
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  const checkDeliveryCost = (data) => {
    if (deliveryCost && taxes && currency) {
      axios
        .post(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Delivery/Add/Cost`,
          {
            repair: repair.repair_id,
            price: deliveryCost,
            taxes: taxes,
            total_cost: totalCost,
            currency: currency.id,
          },
          getAuthHeader()
        )
        .then(() => {
          onHide();
          refreshData(data);
        })
        .catch((error) => {
          generalErrorAlert(error.customErrorMsg);
          dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
          ConsoleHelper(error);
        });
    } else {
      onHide();
      refreshData(data);
    }
  };

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

  const getVendorRatingInfo = () => {
    const serviceType = "repair";
    if (repair.vendor && !repair.in_house) {
      setIsRatingFormShown(true);
      setRatingData({
        vendor_name: repair.vendor_name,
        service_type: serviceType,
        request_status: "delivered",
        request_id: repair.work_order,
      });
    } else {
      setDataReady(false);
    }
  };

  const refreshData = async (data) => {
    const cancelTokenSource = axios.CancelToken.source();
    const INCOMPLETE_STATUS_VALUES = [
      "waiting for vendor",
      "awaiting approval",
      "approved",
      "in transit - to vendor",
      "in progress",
      "at vendor",
      "complete",
      "in transit - to client",
    ];
    let requestURL;
    if (category === "inProgress") {
      if (!INCOMPLETE_STATUS_VALUES.includes(selectedStatus?.toLowerCase())) {
        successAlert("msg", t("repairDetails.success_update_status"), () => {
          if (repair.status === "in transit - to client" || selectedStatus === "delivered") {
            getVendorRatingInfo();
          } else {
            setDataReady(false);
          }
        });
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
      } else {
        requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/List`;
      }
    } else if (category === "completed") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Complete/List`;
    }

    if (requestURL) {
      let response = await axios.get(requestURL, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });

      const repairs = response.data;
      let selectedRepair;
      if (category === "inProgress") {
        for (var i in repairs) {
          if (repairs[i].repair_id === data.repair_id) {
            selectedRepair = repairs[i];
          }
          if (repairs[i].is_urgent) repairs[i].is_urgent = "Yes";
          else repairs[i].is_urgent = "No";

          if (repairs[i].in_house) {
            repairs[i].vendor_name = "In-house Repair";
          } else if (!repairs[i].in_house && !repairs[i].vendor_name) {
            if (repairs[i].vendor_email && !["", "NA"].includes(repairs[i].vendor_email)) {
              repairs[i].vendor_name = repairs[i].vendor_email;
            }
          }
        }
      } else if (category === "completed") {
        for (var y in repairs) {
          if (repairs[y].repair_id === data.repair_id) {
            selectedRepair = repairs[y];
          }
          if (repairs[y].in_house) {
            repairs[y].vendor_name = "In-house Repair";
          } else if (!repairs[y].in_house && !repairs[y].vendor_name) {
            if (repairs[y].vendor_email && !["", "NA"].includes(repairs[y].vendor_email)) {
              repairs[y].vendor_name = repairs[y].vendor_email;
            }
          }
        }
      }

      setSelectedRepair(selectedRepair);
      setRepairRequests(repairs);
      successAlert("msg", t("repairDetails.success_update_status"));
      dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
    }
  };

  const renderFooter = () => {
    return (
      <Button
        label={t("general.update")}
        icon="pi pi-check"
        className="p-button-success p-mt-4"
        onClick={() => {
          handleRepairComplete();
        }}
        disabled={
          (!selectedStatus && repair.status !== "in transit - to client") ||
          (repair.status === "in transit - to client" && !repairCompleteDate) ||
          (selectedStatus === "delivered" && !repairCompleteDate)
        }
      />
    );
  };

  const selectStatus = (status) => {
    setSelectedStatus(status);
  };

  const selectCurrency = (id) => {
    let selected = listCurrencies.find((v) => v.id === parseInt(id));
    setCurrency(selected);
  };

  const onHide = () => {
    setCompleteDialogStatus(false);
    setSelectedStatus(null);
  };

  return (
    <div>
      <Dialog
        className="custom-main-dialog"
        header={t("repairIssueDetails.dialog_title")}
        visible={completeDialogStatus}
        footer={renderFooter}
        onHide={onHide}
        style={{ width: "40vw" }}
        breakpoints={{ "1280px": "40vw", "960px": "60vw", "768px": "80vw" }}
      >
        {repair.status !== "in transit - to client" && (
          <div>
            <div className="p-mb-3">{t("general.update_status")}</div>
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
        )}
        {(selectedStatus === "delivered" || repair.status === "in transit - to client") && (
          <div className="p-d-flex p-flex-column p-jc-center">
            <div className="p-mb-3">{t("repairIssueDetails.dialog_text")}</div>
            <DatePicker
              onChange={setRepairCompleteDate}
              initialDate={repairCompleteDate}
              maxDate={new Date()}
              leftStatus
            />
          </div>
        )}
        {(selectedStatus === "delivered" || repair.status === "in transit - to client") && (
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

export default RepairStatusUpdate;
