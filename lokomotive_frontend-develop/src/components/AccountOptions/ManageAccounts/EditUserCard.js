import React, { useEffect, useState } from "react";
import axios from "axios";
import { useDispatch, useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { faTimesCircle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { getAuthHeader } from "../../../helpers/Authorization";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import { Button } from "primereact/button";
import { InputText } from "primereact/inputtext";
import { InputSwitch } from "primereact/inputswitch";
import GeneralBadge from "../../ShareComponents/GeneralBadge";
import MultiSelectDropdown from "../../ShareComponents/Forms/MultiSelectDropdown";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button1.scss";

const EditUserCard = ({ userInfo, setOnEditMode, setForceUpdate, updateUserInformation }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { listLocations, listBusinessUnits } = useSelector((state) => state.apiCallData);
  const [dataReady, setDataReady] = useState(false);
  const [firstName, setFirstName] = useState(userInfo.user.first_name);
  const [lastName, setLastName] = useState(userInfo.user.last_name);
  const [costAllowance, setCostAllowance] = useState(userInfo.detailed_user.cost_allowance);
  const [isSuperUser, setIsSuperUser] = useState(userInfo.user.is_superuser);
  const [isActive, setIsActive] = useState(userInfo.user.is_active);
  const [selectedBusinessUnit, setSelectedBusinessUnit] = useState(null);
  const [selectedLocations, setSelectedLocations] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);

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

  useEffect(() => {
    setDataReady(false);
    setSelectedBusinessUnit(null);
    setSelectedLocations([]);
    setSelectedRole(null);

    let findRole = roles.find(
      (role) => role.name.toLowerCase() === userInfo.detailed_user.role_permissions.role
    );
    setSelectedRole(findRole);

    if (
      listBusinessUnits &&
      listLocations &&
      (!selectedBusinessUnit || selectedLocations.length === 0)
    ) {
      if (!selectedBusinessUnit && userInfo.detailed_user.business_unit) {
        let findBusinessU = listBusinessUnits.find(
          (businessU) => businessU.name === userInfo.detailed_user.business_unit.name
        );
        let reformatBusinessU = {
          name: findBusinessU.name,
          code: findBusinessU.business_unit_id,
        };
        setSelectedBusinessUnit(reformatBusinessU);
      }
      if (selectedLocations.length === 0) {
        let tempLocationList = [];
        userInfo.detailed_user.location.forEach((location) => {
          let findlocation = listLocations.find((l) => l.location_name === location.location_name);
          let reformatLocation = {
            name: findlocation.location_name,
            code: findlocation.location_id,
          };
          tempLocationList.push(reformatLocation);
        });
        setSelectedLocations(tempLocationList);
      }
      setDataReady(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selectBusinessUnit = (id) => {
    let selected = listBusinessUnits.find(
      (businessUnit) => businessUnit.business_unit_id === parseInt(id)
    );
    let selectedBusinessUnit = { name: selected.name, code: selected.business_unit_id };
    setSelectedBusinessUnit(selectedBusinessUnit);
  };

  const selectRole = (id) => {
    let selected = roles.find((role) => role.code === parseInt(id));
    setSelectedRole(selected);
  };

  const changeLocations = (e) => {
    setSelectedLocations(e.value);
  };

  const handleSubmit = (data) => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Edit/AnyAccount`, data, getAuthHeader())
      .then((res) => {
        successAlert();
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
        setForceUpdate(Date.now());
      })
      .finally(() => {
        updateUserInformation();
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
        ConsoleHelper(error);
      });
  };

  const handleChange = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let locationArray = selectedLocations.map((location) => location.code);
    let data = {
      user_id: userInfo.user.id,
      email: userInfo.user.email,
      first_name: firstName,
      last_name: lastName,
      is_superuser: isSuperUser,
      cost_allowance: parseInt(costAllowance),
      location_ids: locationArray,
      role_permissions: selectedRole.code,
      business_unit: selectedBusinessUnit.code,
      is_staff: userInfo.user.is_staff,
      is_active: isActive,
    };
    handleSubmit(data);
  };
  const handleInputChange = (event) => {
    const inputVal = event.target.value;

    // Remove any non-digit characters except dots
    const cleanedValue = inputVal.replace(/[^\d.]/g, "");

    setCostAllowance(cleanedValue);
  };
  const formattedAmount = parseFloat(costAllowance).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
  return (
    <React.Fragment>
      <div className="title p-d-flex p-jc-between p-ai-center p-mb-3">
        <span>{t("accountOptions.edit_card_title")}</span>
        <div className="close-btn" onClick={() => setOnEditMode(false)}>
          <FontAwesomeIcon icon={faTimesCircle} color="white" />
        </div>
      </div>
      <div className="edit-fields">
        <div className="field-title">{t("accountOptions.profile_email")}</div>
        <div className="field-value">{userInfo.user.email}</div>
      </div>
      <hr />
      <div className="edit-fields p-mt-3">
        <div className="field-title">{t("accountOptions.profile_first_name")}</div>
        <div className="field-value text-only">
          <InputText
            className="w-100"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
          />
        </div>
      </div>
      <div className="edit-fields p-my-2">
        <div className="field-title">{t("accountOptions.profile_last_name")}</div>
        <div className="field-value text-only">
          <InputText
            className="w-100"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
          />
        </div>
      </div>
      <div className="edit-fields p-my-2">
        <div className="field-title">{t("accountOptions.profile_role")}</div>
        <div className="field-value">
          <FormDropdown
            className="w-100"
            defaultValue={selectedRole}
            onChange={selectRole}
            options={roles}
            loading={!dataReady}
            disabled={!roles || !dataReady}
            dataReady={dataReady}
            plain_dropdown
          />
        </div>
      </div>
      <div className="edit-fields p-my-2">
        <div className="field-title">{t("accountOptions.profile_business_unit")}</div>
        <div className="field-value">
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
            loading={!dataReady}
            disabled={!listBusinessUnits || !dataReady}
            dataReady={dataReady}
            plain_dropdown
          />
        </div>
      </div>
      <div className="edit-fields p-my-2">
        <div className="field-title">{t("accountOptions.profile_costAllowance")}</div>
        <div
          style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
          className="field-value text-only"
        >
          <span className="mr-2 text-gray-600">$</span>
          <InputText
            type="text"
            className="border rounded p-2 w-40"
            value={costAllowance ? parseFloat(costAllowance).toLocaleString() : 0}
            onChange={handleInputChange}
            placeholder="0.00"
          />
        </div>
      </div>
      <div className="edit-fields p-my-2">
        <div className="field-title">{t("accountOptions.profile_location")}</div>
        <div className="field-value text-only">
          {dataReady ? (
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
                disabled={listLocations ? false : true}
              />
            </div>
          ) : (
            <InputText className="w-100" placeholder={"Loading..."} disabled />
          )}
        </div>
      </div>
      <hr />
      <div className="edit-fields p-my-3">
        <div className="field-title">{t("accountOptions.profile_superuser")}</div>
        <div className="field-value p-d-flex p-ai-center">
          <InputSwitch
            checked={isSuperUser}
            onChange={(e) => {
              setIsSuperUser(e.value);
            }}
          />
          <div className="p-ml-3 p-d-flex p-ai-center">
            {isSuperUser ? (
              <GeneralBadge data={t("accountOptions.super_user")} colorTheme={"badge-success"} />
            ) : (
              <GeneralBadge data={t("accountOptions.normal_user")} colorTheme={"badge-secondary"} />
            )}
          </div>
        </div>
      </div>
      <div className="edit-fields p-my-2">
        <div className="field-title">{t("accountOptions.profile_active")}</div>
        <div className="field-value p-d-flex p-ai-center">
          <InputSwitch
            checked={isActive}
            onChange={(e) => {
              setIsActive(e.value);
            }}
          />
          <div className="p-ml-3 p-d-flex p-ai-center">
            {isActive ? (
              <GeneralBadge
                data={t("accountOptions.account_status_active")}
                colorTheme={"badge-success"}
              />
            ) : (
              <GeneralBadge
                data={t("accountOptions.account_status_inactive")}
                colorTheme={"badge-danger"}
              />
            )}
          </div>
        </div>
      </div>
      <div className="btn-1 p-d-flex p-jc-end p-mt-3">
        <Button
          style={{ width: "120px" }}
          label={t("general.submit")}
          onClick={handleChange}
          disabled={selectedLocations.length === 0 || !selectedRole || !selectedBusinessUnit}
        />
      </div>
    </React.Fragment>
  );
};

export default EditUserCard;
