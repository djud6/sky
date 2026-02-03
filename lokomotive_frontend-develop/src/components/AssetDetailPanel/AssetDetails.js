import React, { useState, useEffect } from "react";
import { useHistory } from "react-router-dom";
import axios from "axios";
import { getAuthHeader, getRolePermissions } from "../../helpers/Authorization";
import * as Constants from "../../constants";
import VehicleTable from "./VehicleTable";
import IssuesTab from "./IssuesTab";
import RepairsTab from "./RepairsTab";
import MaintenanceTab from "./MaintenanceTab";
import IncidentsTab from "./IncidentsTab";
import TransfersTab from "./TransfersTab";
import DowntimeTab from "./DowntimeTab";
import DocumentTab from "./DocumentTab";
import CostsTab from "./CostsTab";
import DatePicker from "../ShareComponents/DatePicker";
import FormDropdown from "../ShareComponents/Forms/FormDropdown";
import FullWidthSkeleton from "../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import { loadingAlert, successAlert, generalErrorAlert } from "../ShareComponents/CommonAlert";
import { useTranslation } from "react-i18next";
import { TabView, TabPanel } from "primereact/tabview";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import { InputText } from "primereact/inputtext";
import AssetLogTab from "./AssetLogTab";
import AssetTransferBtn from "../ShareComponents/helpers/AssetTransferBtn";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import "../../styles/dialogStyles.scss";

