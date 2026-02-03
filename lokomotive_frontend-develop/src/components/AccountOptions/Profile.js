import React, { useEffect, useState } from "react";
import axios from "axios";
import swal from "sweetalert";
import moment from "moment";
import { useDispatch, useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Dialog } from "primereact/dialog";
import { Button } from "primereact/button";
import { faUser } from "@fortawesome/free-solid-svg-icons";
import * as Constants from "../../constants";
import { CTRL_AUDIO_PLAY } from "../../redux/types/audioTypes";
import { getUserInformation } from "../../redux/actions/apiCallAction";
import { getAuthHeader, logout } from "../../helpers/Authorization";
import { capitalize } from "../../helpers/helperFunctions";
import PanelHeader from "../ShareComponents/helpers/PanelHeader";
import Spinner from "../ShareComponents/Spinner";
import ShowMore from "../ShareComponents/ShowMore";
import InfoCard from "../ShareComponents/InfoCard";
import { loadingAlert } from "../ShareComponents/CommonAlert";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import { ImageDialog, PasswordDialog, ConfigDialog } from "./DialogContent";
import { successAlert, generalErrorAlert as errorAlert } from "../ShareComponents/CommonAlert";
import "./AccountOptions.scss";
import "../../styles/dialogStyles.scss";
import "../../styles/helpers/fileInput.scss";
import "../../styles/AccountOptions/profile.scss";

const ProfileDetailsCard = ({ userInfo }) => {
  const { t } = useTranslation();

  const createLocations = (locations) => {
    let finalLocations = "";
    locations.forEach((singleLocation) => {
      finalLocations += singleLocation.location_name + ", ";
    });
    return finalLocations.substr(0, finalLocations.length - 2);
  };

  const ProfileRow = ({ title, info }) => {
    return (
      <div className="profile-item-wrapper">
        <div className="p-d-flex p-flex-wrap p-jc-between">
          <div className="profile-item-title">{title}:</div>
          <div className="profile-item-value">{info || "N/A"}</div>
        </div>
        <hr />
      </div>
    );
  };

  return (
    <InfoCard>
      <div className="d-flex flex-row no-gutters pt-2 pb-2 justify-content-start fleet-card-title">
        <h5 className="chart-card-title font-weight-bold">{t("accountOptions.account_details")}</h5>
      </div>
      <ProfileRow title={t("accountOptions.profile_first_name")} info={userInfo.firstName} />
      <ProfileRow title={t("accountOptions.profile_last_name")} info={userInfo.lastName} />
      <ProfileRow title={t("accountOptions.profile_email")} info={userInfo.email} />
      <ProfileRow title={t("accountOptions.profile_company")} info={userInfo.company} />
      <ProfileRow title={t("accountOptions.profile_business_unit")} info={userInfo.businessUnit} />
      <ProfileRow
        title={t("accountOptions.profile_location")}
        info={
          userInfo.location ? (
            <ShowMore text={createLocations(userInfo.location)} limit={35} excerpt={35} />
          ) : (
            "N/A"
          )
        }
      />
      <ProfileRow
        title={t("accountOptions.profile_cost_allowance")}
        info={userInfo.costAllowance}
      />
      <ProfileRow title={t("accountOptions.profile_join_date")} info={userInfo.joinDate} />
      <ProfileRow title={t("accountOptions.profile_last_login")} info={userInfo.lastLogin} />
    </InfoCard>
  );
};

