import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import * as Constants from "../../constants";
import { getAuthHeader } from "../../helpers/Authorization";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import FormDropdown from "../ShareComponents/Forms/FormDropdown";
import { loadingAlert, successAlert, generalErrorAlert } from "../ShareComponents/CommonAlert";
import ConsoleHelper from "../../helpers/ConsoleHelper";

const UpdateAssetStatus = ({ asset, dialogStatus, setDialogStatus, setForceUpdate }) => {
  const { t } = useTranslation();
  const [selectedStatus, setSelectedStatus] = useState(null);
  const [defaultStatus, setDefaultStatus] = useState(null);
  const statusOptions = [
    {
      name: t("general.status_active"),
      code: "Active",
    },
    {
      name: t("general.status_inoperative"),
      code: "Inoperative",
    },
    {
      name: t("general.status_disposedOf"),
      code: "Disposed-of",
    },
  ];

  useEffect(() => {
    if (asset) {
      const defaultS = statusOptions.find((option) => option.code === asset.status);
      setDefaultStatus(defaultS);
      setSelectedStatus(defaultS);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [asset]);

  const handleStatusUpdate = () => {
    let maintenanceData = {
      VIN: asset.VIN,
      status: selectedStatus.code,
    };
    handleUpdateSubmit(maintenanceData);
  };

  const handleUpdateSubmit = (data) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Set/Status`, data, getAuthHeader())
      .then((res) => {
        successAlert("msg", t("assetDetailPanel.update_status_success_text"));
        setDialogStatus(false);
        setForceUpdate(Date.now());
      })
      .catch((error) => {
        ConsoleHelper(error);
        generalErrorAlert(error.customErrorMsg);
      });
  };

  const renderFooter = () => {
    return (
      <div>
        <Button
          label={t("general.cancel")}
          icon="pi pi-times"
          onClick={() => setDialogStatus(false)}
        />
        <Button
          label={t("general.submit")}
          icon="pi pi-check"
          onClick={handleStatusUpdate}
          disabled={defaultStatus.code === selectedStatus.code}
        />
      </div>
    );
  };

  const selectStatus = (code) => {
    let selected = statusOptions.find((op) => op.code === code);
    setSelectedStatus(selected);
  };

  return (
    <div>
      <Dialog
        className="custom-main-dialog"
        header={t("assetDetailPanel.update_asset_status")}
        visible={dialogStatus}
        onHide={() => setDialogStatus(false)}
        style={{ width: "40vw" }}
        breakpoints={{ "1440px": "40vw", "980px": "55vw", "600px": "90vw" }}
        footer={renderFooter}
      >
        <div className="p-field">
          <label>{t("assetDetailPanel.asset_status")}</label>
          <FormDropdown
            onChange={selectStatus}
            options={statusOptions}
            defaultValue={defaultStatus}
            dataReady={defaultStatus}
            plain_dropdown
            leftStatus
            reset={"disabled"}
          />
        </div>
      </Dialog>
    </div>
  );
};

export default UpdateAssetStatus;