const DetailEditBtn = ({ vehicle, setDataReady, setForceUpdate }) => {
  const { t } = useTranslation();
  const [editDialogStatus, setEditDialogStatus] = useState(false);
  const [manufacturerDate, setManufacturerDate] = useState(
    vehicle.date_of_manufacture ? new Date(vehicle.date_of_manufacture + "T12:00:00.000000Z") : null
  );
  const [inServiceDate, setInServiceDate] = useState(
    vehicle.date_in_service ? new Date(vehicle.date_in_service + "T12:00:00.000000Z") : null
  );
  const [assetInfo, setAssetInfo] = useState({
    license_plate: vehicle.license_plate || "",
    unit_number: vehicle.unit_number || "",
    mileage: vehicle.mileage.toString(),
    hours: vehicle.hours.toString(),
    replacement_mileage: vehicle.replacement_mileage.toString(),
    replacement_hours: vehicle.replacement_hours.toString(),
    ...(vehicle.load_capacity
      ? { load_capacity: vehicle.load_capacity.toString() }
      : { load_capacity: "" }),
    engine: vehicle.engine || "",
    fuel: vehicle.fuel || "",
    mileage_unit: vehicle.mileage_unit,
  });
  const mileageUnits = [
    { name: "km", code: "km" },
    { name: "mi", code: "mi" },
  ];

  useEffect(() => {
    if (!editDialogStatus) {
      setAssetInfo({
        license_plate: vehicle.license_plate || "",
        unit_number: vehicle.unit_number || "",
        mileage: vehicle.mileage.toString(),
        hours: vehicle.hours.toString(),
        replacement_mileage: vehicle.replacement_mileage.toString(),
        replacement_hours: vehicle.replacement_hours.toString(),
        ...(vehicle.load_capacity
          ? { load_capacity: vehicle.load_capacity.toString() }
          : { load_capacity: "" }),
        engine: vehicle.engine || "",
        fuel: vehicle.fuel || "",
        mileage_unit: vehicle.mileage_unit,
      });
      setManufacturerDate(
        vehicle.date_of_manufacture
          ? new Date(vehicle.date_of_manufacture + "T12:00:00.000000Z")
          : null
      );
      setInServiceDate(
        vehicle.date_in_service ? new Date(vehicle.date_in_service + "T12:00:00.000000Z") : null
      );
    }
    // eslint-disable-next-line
  }, [editDialogStatus]);

  const handleAssetUpdate = () => {
    let assetUpdateData = {
      VIN: vehicle.VIN,
      ...(assetInfo.license_plate && { license_plate: assetInfo.license_plate }),
      ...(assetInfo.unit_number && { unit_number: assetInfo.unit_number }),
      ...((vehicle.hours_or_mileage.toLowerCase() === "mileage" ||
        vehicle.hours_or_mileage.toLowerCase() === "both") &&
        assetInfo.mileage && { mileage: assetInfo.mileage }),
      ...((vehicle.hours_or_mileage.toLowerCase() === "hours" ||
        vehicle.hours_or_mileage.toLowerCase() === "both") &&
        assetInfo.hours && { hours: assetInfo.hours }),
      ...(assetInfo.replacement_mileage && { replacement_mileage: assetInfo.replacement_mileage }),
      ...(assetInfo.replacement_hours && { replacement_hours: assetInfo.replacement_hours }),
      ...(assetInfo.load_capacity && { load_capacity: assetInfo.load_capacity }),
      ...(assetInfo.engine && { engine: assetInfo.engine }),
      ...(assetInfo.fuel && { fuel: assetInfo.fuel }),
      ...(assetInfo.mileage_unit && { mileage_unit: assetInfo.mileage_unit }),
      ...(manufacturerDate && {
        date_of_manufacture: manufacturerDate.toISOString().split("T")[0],
      }),
      ...(inServiceDate && { date_in_service: inServiceDate.toISOString().split("T")[0] }),
    };
    handleUpdateSubmit(assetUpdateData);
  };

  const handleUpdateSubmit = (data) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Update`, data, getAuthHeader())
      .then((res) => {
        successAlert(t("updateAsset.update_asset"));
        setEditDialogStatus(false);
        setForceUpdate(Date.now());
        if (setDataReady) setDataReady(false);
      })
      .catch((error) => {
        ConsoleHelper(error);
        generalErrorAlert(error.customErrorMsg);
      });
  };

  const selectMileageUnit = (code) => {
    let selected = mileageUnits.find((v) => v.code === code);
    setAssetInfo({ ...assetInfo, mileage_unit: selected.name });
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label="Cancel"
          icon="pi pi-times"
          className="p-button-text"
          onClick={() => setEditDialogStatus(false)}
        />
        <Button label="Confirm" icon="pi pi-check" onClick={handleAssetUpdate} />
      </div>
    );
  };

  return (
    <React.Fragment>
      <Button
        icon="pi pi-pencil"
        className="p-button-rounded p-button-warning p-ml-2"
        onClick={() => setEditDialogStatus(true)}
      />
      <Dialog
        className="custom-main-dialog"
        header={t("updateAsset.update_asset_title")}
        visible={editDialogStatus}
        onHide={() => setEditDialogStatus(false)}
        style={{ width: "50vw" }}
        breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
        footer={renderFooter()}
      >
        <div className="p-field">
          <label className="h6">{t("fleetPanel.license_plate_label")}</label>
          <InputText
            className="w-100"
            value={assetInfo["license_plate"]}
            onChange={(e) => setAssetInfo({ ...assetInfo, license_plate: e.target.value })}
          />
        </div>
        <div className="p-field">
          <label className="h6">{t("updateAsset.unit_number_label")}</label>
          <InputText
            className="w-100"
            value={assetInfo["unit_number"]}
            onChange={(e) => setAssetInfo({ ...assetInfo, unit_number: e.target.value })}
          />
        </div>
        {vehicle.hours_or_mileage.toLowerCase() === "mileage" ||
        vehicle.hours_or_mileage.toLowerCase() === "both" ? (
          <div className="p-field">
            <label className="h6">{t("general.mileage")}</label>
            <InputText
              className="w-100"
              value={assetInfo["mileage"]}
              onChange={(e) => setAssetInfo({ ...assetInfo, mileage: e.target.value })}
              keyfilter={/^\d*\.?\d*$/}
            />
          </div>
        ) : null}
        {vehicle.hours_or_mileage.toLowerCase() === "hours" ||
        vehicle.hours_or_mileage.toLowerCase() === "both" ? (
          <div className="p-field">
            <label className="h6">{t("general.hours")}</label>
            <InputText
              className="w-100"
              value={assetInfo["hours"]}
              onChange={(e) => setAssetInfo({ ...assetInfo, hours: e.target.value })}
              keyfilter={/^\d*\.?\d*$/}
            />
          </div>
        ) : null}
        <div className="p-field">
          <label className="h6">{t("updateAsset.replacement_mileage")}</label>
          <InputText
            className="w-100"
            value={assetInfo["replacement_mileage"]}
            onChange={(e) => setAssetInfo({ ...assetInfo, replacement_mileage: e.target.value })}
            keyfilter={/^\d*\.?\d*$/}
          />
        </div>
        <div className="p-field">
          <label className="h6">{t("updateAsset.replacement_hours")}</label>
          <InputText
            className="w-100"
            value={assetInfo["replacement_hours"]}
            onChange={(e) => setAssetInfo({ ...assetInfo, replacement_hours: e.target.value })}
            keyfilter={/^\d*\.?\d*$/}
          />
        </div>
        <div className="p-field">
          <label className="h6">{t("updateAsset.load_capacity")}</label>
          <InputText
            className="w-100"
            value={assetInfo["load_capacity"]}
            onChange={(e) => setAssetInfo({ ...assetInfo, load_capacity: e.target.value })}
            keyfilter={/^\d*\.?\d*$/}
          />
        </div>
        <div className="p-field">
          <label className="h6">{t("updateAsset.engine")}</label>
          <InputText
            className="w-100"
            value={assetInfo["engine"]}
            onChange={(e) => setAssetInfo({ ...assetInfo, engine: e.target.value })}
          />
        </div>
        <div className="p-field">
          <label className="h6">{t("general.fuel")}</label>
          <InputText
            className="w-100"
            value={assetInfo["fuel"]}
            onChange={(e) => setAssetInfo({ ...assetInfo, fuel: e.target.value })}
          />
        </div>
        <div className="p-field">
          <label>{t("updateAsset.mileage_unit")}</label>
          <FormDropdown
            onChange={selectMileageUnit}
            options={mileageUnits}
            loading={!mileageUnits}
            disabled={!mileageUnits}
            dataReady
            plain_dropdown
          />
        </div>
        <div className="p-field">
          <label>{t("updateAsset.date_of_manufacture")}</label>
          <div className="p-fluid p-grid p-formgrid">
            <div className="p-col-12">
              <DatePicker onChange={setManufacturerDate} initialDate={manufacturerDate} />
            </div>
          </div>
        </div>
        <div className="p-field">
          <label>{t("updateAsset.date_in_service")}</label>
          <div className="p-fluid p-grid p-formgrid">
            <div className="p-col-12">
              <DatePicker onChange={setInServiceDate} initialDate={inServiceDate} />
            </div>
          </div>
        </div>
      </Dialog>
    </React.Fragment>
  );
};

const AssetDetails = ({ vin, setDataReady }) => {
  let history = useHistory();
  let [vehicle, setVehicle] = useState(null);
  let [isOperator, setIsOperator] = useState(false);
  let [roleReady, setRoleReady] = useState(false);
  let [vehicleReady, setVehicleReady] = useState(false);
  let [forceUpdate, setForceUpdate] = useState(Date.now());
  const { t } = useTranslation();

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    const rolePermissions = getRolePermissions();
    setVehicleReady(false);
    if (rolePermissions.role.toLowerCase() === "operator") {
      setIsOperator(true);
      setRoleReady(true);
    } else {
      setRoleReady(true);
    }
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetsByLast/VIN/UnitNumber/${vin}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((res) => {
        setVehicle(res.data);
        setVehicleReady(true);
      })
      .catch((error) => {
        ConsoleHelper(error);
      });
    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [vin, forceUpdate]); // @TODO: Please check. Im not sure if this is the right business logic. This effect will only run if the vin changes.

  const handleNewAssetOrder = (e) => {
    e.preventDefault();
    history.push({
      pathname: `/assets/asset-request`,
      state: { vehicle: vehicle },
    });
  };

  return (
    <div>
      <h1>
        <div className="p-d-flex p-flex-wrap p-jc-between p-ai-center p-mx-3 p-mb-3">
          <div className="p-d-flex p-ai-center">
            {t("assetDetailPanel.page_title", { vin: vin })}
            {vehicleReady && !isOperator ? (
              <DetailEditBtn
                vehicle={vehicle[0]}
                setDataReady={setDataReady}
                setForceUpdate={setForceUpdate}
              />
            ) : null}
          </div>
          {vehicleReady && !isOperator ? (
            <div className="p-d-flex p-ai-center">
              <Button
                icon="pi pi-plus-circle"
                label={t("assetDetailPanel.order_same_asset")}
                className="p-button-outlined p-button-secondary p-mx-3"
                onClick={handleNewAssetOrder}
              />
              {vehicle[0].status !== "Inoperative" && !vehicle[0].has_transfer ? (
                <AssetTransferBtn vin={vin} asset={vehicle} />
              ) : null}
            </div>
          ) : null}
        </div>
      </h1>
      {vehicleReady ? (
        <React.Fragment>
          <div className="row">
            <div className="col">
              <VehicleTable vehicle={vehicle} roleReady={roleReady} />
            </div>
          </div>
          <div className="row">
            <div className="col">
              {isOperator ? (
                <TabView>
                  <TabPanel header="ISSUES">
                    <IssuesTab vin={vin} />
                  </TabPanel>
                </TabView>
              ) : (
                <TabView>
                  <TabPanel header="ASSET LOG">
                    <AssetLogTab vin={vin} />
                  </TabPanel>
                  <TabPanel header="ISSUES">
                    <IssuesTab vin={vin} />
                  </TabPanel>
                  <TabPanel header="REPAIRS">
                    <RepairsTab vin={vin} />
                  </TabPanel>
                  <TabPanel header="MAINTENANCE">
                    <MaintenanceTab vin={vin} />
                  </TabPanel>
                  <TabPanel header="INCIDENTS">
                    <IncidentsTab vin={vin} />
                  </TabPanel>
                  <TabPanel header="DOWNTIME">
                    <DowntimeTab vin={vin} />
                  </TabPanel>
                  <TabPanel header="TRANSFERS">
                    <TransfersTab vin={vin} asset={vehicle} />
                  </TabPanel>
                  <TabPanel header="DOCUMENTS">
                    <DocumentTab vin={vin} />
                  </TabPanel>
                  <TabPanel header="COSTS">
                    <CostsTab vin={vin} />
                  </TabPanel>
                </TabView>
              )}
            </div>
          </div>
        </React.Fragment>
      ) : (
        <React.Fragment>
          <FullWidthSkeleton height={"500px"} />
        </React.Fragment>
      )}
    </div>
  );
};

export default AssetDetails;
