import React, { useState, useEffect } from "react";
import axios from "axios";
import swal from "sweetalert";
import { useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import * as Constants from "../../constants";
import { getAuthHeader, logout } from "../../helpers/Authorization";
import CustomInputText from "./CustomInputText";
import { loadingAlert, generalErrorAlert } from "./CommonAlert";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import "../../styles/helpers/button1.scss";
import "../../styles/ShareComponents/FirstTimePwd.scss";

const FirstTimePwd = () => {
  const { t } = useTranslation();
  const { userInfo } = useSelector((state) => state.apiCallData);
  const [password, setPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [pwdError, setPwdError] = useState(true);
  const [matchingError, setMatchingError] = useState(false);
  const [changeSuccess, setChangeSuccess] = useState(false);

  useEffect(() => {
    if (!newPassword || !confirmPassword || !password) {
      setPwdError(true);
    } else if (newPassword && confirmPassword && newPassword !== confirmPassword) {
      setMatchingError(true);
      setPwdError(true);
    } else {
      setMatchingError(false);
      setPwdError(false);
    }
  }, [password, newPassword, confirmPassword]);

  const validatePassword = () => {
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api-auth/v1/Login`, {
        username: userInfo.user.email,
        password: password,
      })
      .then((r) => {
        handlePasswordChange();
      })
      .catch((e) => {
        ConsoleHelper(e);
        generalErrorAlert(t("accountOptions.wrong_password"));
      });
  };

  const handlePasswordChange = () => {
    const authHeader = getAuthHeader();
    axios
      .post(
        `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Update/Password`,
        { password: newPassword },
        authHeader
      )
      .then((r) => {
        setChangeSuccess(true);
        successAlert();
      })
      .catch((err) => {
        ConsoleHelper(err);
        generalErrorAlert(err.customErrorMsg);
      });
  };

  const successAlert = () => {
    return swal({
      title: t("general.success"),
      text: t("accountOptions.password_update_success"),
      icon: "success",
      buttons: { return: t("general.confirm") },
    }).then((value) => {
      switch (value) {
        case "return":
          logout();
          break;
        default:
          logout();
      }
    });
  };

  return (
    <div className="first-password-overlay opac">
      {!changeSuccess ? (
        <div className="password-section">
          <div className="title">
            <h4>Reset Password</h4>
          </div>
          <div className="p-mt-3">
            <label>{t("accountOptions.old_password_label")}</label>
            <CustomInputText
              required
              leftStatus
              type="password"
              placeholder="Password"
              onChange={setPassword}
            />
          </div>
          <div className="p-mt-3">
            <label>{t("accountOptions.new_password_label")}</label>
            <CustomInputText
              classnames={`${matchingError ? "is-invalid" : ""}`}
              required
              leftStatus
              type="password"
              placeholder="New Password"
              onChange={setNewPassword}
            />
          </div>
          <div className="p-mt-3 p-mb-5">
            <label>{t("accountOptions.new_password_again_label")}</label>
            <CustomInputText
              classnames={`${matchingError ? "is-invalid" : ""}`}
              required
              leftStatus
              type="password"
              placeholder="Confirm Password"
              onChange={setConfirmPassword}
            />
          </div>
          <div className="btn-1 p-d-flex p-jc-end p-mb-3">
            <Button onClick={validatePassword} disabled={pwdError}>
              {t("accountOptions.submit_button_label")}
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default FirstTimePwd;
