import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { useDispatch, useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../constants";
import { CTRL_AUDIO_PLAY } from "../../redux/types/audioTypes";
import { getAuthHeader } from "../../helpers/Authorization";
import { Button } from "primereact/button";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { Toolbar } from "primereact/toolbar";
import { Dialog } from "primereact/dialog";
import { SelectButton } from "primereact/selectbutton";
import FormDropdown from "../ShareComponents/Forms/FormDropdown";
import { loadingAlert, successAlert, errorAlert } from "../ShareComponents/CommonAlert";
import { filterIssue, formatIssueTitle } from "../../helpers/helperFunctions";
import CustomInputNumber from "../ShareComponents/CustomInputNumber";
import Tooltip from "../ShareComponents/Tooltip/Tooltip";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import "../../styles/ShareComponents/Table/table.scss";
import "../../styles/dialogStyles.scss";
import "../../styles/helpers/button2.scss";
import "../../styles/helpers/textfield1.scss";

const LaborCostTable = ({
  request,
  laborInfo,
  issues,
  maintenanceID,
  costDataReady,
  setCostDataReady,
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { listCurrencies } = useSelector((state) => state.apiCallData);
  const [cost, setCost] = useState(null);
  const [costDialog, setCostDialog] = useState(false);
  const [deleteCostDialog, setDeleteCostDialog] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [taxOption, setTaxOption] = useState("Amount($)");
  const [onAdd, setOnAdd] = useState(false);
  const [onUpdate, setOnUpdate] = useState(false);
  const [deleteCostID, setDeleteCostID] = useState(null);
  const [defaultCurrency, setDefaultCurrency] = useState(null);
  const taxOptions = ["Amount($)", "Percentage(%)"];
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  let emptyCost = {
    base_hourly_rate: undefined,
    total_base_hours: "",
    overtime_rate: undefined,
    total_overtime_hours: "",
    taxes: undefined,
    total_cost: null,
    currency: null,
  };
  const dtRef = useRef(null);

  useEffect(() => {
    if (!onAdd && !onUpdate && costDataReady) {
      setOnAdd(false);
      setOnUpdate(false);
      setCostDialog(false);
      setSelectedIssue(null);
      setTaxOption("Amount($)");
      setDefaultCurrency(null);
    }
  }, [onAdd, onUpdate, costDataReady]);

  useEffect(() => {
    if (onUpdate) {
      const filtered = listCurrencies.filter((c) => {
        return c.code === cost.currency;
      });
      let reformatCurrency = {
        name: filtered[0].name,
        code: filtered[0].id,
      };
      setDefaultCurrency(reformatCurrency);
    }
    // eslint-disable-next-line
  }, [onUpdate]);

  const submitLaborCost = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    if (!cost.base_hourly_rate || !cost.total_base_hours || !cost.taxes) {
      return errorAlert(t("partsCost.empty_submit_alert_message"), submitLaborCost);
    }
    if (!cost.overtime_rate) {
      cost.overtime_rate = 0;
    }
	if (!cost.total_overtime_hours) {
		cost.total_overtime_hours = 0;
	}

    let _cost = { ...cost };
    _cost["base_hourly_rate"] = cost.base_hourly_rate;
    _cost["total_base_hours"] = parseFloat(cost.total_base_hours);
    _cost["overtime_rate"] = cost.overtime_rate;
    _cost["total_overtime_hours"] = parseFloat(cost.total_overtime_hours);
    if (taxOption === "Amount($)") {
      _cost["taxes"] = cost.taxes;
    } else if (taxOption === "Percentage(%)") {
      _cost["taxes"] = parseFloat(
        (
          ((cost.base_hourly_rate * parseFloat(cost.total_base_hours) +
            cost.overtime_rate * parseFloat(cost.total_overtime_hours)) *
            cost.taxes) /
          100
        ).toFixed(2)
      );
    }
    _cost["total_cost"] =
      cost.base_hourly_rate * parseFloat(cost.total_base_hours) +
      cost.overtime_rate * parseFloat(cost.total_overtime_hours) +
      _cost.taxes;
    if (!cost.currency) {
      return errorAlert(t("partsCost.empty_currency_alert_message"), submitLaborCost);
    } else if (typeof cost.currency === "object") {
      _cost["currency"] = cost.currency.code;
    } else if (typeof cost.currency === "string") {
      let findCurrency = listCurrencies.find((currency) => currency.code === cost.currency);
      _cost["currency"] = findCurrency.id;
    }
    if (issues && onAdd) {
      if (issues.length === 1) {
        _cost["issue"] = issues[0].issue_id;
      } else if (issues.length > 1 && !selectedIssue) {
        return errorAlert(t("partsCost.empty_issue_alert_message"), submitLaborCost);
      } else if (issues.length > 1 && selectedIssue) {
        _cost["issue"] = selectedIssue.issue_id;
      }
    }
    if (maintenanceID && onAdd) {
      _cost["maintenance"] = maintenanceID;
    }

    if (onAdd) {
      handleSubmit(_cost, `${Constants.ENDPOINT_PREFIX}/api/v1/Labor/Add/Cost`);
    }
    if (onUpdate) {
      handleSubmit(_cost, `${Constants.ENDPOINT_PREFIX}/api/v1/Labor/Update/Cost`);
    }
  };

  const submitDeletePartsCost = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let deleteCostData = {
      id: deleteCostID.toString(),
    };
    handleSubmit(deleteCostData, `${Constants.ENDPOINT_PREFIX}/api/v1/Labor/Delete/Cost`);
  };

  const handleSubmit = (laborCostData, url) => {
    loadingAlert();
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .post(url, laborCostData, { ...getAuthHeader(), cancelToken: cancelTokenSource.token })
      .then((response) => {
        successAlert(t("laborCost.labor_title"));
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
        setCostDialog(false);
        setDeleteCostDialog(false);
        setCostDataReady(false);
        setTaxOption("Amount($)");
      })
      .catch((error) => {
        errorAlert(error.customErrorMsg, handleSubmit);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  const addCost = () => {
    setOnAdd(true);
    setOnUpdate(false);
    setCost(emptyCost);
    setCostDialog(true);
  };
  const editCost = (currentCost) => {
    setOnAdd(false);
    setOnUpdate(true);
    const tempCost = (({
      id,
      issue,
      maintenance,
      base_hourly_rate,
      total_base_hours,
      overtime_rate,
      total_overtime_hours,
      taxes,
      total_cost,
      currency,
    }) => ({
      id,
      issue,
      maintenance,
      base_hourly_rate,
      total_base_hours,
      overtime_rate,
      total_overtime_hours,
      taxes,
      total_cost,
      currency,
    }))(currentCost);
    setCost({ ...tempCost });
    setCostDialog(true);
  };
  const deleteCost = (cost) => {
    setDeleteCostID(cost.id);
    setDeleteCostDialog(true);
  };
  const hideDialog = () => {
    setOnAdd(false);
    setOnUpdate(false);
    setCostDialog(false);
  };

  const exportCSV = () => {
    dtRef.current.exportCSV();
  };

  const onNumberChange = (value, name) => {
    let _cost = { ...cost };
    _cost[`${name}`] = value;
    setCost(_cost);
  };
  const selectCurrency = (id) => {
    let selected = listCurrencies.find((currency) => currency.id === parseInt(id));
    let selectedCurrency = { name: selected.name, code: selected.id };
    let _cost = { ...cost };
    _cost["currency"] = selectedCurrency;
    setCost(_cost);
  };

  const costDialogFooter = (
    <React.Fragment>
      <Button label="Cancel" icon="pi pi-times" className="p-button-text" onClick={hideDialog} />
      <Button label="Save" icon="pi pi-check" className="p-button-text" onClick={submitLaborCost} />
    </React.Fragment>
  );
  const deleteCostDialogFooter = (
    <React.Fragment>
      <Button
        label={t("general.confirm")}
        icon="pi pi-check"
        className="p-button-text"
        onClick={submitDeletePartsCost}
      />
      <Button
        label={t("general.cancel")}
        icon="pi pi-times"
        onClick={() => setDeleteCostDialog(false)}
      />
    </React.Fragment>
  );

  const leftToolbarTemplate = () => {
    return (
      <div className="d-flex align-items-center">
        <h4 className="p-m-0">{t("laborCost.labor_title")}</h4>
        <Tooltip
          label="cost_action"
          description={t("general.tooltip_cost_action")}
          styles={{ verticalAlign: "super" }}
        />
      </div>
    );
  };
  const rightToolbarTemplate = () => {
    return (
      <div className="d-flex">
        <div className="btn-2">
          <Button
            label={t("laborCost.add_button")}
            icon="pi pi-plus"
            onClick={addCost}
            disabled={request.status === "cancelled" || request.status === "denied"}
          />
        </div>
        {!isMobile && (
          <div className="btn-2 p-ml-3 table-export-btn-addn" style={{ textAlign: "right" }}>
            <Button
              disabled={!laborInfo.length}
              type="button"
              icon="pi pi-external-link"
              label="Export"
              onClick={exportCSV}
            />
          </div>
        )}
      </div>
    );
  };

  const bodyTemplate = (data, header) => {
    return (
      <React.Fragment>
        <span className="p-column-title">{header}</span>
        <span className="p-body-template">{data}</span>
      </React.Fragment>
    );
  };

  const priceBodyTemplate = (price, currency, header) => {
    return (
      <React.Fragment>
        <span className="p-column-title">{header}</span>
        <span className="p-body-template">
          {price.toLocaleString("en-US", { style: "currency", currency: currency })}
        </span>
      </React.Fragment>
    );
  };

  const actionBodyTemplate = (rowData) => {
    return !rowData.submitted_by_vendor ? (
      <div className="p-d-flex p-jc-between w-100 edit-delete">
        {isMobile && <h3>{t("laborCost.labor_details")}</h3>}
        <div className="edit-delete-btn">
          <Button
            icon="pi pi-pencil"
            className="p-button-rounded p-button-edit-cost p-mr-2"
            onClick={() => editCost(rowData)}
          />
          <Button
            icon="pi pi-trash"
            className="p-button-rounded p-button-delete-cost"
            onClick={() => deleteCost(rowData)}
          />
        </div>
      </div>
    ) : null;
  };

  var issueTitle;
  if (onUpdate && issues) {
    const filtedIssue = filterIssue(issues, cost.issue);
    issueTitle = formatIssueTitle(filtedIssue);
  }

  return (
    <div className={`parts-labor-cost-table darkTable ${isMobile && "p-mb-5"}`}>
      <Toolbar className="p-mb-2" left={leftToolbarTemplate} right={rightToolbarTemplate}>
        {""}
      </Toolbar>
      <DataTable
        loading={!costDataReady}
        value={laborInfo}
        ref={dtRef}
        dataKey="id"
        paginator
        rows={isMobile ? 5 : 7}
        selectionMode={"null"}
        resizableColumns
        // rowsPerPageOptions={[5, 10, 15]}
        // paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        // currentPageReportTemplate="Showing {first} to {last} of {totalRecords} costs"
      >
        {isMobile && <Column body={actionBodyTemplate} />}
        <Column
          field="base_hourly_rate"
          header={t("laborCost.base_hourly_rate")}
          body={(rowData) =>
            priceBodyTemplate(
              rowData.base_hourly_rate,
              rowData.currency,
              t("laborCost.base_hourly_rate")
            )
          }
        />
        <Column
          field="total_base_hours"
          header={t("laborCost.total_base_hours")}
          body={(rowData) =>
            bodyTemplate(rowData.total_base_hours, t("laborCost.total_base_hours"))
          }
        />
        <Column
          field="overtime_rate"
          header={t("laborCost.overtime_rate")}
          body={(rowData) =>
            priceBodyTemplate(rowData.overtime_rate, rowData.currency, t("laborCost.overtime_rate"))
          }
        />
        <Column
          field="total_overtime_hours"
          header={t("laborCost.total_overtime_hours")}
          body={(rowData) =>
            bodyTemplate(rowData.total_overtime_hours, t("laborCost.total_overtime_hours"))
          }
        />
        <Column
          field="taxes"
          header={t("laborCost.taxes")}
          body={(rowData) =>
            priceBodyTemplate(rowData.taxes, rowData.currency, t("laborCost.taxes"))
          }
        />
        <Column
          field="currency"
          header={t("laborCost.currency")}
          body={(rowData) => bodyTemplate(rowData.currency, t("laborCost.currency"))}
        />
        <Column
          field="total_cost"
          header={t("laborCost.total_cost")}
          body={(rowData) =>
            priceBodyTemplate(rowData.total_cost, rowData.currency, t("laborCost.total_cost"))
          }
        />
        {!isMobile && <Column body={actionBodyTemplate} header={t("general.cost_action")} />}
      </DataTable>
      {costDialog ? (
        <Dialog
          visible={costDialog}
          style={{ width: "750px" }}
          header={t("laborCost.update")}
          className="p-fluid custom-main-dialog"
          footer={costDialogFooter}
          onHide={hideDialog}
          breakpoints={{ "768px": "90vw" }}
          modal
        >
          {issues ? (
            issues.length > 1 ? (
              onAdd ? (
                <div className="p-field form-tooltip">
                  <label>{t("partsCost.issue")}</label>
                  <Tooltip label={"issue"} description={t("general.tooltip_issue")} />
                  <FormDropdown
                    className="w-100"
                    onChange={(e) => {
                      setSelectedIssue(e);
                    }}
                    options={
                      issues &&
                      issues.map((issue) => ({
                        name: formatIssueTitle(issue),
                        code: issue,
                      }))
                    }
                    plain_dropdown
                    leftStatus
                  />
                </div>
              ) : onUpdate ? (
                <div className="p-field">
                  <label>{t("partsCost.issue")}</label>
                  <p>{issueTitle}</p>
                </div>
              ) : null
            ) : null
          ) : null}
          <div className="p-field txtField-1">
            <label>{t("laborCost.base_hourly_rate")} </label>
            <CustomInputNumber
              value={cost.base_hourly_rate}
              onChange={(v) => onNumberChange(v, "base_hourly_rate")}
              className="w-100"
              mode="decimal"
              minFractionDigits={2}
              maxFractionDigits={2}
              max={2147483646}
              leftStatus
            />
          </div>
          <div className="p-field txtField-1">
            <label>{t("laborCost.total_base_hours")}</label>
            <CustomInputNumber
              value={cost.total_base_hours ? cost.total_base_hours : null}
              onChange={(v) => onNumberChange(v, "total_base_hours")}
              className="w-100"
              mode="decimal"
              minFractionDigits={2}
              maxFractionDigits={2}
              max={2147483646}
              leftStatus
            />
          </div>
          <div className="p-field txtField-1">
            <label>{t("laborCost.overtime_rate")}</label>
            <CustomInputNumber
              value={cost.overtime_rate}
              onChange={(v) => onNumberChange(v, "overtime_rate")}
              className="w-100"
              mode="decimal"
              minFractionDigits={2}
              maxFractionDigits={2}
              max={2147483646}
              leftStatus
            />
          </div>
          <div className="p-field txtField-1">
            <label>{t("laborCost.total_overtime_hours")}</label>
            <CustomInputNumber
              value={cost.total_overtime_hours ? cost.total_overtime_hours : null}
              onChange={(v) => onNumberChange(v, "total_overtime_hours")}
              className="w-100"
              mode="decimal"
              minFractionDigits={2}
              maxFractionDigits={2}
              max={2147483646}
              leftStatus
            />
          </div>
          <div className="p-field txtField-1">
            <div className="p-d-flex p-jc-between tax-button p-mb-2 btn-2 btn-2-select">
              <label className="p-my-auto">{t("laborCost.taxes")}</label>
              <SelectButton
                className="p-ml-2"
                value={taxOption}
                options={taxOptions}
                onChange={(e) => setTaxOption(e.value)}
              />
            </div>
            {taxOption === "Amount($)" ? (
              <CustomInputNumber
                value={cost.taxes}
                onChange={(v) => onNumberChange(v, "taxes")}
                className="w-100"
                mode="decimal"
                minFractionDigits={2}
                maxFractionDigits={2}
                max={2147483646}
                leftStatus
              />
            ) : null}
            {taxOption === "Percentage(%)" ? (
              <CustomInputNumber
                value={cost.taxes}
                onChange={(v) => onNumberChange(v, "taxes")}
                className="w-100"
                min={0}
                max={100}
                suffix=" %"
                leftStatus
              />
            ) : null}
          </div>
          <div className="p-field">
            <label>{t("laborCost.currency")}</label>
            <FormDropdown
              className="w-100"
              defaultValue={defaultCurrency}
              onChange={selectCurrency}
              options={
                listCurrencies &&
                listCurrencies.map((currency) => ({
                  name: currency.name,
                  code: currency.id,
                }))
              }
              loading={!listCurrencies}
              disabled={!listCurrencies}
              dataReady={listCurrencies}
              plain_dropdown
              leftStatus
              reset={"disabled"}
            />
          </div>
        </Dialog>
      ) : null}
      {deleteCostDialog ? (
        <Dialog
          className="custom-main-dialog"
          visible={deleteCostDialog}
          style={{ width: "450px" }}
          header={t("general.confirm")}
          footer={deleteCostDialogFooter}
          onHide={() => setDeleteCostDialog(false)}
          modal
        >
          <div>
            <h5 className="p-d-inline-flex">
              <div className="p-d-flex p-ai-center">
                <i className="pi pi-exclamation-triangle p-mr-2" style={{ fontSize: "1.2rem" }} />
              </div>
              {t("laborCost.delete_confirm_dialog")}
            </h5>
          </div>
        </Dialog>
      ) : null}
    </div>
  );
};

export default LaborCostTable;
