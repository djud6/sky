import React, { useState } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useSelector } from "react-redux";
import { Button } from "primereact/button";
import { faUserPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import CustomInputText from "../../ShareComponents/CustomInputText";
import CustomInputNumber from "../../ShareComponents/CustomInputNumber";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import MultiSelectDropdown from "../../ShareComponents/Forms/MultiSelectDropdown";
import AdditionalAlert from "../../ShareComponents/AdditionalAlert";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button1.scss";

const AddUserForm = () => {
  const { t } = useTranslation();
  const { listLocations, listBusinessUnits } = useSelector((state) => state.apiCallData);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [costAllowance, setCostAllowance] = useState(null);
  const [selectedRole, setSelectedRole] = useState(null);
  const [selectedBusinessUnit, setSelectedBusinessUnit] = useState(null);
  const [selectedLocations, setSelectedLocations] = useState([]);
  const [dropdownReset, setDropdownReset] = useState(false);
  const [confirmAlert, setConfirmAlert] = useState(false);
  const roles = [
    {
      name: "Operator",
      code: 1,
    },
    {
      name: "Supervisor",
      code: 4,
    },
    {
      name: "Manager",
      code: 2,
    },
    {
      name: "Executive",
      code: 3,
    },
  ];

  const resetForm = () => {
    setFirstName("");
    setLastName("");
    setEmail("");
    setCostAllowance(null);
    setSelectedRole(null);
    setSelectedBusinessUnit(null);
    setSelectedLocations([]);
    setDropdownReset(!dropdownReset);
  };

  const onAddUser = () => {
    setConfirmAlert(false);
    let locArray = [];
    selectedLocations.forEach((loc) => {
      locArray.push(loc.code);
    });

    let data = {
      email: email,
      first_name: firstName,
      last_name: lastName,
      cost_allowance: costAllowance,
      business_unit: selectedBusinessUnit.code,
      role_permissions: selectedRole.code,
      location_ids: locArray,
    };

    handleSubmit(data);
  };

  const handleSubmit = (data) => {
    loadingAlert();
    axios
      .post(
        `
      ${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Create/Account`,
        data,
        getAuthHeader()
      )
      .then((res) => {
        successAlert();
        resetForm();
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        ConsoleHelper(error);
      });
  };

  const selectRole = (id) => {
    let selected = roles.find((role) => role.code === parseInt(id));
    setSelectedRole(selected);
  };

  const selectBusinessUnit = (id) => {
    let selected = listBusinessUnits.find(
      (businessUnit) => businessUnit.business_unit_id === parseInt(id)
    );
    let temp_bu = { name: selected.name, code: selected.business_unit_id };
    setSelectedBusinessUnit(temp_bu);
  };

  const changeLocations = (e) => {
    setSelectedLocations(e.value);
  };

  const onCancelChange = () => {
    setConfirmAlert(false);
  };

  return (
    <div className="add-user-form">
      <div className="title p-mb-3">
        <span>{t("accountOptions.add_user_title")}</span>
      </div>
      <div className="form-fields p-mt-3">
        <div className="field-title">{t("accountOptions.profile_first_name")}</div>
        <CustomInputText
          className="w-100"
          value={firstName}
          onChange={setFirstName}
          keyfilter={"alpha"}
          leftStatus
        />
      </div>
      <div className="form-fields p-my-2">
        <div className="field-title">{t("accountOptions.profile_last_name")}</div>
        <CustomInputText
          className="w-100"
          value={lastName}
          onChange={setLastName}
          keyfilter={"alpha"}
          leftStatus
        />
      </div>
      <div className="form-fields p-my-2">
        <div className="field-title">{t("accountOptions.profile_email")}</div>
        <CustomInputText
          className="w-100"
          value={email}
          onChange={setEmail}
          keyfilter={"email"}
          leftStatus
        />
      </div>
      <div className="form-fields p-my-2">
        <div className="field-title">{t("accountOptions.profile_costAllowance")}</div>
        <CustomInputNumber
          className="w-100"
          value={costAllowance}
          onChange={setCostAllowance}
          keyfilter={"pnum"}
          leftStatus
        />
      </div>
      <div className="form-fields p-my-2">
        <div className="field-title">{t("accountOptions.profile_role")}</div>
        <FormDropdown
          className="w-100"
          onChange={selectRole}
          options={roles}
          reset={dropdownReset}
          plain_dropdown
          leftStatus
        />
      </div>
      <div className="form-fields p-my-2">
        <div className="field-title">{t("accountOptions.profile_business_unit")}</div>
        <FormDropdown
          className="w-100"
          defaultValue={selectedBusinessUnit}
          onChange={selectBusinessUnit}
          options={
            listBusinessUnits &&
            listBusinessUnits.map((businessUnit) => ({
              name: businessUnit.name,
              code: businessUnit.business_unit_id,
            }))
          }
          loading={!listBusinessUnits}
          disabled={!listBusinessUnits}
          dataReady={listBusinessUnits}
          reset={dropdownReset}
          plain_dropdown
          leftStatus
        />
      </div>
      <div className="form-fields p-my-2">
        <div className="field-title">{t("accountOptions.profile_location")}</div>
        <React.Fragment>
          {listLocations ? (
            <div className="custom-multi-select">
              <MultiSelectDropdown
                classNames="w-100"
                value={selectedLocations}
                options={
                  listLocations &&
                  listLocations.map((location) => ({
                    name: location.location_name,
                    code: location.location_id,
                  }))
                }
                onChange={changeLocations}
                leftStatus
              />
            </div>
          ) : (
            <CustomInputText className="w-100" placeholder={"Loading..."} disabled leftStatus />
          )}
        </React.Fragment>
        <div className="p-mt-4 btn-1 p-d-flex p-jc-end">
          <Button
            label={t("general.submit")}
            disabled={
              !firstName ||
              !lastName ||
              !email ||
              !costAllowance ||
              !selectedRole ||
              !selectedBusinessUnit ||
              !selectedLocations.length
            }
            onClick={() => setConfirmAlert(true)}
          />
        </div>
      </div>
      {confirmAlert && (
        <AdditionalAlert
          title={t("accountOptions.add_user_warning_title")}
          text={t("accountOptions.add_user_warning_text")}
          warningMsg={t("accountOptions.add_user_warning_sub_text")}
          confirmBtn={t("additionalAlert.confirm_yes")}
          cancelBtn={t("additionalAlert.cancel_no")}
          onConfirm={onAddUser}
          onCancel={onCancelChange}
        />
      )}
    </div>
  );
};

const AddUser = ({ setMode }) => {
  const { t } = useTranslation();

  return (
    <div className="op-add-user">
      <div className="no-style-btn p-mt-1">
        <Button
          label={t("general.back")}
          className="p-button-link"
          icon="pi pi-chevron-left"
          onClick={() => setMode(null)}
        />
      </div>
      <div className="add-user-container">
        <div className="left-container">
          <FontAwesomeIcon icon={faUserPlus} color="white" />
        </div>
        <div className="right-container">
          <AddUserForm />
        </div>
      </div>
    </div>
  );
};

export default AddUser;
