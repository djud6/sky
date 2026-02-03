import React, { useEffect, useState } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import * as Constants from "../../../constants";
import { getAuthHeader } from "../../../helpers/Authorization";
import { Button } from "primereact/button";
import { InputText } from "primereact/inputtext";
import InfoDetails from "./InfoDetails";
import { errorAlert } from "../../ShareComponents/CommonAlert";
import "../../../styles/AccountOptions/ManageAccounts.scss";
import "../../../styles/helpers/button4.scss";

const UserSearch = ({ setUserInfo, forceUpdate }) => {
  const [userEmail, setUserEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const { t } = useTranslation();

  useEffect(() => {
    handleSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [forceUpdate]);

  const handleSearch = () => {
    function validateEmail(email) {
      // eslint-disable-next-line
      const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(email);
    }

    if (userEmail && validateEmail(userEmail)) {
      setLoading(true);
      setUserInfo(null);
      axios
        .post(
          `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Any-Info`,
          {
            email: userEmail,
          },
          getAuthHeader()
        )
        .then((response) => {
          setLoading(false);
          setUserInfo(response.data);
        })
        .catch((error) => {
          setLoading(false);
          errorAlert(error.customErrorMsg, handleSearch);
        });
    } else if (userEmail && !validateEmail(userEmail)) {
      errorAlert(t("accountOptions.email_error_alert_text"), handleSearch);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key.toLowerCase() === "enter") {
      handleSearch();
    }
  };

  return (
    <div className="search-user-bar p-mt-3">
      <span className="title">{t("accountOptions.search_user_title")}</span>
      <div className="search-bar p-mt-2 p-d-flex">
        <div className="p-inputgroup">
          <span className="p-inputgroup-addon">
            <i className="pi pi-user">{""}</i>
          </span>
          <div className="input-box p-input-icon-right w-100">
            {loading && <i className="pi pi-spin pi-spinner" />}
            <InputText
              className="w-100 rounded-0 input-user"
              value={userEmail}
              onChange={(e) => setUserEmail(e.target.value)}
              placeholder={t("accountOptions.search_user_placeholder")}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
          </div>
          <Button
            icon="pi pi-search"
            className="search-button"
            onClick={handleSearch}
            disabled={loading}
          />
        </div>
      </div>
    </div>
  );
};

const EditUser = ({ setMode, updateUserInformation }) => {
  const { t } = useTranslation();
  const [userInfo, setUserInfo] = useState(null);
  const [forceUpdate, setForceUpdate] = useState(Date.now());

  return (
    <div className="op-edit-user">
      <div className="no-style-btn p-mt-1">
        <Button
          label={t("general.back")}
          className="p-button-link"
          icon="pi pi-chevron-left"
          onClick={() => setMode(null)}
        />
      </div>
      <UserSearch setUserInfo={setUserInfo} forceUpdate={forceUpdate} />

   

      {userInfo ? 
        <InfoDetails 
          userInfo={userInfo} 
          setUserInfo={setUserInfo} 
          setForceUpdate={setForceUpdate} 
          updateUserInformation={updateUserInformation}
        /> 
        : null
      }
    </div>
  );
};

export default EditUser;
