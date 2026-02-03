import { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { useDispatch } from "react-redux";
import { Dialog } from "primereact/dialog";
import { Button } from "primereact/button";
import logo from "./img/logo_lokomotive_white@2x.png";
import eyeclose from "../../images/icons/eye-close.png";
import eyeopen from "../../images/icons/eye-open.png";
import * as Constants from "../../constants";
import { CTRL_AUDIO_PLAY } from "../../redux/types/audioTypes";
import CustomInputText from "../ShareComponents/CustomInputText";
import ErrorBoundary from "../ShareComponents/ErrorBoundary";
import { setAuthHeader, setAgreementHeader } from "../../helpers/Authorization";
import {
  loadingAlert,
  successAlert,
  errorAlert,
  generalErrorAlert,
} from "../ShareComponents/CommonAlert";
import loginVideo from "../../images/background/main_bg.mp4";
import loadingVideo from "./video/login-loading.mp4";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import { getInitInfo } from "../../redux/actions/apiCallAction";
import { AUDIO_DATA_UPDATE } from "../../redux/types/audioTypes";
import { RESET_INIT_DATA } from "../../redux/types/apiCallTypes";
import { RESET_WEATHER_DATA } from "../../redux/types/weatherTypes";
import "../../styles/LoginForm/login.scss";
import "../../styles/dialogStyles.scss";

const LoginForm = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [email, setEmail] = useState("");
  const [forgotpwdEamil, setForgotpwdEamil] = useState("");
  const [password, setPassword] = useState("");
  const [pwdShow, setPwdShow] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [forgotPwdDialog, setForgotPwdDialog] = useState(false); 

  const isMobile = useMediaQuery({ query: `(max-width: 799px)` });

  const getCurrentUrl = () => {
    let url = window.location.href;
    let lastUrlIndex = url.length - 1;
    if (url[lastUrlIndex] === "/") {
      url = url.substr(0, lastUrlIndex);
    }
    return url;
  };

  useEffect(() => {
    dispatch({ type: AUDIO_DATA_UPDATE, sound: false });
    dispatch({ type: RESET_INIT_DATA });
    dispatch({ type: RESET_WEATHER_DATA });
  }, [dispatch]);

  const handleLogin = (event) => {
    event.preventDefault();
    if (email && password) {
      setLoading(true);
      axios
        .post(`${Constants.ENDPOINT_PREFIX}/api-auth/v1/Login`, {
          username: email,
          password: password,
        })
        .then((r) => {
          dispatch(getInitInfo(r.data));
          setAuthHeader(
            r.data.token,
            r.data.token_expiration,
            r.data.detailed_user.role_permissions,
            r.data.user
          );
          setAgreementHeader(r.data.detailed_user.agreement_accepted);
          
          setForgotPwdDialog(false); 
          
          if (r.data.detailed_user.role_permissions.role === "supervisor") {
            window.location.href = "";
          } else {
            window.location.href = "/dashboard";
          }
        })
        .catch((e) => {
          ConsoleHelper(e);
          setLoading(false);
          setError(t("loginForm.incorrect_information"));
        });
    } else if (email) {
      setError(t("loginForm.incorrect_information"));
    } else {
      setError(t("loginForm.info_not_provided"));
    }
  };

  const handleSubmit = () => {
    if (!forgotpwdEamil.match(/.+@.+/)) {
      generalErrorAlert(t("loginForm.email_invalid_msg"));
      dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
    } else {
      loadingAlert();
      axios
        .post(`${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Forgot/Password`, {
          email: forgotpwdEamil,
          redirect_url: getCurrentUrl(),
        })
        .then(() => {
          successAlert();
          dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
          setForgotpwdEamil("");
        })
        .catch((error) => {
          errorAlert(error.customErrorMsg, handleSubmit);
          dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
          ConsoleHelper(error);
        });
    }
  };

  const renderFooter = () => {
    return (
      <Button
        label="Submit"
        icon="pi pi-check"
        onClick={() => {
          setForgotPwdDialog(false);
          handleSubmit();
        }}
        disabled={!forgotpwdEamil}
      />
    );
  };

  return (
    <ErrorBoundary>
      {loading ? (
        <div className="loading-video">
          <video key={loadingVideo} playsInline autoPlay muted loop>
            <source src={loadingVideo} type="video/mp4" />
          </video>
        </div>
      ) : (
        <div className="login-wrapper">
          <video key={loginVideo} playsInline autoPlay muted loop className="login-bg-vid">
            <source src={loginVideo} type="video/mp4" />
          </video>
          <form className="form-signin" onSubmit={handleLogin}>
            <div className="login-logo">
              <img src={logo} alt="" width="240" />
            </div>
            {error && <p className="text-danger">{error}</p>}
            <div className="login-inputs">
              <span className="login-email-text">Email</span>
              <input
                type="email"
                className="login-input-email"
                placeholder={`${
                  isMobile ? "someone@example.com" : t("loginForm.username_placeholder")
                }`}
                required
                onChange={(event) => {
                  setEmail(event.target.value);
                  if (event.nativeEvent.inputType === "insertText") setError("");
                }}
              />
              <span className="login-pass-text">Password</span>
              <div className="pass-wrapper">
                <input
                  type={pwdShow ? "text" : "password"}
                  className="login-input-pass"
                  placeholder={`${isMobile ? "**********" : t("loginForm.password_placeholder")}`}
                  required
                  onChange={(event) => {
                    setPassword(event.target.value);
                    if (event.nativeEvent.inputType === "insertText") setError("");
                  }}
                />
                <div className="login-input-pass-icon" onClick={() => setPwdShow(!pwdShow)}>
                  <img src={pwdShow ? eyeclose : eyeopen} alt="eye-icon" width="13" />
                </div>
              </div>
            </div>
            <div className="login-btns">
              <div className="forgot-btn-container">
                <Button
                  type="button"
                  label={t("loginForm.forgot_password_link")}
                  className="p-button-link forgot-pwd-btn"
                  onClick={() => setForgotPwdDialog(true)}
                />
              </div>
              <div className="signin-btn-container">
                <button className="sign-in-btn" type="submit">
                  {t("loginForm.sign_in_button")}
                </button>
              </div>
            </div>
            <Dialog
              className="custom-main-dialog"
              baseZIndex={1000}
              header={t("loginForm.forgot_password_link")}
              visible={forgotPwdDialog}
              footer={renderFooter}
              onHide={() => {
                setForgotPwdDialog(false);
                setForgotpwdEamil("");
              }}
              style={{ width: "40vw" }}
              breakpoints={{
                "1280px": "40vw",
                "960px": "65vw",
                "768px": "80vw",
                "500px": "90vw",
              }}
            >
              <div className="p-d-flex p-ai-center p-jc-between row">
                <span className={`${isMobile ? "col-12" : "col-6"}`}>
                  {t("loginForm.username_placeholder")}:
                </span>
                <div className={`p-my-1 ${isMobile ? "col-12" : "col-6"}`}>
                  <CustomInputText
                    className="w-100"
                    value={forgotpwdEamil}
                    onChange={setForgotpwdEamil}
                    status={forgotpwdEamil}
                    leftStatus
                  />
                </div>
              </div>
            </Dialog>
          </form>
        </div>
      )}
    </ErrorBoundary>
  );
};

export default LoginForm;