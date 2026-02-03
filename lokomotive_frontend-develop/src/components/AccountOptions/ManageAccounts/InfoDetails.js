import React, { useEffect, useState } from "react";
import axios from "axios";
import swal from "sweetalert";
import { useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { Button } from 'primereact/button';
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import UserInfoCard from "./UserInfoCard";
import EditUserCard from "./EditUserCard";
import { getAuthHeader } from "../../../helpers/Authorization";
import { loadingAlert, successAlert, errorAlert } from "../../ShareComponents/CommonAlert";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/helpers/button5.scss";

const InfoDetails = ({ userInfo, setUserInfo, setForceUpdate, updateUserInformation }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [onEditMode, setOnEditMode] = useState(false);

  useEffect(() => {
    setOnEditMode(false);
  }, [userInfo]);

  const resetPassword = () => {
    loadingAlert();
    axios.post(`${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Create/Password`, 
      { user_id: userInfo.user.id }, getAuthHeader())
      .then((res) => {
        setUserInfo(null);
        setForceUpdate(Date.now());
        successAlert();
      })
      .catch((error) => {
        errorAlert(error.customErrorMsg, resetPassword);
        ConsoleHelper(error);
      });
  }

  const handleResetPassword = () => {
    warningAlert();
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "warning_alert" });
  }

  const warningAlert = () => {
    return swal({
      title: t("general.warning"),
      text: t("accountOptions.warning_alert_text"),
      icon: "warning",
      buttons: {
        return: t("general.continue"),
        cancel: t("general.cancel")
      },
    }).then((value) => {
      if (value === "return") {
        resetPassword();
      }
    });
  }
  
  return (
    <div className="user-info-card p-d-flex p-flex-wrap">
      <div className="user-info-card-left p-d-flex p-ai-center">
        <div className="p-d-flex p-flex-column p-ai-center w-100">
          <div className="img-name p-d-flex p-ai-center p-jc-center p-flex-wrap w-100">
            <div className="user-info-avatar">
            {userInfo.detailed_user.image_url.toLowerCase() !== "na" ?
              <img className="user-info-avatar-img" alt="userimg" src={userInfo.detailed_user.image_url} /> 
              : <img className="user-info-avatar-img" alt="userimg" src={process.env.PUBLIC_URL + "/user_img_placeholder.jpg"} /> 
            }
            </div>
            <div className="user-info-msg p-mx-5 p-py-5 p-d-flex p-flex-column">
              <span className="name">{`${userInfo.user.first_name} ${userInfo.user.last_name}`}</span>
              <span className="position text-capitalize">{userInfo.detailed_user.role_permissions.role}</span>
            </div>
          </div>
          <div className="user-action-btns p-d-flex p-flex-column w-75">
            <div className="edit-btn">
              <Button
                className="w-100 p-button-lg"
                label={t("accountOptions.edit_user")}
                icon="pi pi-user-edit" 
                onClick={() => setOnEditMode(true)}
                disabled={onEditMode}
              />
            </div>
            <div className="btn-5 reset-btn">
              <Button
                className="w-100 p-button-lg"
                label={t("accountOptions.reset_password")}
                icon="pi pi-exclamation-triangle" 
                onClick={handleResetPassword}
              />
            </div>
          </div>
        </div>
      </div>
      <div className={`user-info-card-right p-px-5 p-py-3 ${onEditMode ? "edit-mode" : ""}`}>
        {!onEditMode ?
          <div className="info-details">
            <UserInfoCard userInfo={userInfo} />
          </div>
          :
          <div className="edit-info-details">
            <EditUserCard
              userInfo={userInfo}
              setOnEditMode={setOnEditMode}
              setForceUpdate={setForceUpdate}
              updateUserInformation={updateUserInformation}
            />
          </div>
        }
      </div>
    </div>
  );
}

export default InfoDetails;