const ProfileModificationCard = ({ userInfo, setDataReady }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const [changeImageDialog, setChangeImageDialog] = useState(false);
  const [changeConfigDialog, setChangeConfigDialog] = useState(false);
  const [changePwdDialog, setChangePwdDialog] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(false);
  const [selectedFile, setSelectedFile] = useState([]);
  const [fileLoading, setFileLoading] = useState(false);
  const [password, setPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitPassword, setSubmitPassword] = useState(false);
  const [currentCategory, setCurrentCategory] = useState("");
  const [configurations, setConfigurations] = useState(null);
  const [currentConfigurations, setCurrentConfigurations] = useState(null);

  const passwordSuccessAlert = () => {
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

  const validatePassword = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    setSubmitPassword(true);
    if (newPassword === confirmPassword && newPassword && confirmPassword && password) {
      loadingAlert();
      axios
        .post(`${Constants.ENDPOINT_PREFIX}/api-auth/v1/Login`, {
          username: userInfo.email,
          password: password,
        })
        .then((_) => {
          handlePwdSubmission();
        })
        .catch((err) => {
          ConsoleHelper(err);
          errorAlert(err.customErrorMsg);
        });
    }
  };

  const handlePwdSubmission = () => {
    const authHeader = getAuthHeader();
    axios
      .post(
        `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Update/Password`,
        { password: newPassword },
        authHeader
      )
      .then((_) => {
        setChangePwdDialog(false);
        passwordSuccessAlert();
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
      })
      .catch((err) => {
        ConsoleHelper(err);
        errorAlert(err.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  const handleImageSubmission = () => {
    setUploadStatus(true);
    const imageData = new FormData();
    imageData.append("image", selectedFile[0]);
    axios
      .post(
        `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Update/Image`,
        imageData,
        getAuthHeader()
      )
      .then((_) => {
        setUploadStatus(false);
        setDataReady(false);
        setChangeImageDialog(false);
      })
      .catch((error) => {
        errorAlert(error.customErrorMsg);
        setUploadStatus(false);
        ConsoleHelper(error);
      });
  };

  const footerImg = (
    <div>
      <Button
        onClick={handleImageSubmission}
        className="btn btn-secondary mt-4"
        disabled={selectedFile.length === 0 || uploadStatus || fileLoading}
      >
        {!uploadStatus ? (
          t("accountOptions.submit_button_label")
        ) : (
          <div>
            <span
              className="spinner-border spinner-border-sm mr-1"
              role="status"
              aria-hidden="true"
            />
            {t("accountOptions.uploading_status_label")}
          </div>
        )}
      </Button>
    </div>
  );

  let matchError =
    newPassword.length > 0 && confirmPassword.length > 0 && newPassword !== confirmPassword;
  let emptyError = !newPassword || !confirmPassword || !password;

  const footerPwd = (
    <div>
      <Button
        onClick={validatePassword}
        className="btn btn-secondary mt-4"
        disabled={submitPassword && (matchError || emptyError)}
      >
        {t("accountOptions.submit_button_label")}
      </Button>
    </div>
  );

  const allCategory = ["add_config", "update_config", "misc_config"];

  const addConfig = [
    "add_accident_email",
    "add_asset_request_email",
    "add_auction_disposal_email",
    "add_scrap_disposal_email",
    "add_donation_disposal_email",
    "add_issue_email",
    "add_maintenance_email",
    "add_repair_email",
    "add_transfer_email",
    "add_error_report_email",
  ];

  const updateConfig = [
    "update_accident_email",
    "update_asset_request_email",
    "update_daily_check_email",
    "update_disposal_email",
    "update_issue_email",
    "update_maintenance_email",
    "update_repair_email",
    "update_transfer_email",
  ];

  const miscConfig = [
    "daily_check_issues_email",
    "asset_request_status_email",
    "reassign_asset_email",
    "upcoming_maintenance_email",
    "document_expirations_email",
  ];

  const allConfig = {
    add_config: addConfig,
    update_config: updateConfig,
    misc_config: miscConfig,
  };

  const onCategoryChange = (category) => {
    setCurrentCategory(category);
  };

  useEffect(() => {
    setCurrentCategory(allCategory[0]);
    let newConfigurations = {};
    userInfo.userConfig
      ? Object.entries(userInfo.userConfig).forEach(([key, value]) => {
        Object.values(allConfig).some((config) => config.includes(key)) &&
          (newConfigurations[key] = value);
      })
      : allCategory.forEach((category) => {
        const partialConfigurations = {};
        allConfig[category].forEach((configuration) => {
          partialConfigurations[configuration] = true;
        });
        Object.assign(newConfigurations, partialConfigurations);
      });
    setConfigurations(newConfigurations);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const tempConfigurations = { ...configurations };
    const newCurrentConfigurations = {};
    Object.entries(tempConfigurations).forEach(([key, value]) => {
      if (allConfig[currentCategory].includes(key)) newCurrentConfigurations[key] = value;
    });
    setCurrentConfigurations(newCurrentConfigurations);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentCategory, configurations]);

  const setOneConfigurations = (key) => () => {
    const tempConfigurations = { ...configurations };
    tempConfigurations[key] = !tempConfigurations[key];
    setConfigurations(tempConfigurations);
  };

  const setAllConfigurations = (value) => {
    const tempConfigurations = { ...configurations };
    Object.keys(tempConfigurations).forEach((key) => (tempConfigurations[key] = value));
    setConfigurations(tempConfigurations);
  };

  const handleConfigSubmission = () => {
    const authHeader = getAuthHeader();
    loadingAlert();
    axios
      .post(
        `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Update/Configuration`,
        configurations,
        authHeader
      )
      .then((_) => {
        setChangePwdDialog(false);
        setDataReady(false);
        successAlert("msg", t("accountOptions.email_update_success"));
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
      })
      .catch((err) => {
        ConsoleHelper(err);
        errorAlert(err.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  const footerConfig = (
    <div>
      <Button onClick={handleConfigSubmission} className="btn btn-secondary mt-4">
        {t("accountOptions.submit_button_label")}
      </Button>
    </div>
  );

  return (
    <div className="profile-left">
      <div className="p-d-flex p-py-2 justify-content-center">
        <div className="p-d-flex p-flex-column">
          <div className="profile-user-info-avatar">
            <img
              alt="user_image"
              src={userInfo.imageUrl}
              className="profile-user-info-avatar-img"
            />
            <button
              className="profile-img-btn change-button change-settings"
              onClick={() => setChangeImageDialog(true)}
            >
              <i className="pi pi-camera">{""}</i>
            </button>
          </div>
          <h4 className="text-center text-name p-mt-3">{userInfo.name || "N/A"}</h4>
          <h5 className="text-center text-role p-mb-4">{capitalize(userInfo.role) || "N/A"}</h5>
        </div>
      </div>
      <div className="p-d-flex p-flex-column p-0 align-items-center">
        <Dialog
          className="custom-main-dialog"
          baseZIndex={1000}
          header="Change Profile Image"
          visible={changeImageDialog}
          footer={footerImg}
          onHide={() => setChangeImageDialog(false)}
          style={{ width: "40vw" }}
          breakpoints={{ "1280px": "40vw", "960px": "60vw", "768px": "80vw" }}
        >
          <ImageDialog
            setDataReady={setDataReady}
            setChangeImageDialog={setChangeImageDialog}
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            fileLoading={fileLoading}
            setFileLoading={setFileLoading}
          />
        </Dialog>

        <button
          className="profile-pass-btn change-button change-settings bg-secondary"
          onClick={() => setChangePwdDialog(true)}
        >
          <i className="pi pi-pencil p-mr-2">{""}</i>
          {t("accountOptions.change_password")}
        </button>
        <Dialog
          className="custom-main-dialog"
          baseZIndex={1000}
          header="Change Profile Password"
          visible={changePwdDialog}
          footer={footerPwd}
          onHide={() => setChangePwdDialog(false)}
          style={{ width: "30vw" }}
          breakpoints={{ "1280px": "40vw", "960px": "60vw", "768px": "80vw" }}
        >
          <PasswordDialog
            userInfo={userInfo}
            setChangePwdDialog={setChangePwdDialog}
            password={password}
            setPassword={setPassword}
            matchError={matchError}
            emptyError={emptyError}
            newPassword={newPassword}
            setNewPassword={setNewPassword}
            confirmPassword={confirmPassword}
            setConfirmPassword={setConfirmPassword}
            submitPassword={submitPassword}
            setSubmitPassword={setSubmitPassword}
          />
        </Dialog>

        <button
          className={`profile-pass-btn change-button change-settings bg-secondary ${isMobile ? "p-mt-3" : "p-mt-1"
            }`}
          onClick={() => setChangeConfigDialog(true)}
        >
          <i className="pi pi-bell p-mr-2">{""}</i>
          {t("accountOptions.notification_setting")}
        </button>
        <Dialog
          className="custom-main-dialog"
          baseZIndex={1000}
          header="Change Email Notification Setting"
          visible={changeConfigDialog}
          footer={footerConfig}
          onHide={() => setChangeConfigDialog(false)}
          style={{ width: "50vw" }}
          breakpoints={{ "1280px": "50vw", "960px": "70vw", "768px": "80vw" }}
        >
          <ConfigDialog
            defaultCategory={currentCategory}
            allCategory={allCategory}
            onCategoryChange={onCategoryChange}
            configurations={currentConfigurations}
            setConfigurations={setOneConfigurations}
            setAllConfigurations={setAllConfigurations}
          />
        </Dialog>
      </div>
    </div>
  );
};

const Profile = () => {
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const { userInfo } = useSelector((state) => state.apiCallData);
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [dataReady, setDataReady] = useState(true);
  const [userInformation, setUserInfo] = useState({
    name: userInfo.user.first_name + " " + userInfo.user.last_name,
    role: userInfo.detailed_user.role_permissions.role,
    firstName: userInfo.user.first_name,
    lastName: userInfo.user.last_name,
    email: userInfo.user.email,
    joinDate: moment(userInfo.user.date_joined).format("YYYY-MM-DD") || t("general.not_applicable"),
    lastLogin: moment(userInfo.user.last_login).format("YYYY-MM-DD") || t("general.not_applicable"),
    userConfig: userInfo.user_config,
    ...(userInfo.detailed_user.company
      ? { company: userInfo.detailed_user.company.company_name }
      : { company: t("general.not_applicable") }),
    ...(userInfo.detailed_user.business_unit
      ? { businessUnit: userInfo.detailed_user.business_unit.name }
      : { businessUnit: t("general.not_applicable") }),
    ...(userInfo.detailed_user.location.length !== 0
      ? { location: userInfo.detailed_user.location }
      : { location: t("general.not_applicable") }),
    ...(userInfo.detailed_user.cost_allowance
      ? { costAllowance: userInfo.detailed_user.cost_allowance }
      : { costAllowance: t("general.not_applicable") }),
    ...(userInfo.detailed_user.image_url.toLowerCase() !== "na"
      ? { imageUrl: userInfo.detailed_user.image_url }
      : { imageUrl: process.env.PUBLIC_URL + "/user_img_placeholder.jpg" }),
  });

  useEffect(() => {
    if (!dataReady) {
      const authHeader = getAuthHeader();
      let userInfoRequests = axios.get(
        `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Info`,
        authHeader
      );
      axios
        .all([userInfoRequests])
        .then(
          axios.spread((...responses) => {
            const userInfoResponse = !!responses[0] ? responses[0].data : 0;
            dispatch(getUserInformation(responses[0].data));
            setUserInfo({
              name: userInfoResponse.user.first_name + " " + userInfoResponse.user.last_name,
              role: userInfoResponse.detailed_user.role_permissions.role,
              firstName: userInfoResponse.user.first_name,
              lastName: userInfoResponse.user.last_name,
              email: userInfoResponse.user.email,
              joinDate:
                moment(userInfoResponse.user.date_joined).format("YYYY-MM-DD") ||
                t("general.not_applicable"),
              lastLogin:
                moment(userInfoResponse.user.last_login).format("YYYY-MM-DD") ||
                t("general.not_applicable"),
              userConfig: userInfoResponse.user_config,
              ...(userInfoResponse.detailed_user.company
                ? { company: userInfoResponse.detailed_user.company.company_name }
                : { company: t("general.not_applicable") }),
              ...(userInfoResponse.detailed_user.business_unit
                ? { businessUnit: userInfoResponse.detailed_user.business_unit.name }
                : { businessUnit: t("general.not_applicable") }),
              ...(userInfoResponse.detailed_user.location.length !== 0
                ? { location: userInfoResponse.detailed_user.location }
                : { location: t("general.not_applicable") }),
              ...(userInfoResponse.detailed_user.cost_allowance
                ? { costAllowance: userInfoResponse.detailed_user.cost_allowance }
                : { costAllowance: t("general.not_applicable") }),
              ...(userInfoResponse.detailed_user.image_url.toLowerCase() !== "na"
                ? { imageUrl: userInfoResponse.detailed_user.image_url }
                : { imageUrl: process.env.PUBLIC_URL + "/user_img_placeholder.jpg" }),
            });
            setDataReady(true);
          })
        )
        .catch((errors) => {
          ConsoleHelper("Errors: " + errors);
        });
    }
    // eslint-disable-next-line
  }, [dataReady]);

  return (
    <div className="profile-page">
      <div className={`header-container p-mx-5 ${!isMobile ? "p-mt-5" : "p-mt-2"}`}>
        <PanelHeader icon={faUser} text={t("accountOptions.profile_title")} disableBg />
      </div>
      <ProfileRow title={t("accountOptions.profile_first_name")} info={userInfo.firstName} />
      <ProfileRow title={t("accountOptions.profile_last_name")} info={userInfo.lastName} />
      <ProfileRow title={t("accountOptions.profile_email")} info={userInfo.email} />
      <ProfileRow title={t("accountOptions.profile_company")} info={userInfo.company} />
      <ProfileRow title={t("accountOptions.profile_business_unit")} info={userInfo.businessUnit} />
      <ProfileRow
        title={t("accountOptions.profile_location")}
        info={
          userInfo.location ? (
            // <ShowMore text={createLocations(userInfo.location)} limit={35} excerpt={35} />
            <ShowMore limit={35} excerpt={35} />
          ) : (
            "N/A"
          )
        }
      />
      <ProfileRow
        title={t("accountOptions.profile_cost_allowance")}
        info={"$ " + userInfo.costAllowance.toLocaleString()}
      />
      <ProfileRow title={t("accountOptions.profile_join_date")} info={userInfo.joinDate} />
      <ProfileRow title={t("accountOptions.profile_last_login")} info={userInfo.lastLogin} />
    </div>
  );
};

export default Profile;
