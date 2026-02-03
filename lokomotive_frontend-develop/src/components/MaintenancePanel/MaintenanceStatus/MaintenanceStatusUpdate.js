import React, { useState, useEffect, useMemo } from "react";
import axios from "axios";
import { useSelector } from "react-redux";
import { useDispatch } from "react-redux";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import CustomInputText from "../../ShareComponents/CustomInputText";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import RatingDialog from "../../ShareComponents/RatingDialog";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/dialogStyles.scss";

const MaintenanceStatusUpdate = ({
  maintenance,
  updateDialogStatus,
  setUpdateDialogStatus,
  setSelectedMaintenance,
  setMaintenances,
  setDataReady,
  maintenanceStatus,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { listCurrencies } = useSelector((state) => state.apiCallData);
  const [selectedStatus, setSelectedStatus] = useState(null);
  const [deliveryCost, setDeliveryCost] = useState("");
  const [taxes, setTaxes] = useState("");
  const [totalCost, setTotalCost] = useState("");
  const [currency, setCurrency] = useState(null);
  const [isRatingFormShown, setIsRatingFormShown] = useState(false);
  const [ratingData, setRatingData] = useState({});

  const statusOptions = useMemo(() => {
    let options = [];
    if (maintenance.in_house || !maintenance.assigned_vendor) {
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
          name: t("requestProgress.in_transit_to_vendor"),
          code: "in transit - to vendor",
        },
        {
          name: t("requestProgress.at_vendor"),
          code: "at vendor",
        },
        {
          name: t("requestProgress.complete"),
          code: "complete",
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
      ].filter((el) => el.code !== maintenance.status?.toLowerCase());
    } else {
      if (maintenance.status?.toLowerCase() === "awaiting approval") {
        options = [
          {
            name: t("requestProgress.cancelled"),
            code: "cancelled",
          },
        ];
      } else if (maintenance.status?.toLowerCase() === "approved") {
        options = [
          {
            name: t("requestProgress.in_transit_to_vendor"),
            code: "in transit - to vendor",
          },
          {
            name: t("requestProgress.cancelled"),
            code: "cancelled",
          },
        ];
      } else if (maintenance.status?.toLowerCase() === "in transit - to client") {
        options = [
          {
            name: t("requestProgress.delivered"),
            code: "delivered",
          },
        ];
      }
    }

    return options;
  }, [maintenance, t]);

  useEffect(() => {
    let autoCalculate =
      parseFloat(deliveryCost ? deliveryCost : "0") + parseFloat(taxes ? taxes : "0");

    setTotalCost(autoCalculate);
  }, [deliveryCost, taxes]);

  const handleStatusUpdate = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });

    let updateData = {
      maintenance_id: maintenance.maintenance_id,
      status: selectedStatus,
    };
    handleSubmit(updateData);
  };

  const handleSubmit = (data) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Update/Status`, data, getAuthHeader())
      .then(() => {
        if (selectedStatus === "delivered") {
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

  const getVendorRatingInfo = () => {
    const serviceType = "maintenance";
    if (maintenance.assigned_vendor && !maintenance.in_house) {
      setIsRatingFormShown(true);
      setRatingData({
        vendor_name: maintenance.vendor_name,
        service_type: serviceType,
        request_status: "delivered",
        request_id: maintenance.work_order,
      });
    } else {
      setDataReady(false);
    }
  };

  const checkDeliveryCost = (data) => {
    if (deliveryCost && taxes && currency) {
      axios
        .post(
          `${Constants.ENDPOINT_PREFIX}/api/v1/Delivery/Add/Cost`,
          {
            maintenance: maintenance.maintenance_id,
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

  const refreshData = async (data) => {
    const cancelTokenSource = axios.CancelToken.source();
    const INCOMPLETE_STATUS_VALUES = [
      "waiting for vendor",
      "awaiting approval",
      "approved",
      "in transit - to vendor",
      "at vendor",
      "complete",
      "in transit - to client",
    ];
    let requestURL;
    if (maintenanceStatus === "Outstanding") {
      if (INCOMPLETE_STATUS_VALUES.includes(selectedStatus?.toLowerCase())) {
        successAlert("msg", t("maintenanceDetails.success_update_status"), () => {
          if (selectedStatus === "delivered") {
            getVendorRatingInfo();
          } else {
            setDataReady(false);
          }
        });
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
      } else {
        requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/List`;
      }
    } else if (maintenanceStatus === "Completed") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Completed/List`;
    } else if (maintenanceStatus === "search") {
      requestURL = `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/VIN/${maintenance.VIN}`;
    }

    if (requestURL) {
      let response = await axios.get(requestURL, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });

      const maintenances = response.data;
      let selectedMaintenance;
      for (var i in maintenances) {
        if (maintenances[i].maintenance_id === data.maintenance_id) {
          selectedMaintenance = maintenances[i];
        }

        if (maintenances[i].in_house) {
          maintenances[i].vendor_name = "In-house Maintenance";
        } else if (!maintenances[i].in_house && !maintenances[i].vendor_name) {
          if (maintenance[i].vendor_email && !["", "NA"].includes(maintenance[i].vendor_email)) {
            maintenance[i].vendor_name = maintenance[i].vendor_email;
          }
        }
      }

      setSelectedMaintenance(selectedMaintenance);
      setMaintenances(maintenances);
      successAlert("msg", t("maintenanceDetails.success_update_status"));
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
          handleStatusUpdate();
        }}
        disabled={!selectedStatus}
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
    setUpdateDialogStatus(false);
    setSelectedStatus(null);
  };

  return (
    <div>
      <Dialog
        className="custom-main-dialog"
        header={t("maintenanceDetails.update_maintenance_status")}
        visible={updateDialogStatus}
        footer={renderFooter}
        onHide={onHide}
        style={{ width: "40vw" }}
        breakpoints={{ "1280px": "40vw", "960px": "60vw", "768px": "80vw" }}
      >
        <div className="p-field">
          <label>{t("general.update_status")}</label>
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

export default MaintenanceStatusUpdate;
