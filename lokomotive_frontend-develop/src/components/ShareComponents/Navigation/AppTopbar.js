import React, { useRef, useState, useEffect } from "react";
import ReactTooltip from "react-tooltip";
import classNames from "classnames";
import { debounce } from "lodash";
import { Button } from "primereact/button";
import { useTranslation } from "react-i18next";
import { Link, useHistory } from "react-router-dom";
import {
  getAuthHeader,
  logout,
  getRolePermissions,
  getSuperUserPermission,
} from "../../../helpers/Authorization";
import { AutoComplete } from "primereact/autocomplete";
import { OverlayPanel } from "primereact/overlaypanel";
import axios from "axios";
import * as Constants from "../../../constants";
import { isMobileDevice } from "../../../helpers/helperFunctions";
import FleetGuru from "./FleetGuru";
import bell from "../../../images/menu/topbar_menu_notifications.png";
// import messages from "../../../images/menu/topbar_menu_messages.png";
import feedback from "../../../images/menu/topbar_menu_feedback.png";
import robotOff from "../../../images/menu/topbar_menu_robot_default.png";
import robotOn from "../../../images/menu/topbar_menu_robot_on.png";
import "../../../styles/tooltipStyles.scss";
import "../../../styles/ShareComponents/Navigation/topbar.scss";
import "../../../styles/ShareComponents/Navigation/FleetGuru.scss";
import "../../../styles/ShareComponents/autoComplete.scss";

const NavigationSearch = () => {
  const [fieldValue, setFieldValue] = useState("");
  const [choices, setChoices] = useState([]);
  const { t } = useTranslation();

  useEffect(() => {
    if (choices) setChoices([]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fieldValue]);

  const debouncedSearch = useRef(
    debounce((cancelToken, fieldValue) => {
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetsByLast/VIN/UnitNumber/${fieldValue}`, {
          ...getAuthHeader(),
          cancelToken: cancelToken,
        })
        .then((response) => {
          if (response.data.length > 0) {
            let searchNumber = response.data.map((number) => {
              if (number.unit_number === fieldValue) {
                return number.unit_number;
              } else {
                return number.VIN;
              }
            });
            setChoices([...searchNumber]);
          }
        })
        .catch((e) => {
          if (e.response.status === 300) {
            setChoices([...e.response.data]);
          } else if (e.response.status === 400) {
            setChoices([t("navigationBar.no_matching_assets_found")]);
          }
        });
    }, 1000)
  ).current;

  const autoCompleteMethod = (event) => {
    const { token } = axios.CancelToken.source();
    if (event.query.trim().length >= 2) {
      debouncedSearch(token, fieldValue);
    }
  };

  const vinOption = (vin) => {
    const linkToVin = (
      <Link key={vin} to={`/asset-details/${vin}`} onClick={() => setFieldValue("")}>
        <div>{vin}</div>
      </Link>
    );
    return (
      <>{vin === t("navigationBar.no_matching_assets_found") ? <div>{vin}</div> : linkToVin}</>
    );
  };

  const handleClick = (e) => {
    if (e.value === t("navigationBar.no_matching_assets_found")) return null;
    else setFieldValue(e.value);
  };

  return (
    <li className="search-item">
      <AutoComplete
        panelClassName={choices.length === 0 ? "hide-panel" : ""}
        placeholder={t("searchBox.label_vin_search")}
        suggestions={choices}
        completeMethod={autoCompleteMethod}
        value={fieldValue}
        itemTemplate={vinOption}
        onChange={handleClick}
        minLength={2}
        field="name"
      />
    </li>
  );
};

const AppTopbar = (props) => {
  const [isSupervisor, setIsSupervisor] = useState(false);
  const [isOperator, setIsOperator] = useState(false);
  const [isSuperUser, setIsSuperUser] = useState(false);
  const [isDropdown, setIsDropdown] = useState(false);
  const [onFleetGuru, setOnFleetGuru] = useState(false);
  const fleetguruRef = useRef(null);

  const { t } = useTranslation();
  const history = useHistory();
  const notificationsItemClassName = classNames("notifications-item", {
    "active-menuitem": props.topbarNotificationMenuActive,
  });
  const profileItemClassName = classNames("profile-item", {
    "active-menuitem fadeInDown": props.topbarUserMenuActive,
  });
  let logo_img_url = process.env.PUBLIC_URL + "/assets/layout/images/logo_lokomotive_light.png";

  useEffect(() => {
    const rolePermissions = getRolePermissions();
    const superUserPermission = getSuperUserPermission();

    if (rolePermissions.role === "operator") {
      setIsOperator(true);
    }
    if (rolePermissions.role.toLowerCase() === "supervisor") setIsSupervisor(true);

    setIsSuperUser(superUserPermission);
  }, []);

  useEffect(() => {
    if (!onFleetGuru) {
      fleetguruRef.current.hide();
    }
  }, [onFleetGuru]);

  return (
    <div className="topbar-sticky">
      <div className={`layout-topbar topbar-cont-outter `}>
        <div className="topbar-left">
          <button type="button" className="menu-button p-link" onClick={props.onMenuButtonClick}>
            <i className="pi pi-chevron-left" />
          </button>
          {/* Disable top bar left for Lokomotive
            <span className="topbar-separator" />
          */}
          <div
            className={`topbar-son ${onFleetGuru ? "topbar-son-active" : ""}`}
            onClick={(e) => {
              setOnFleetGuru(!onFleetGuru);
              fleetguruRef.current.toggle(e);
            }}
          >
            {onFleetGuru ? <img src={robotOn} alt="" /> : <img src={robotOff} alt="" />}
          </div>
          <img
            id="logo-mobile"
            className="mobile-logo logo-image"
            src={logo_img_url}
            alt="aukai_logo"
          />
        </div>
        <div className="topbar-right">
          <ul className="topbar-menu">
            <div
              className={`topbar-son
                ${props.assitantStatus ? "topbar-son-hide" : ""}
                ${onFleetGuru ? "topbar-son-active" : ""} 
              `}
              onClick={(e) => {
                setOnFleetGuru(!onFleetGuru);
                fleetguruRef.current.toggle(e);
              }}
            >
              {onFleetGuru ? <img src={robotOn} alt="" /> : <img src={robotOff} alt="" />}
            </div>
            {/* FLEET GURU DROPDOWN */}
            <OverlayPanel
              className="custom-fleet-guru"
              ref={fleetguruRef}
              style={{ width: "550px", right: "200px !important" }}
              breakpoints={{ "550px": "400px", "400px": "350px" }}
              appendTo={document.body}
              onHide={() => setOnFleetGuru(false)}
            >
              <FleetGuru
                setOnFleetGuru={setOnFleetGuru}
                setAssistantStatus={props.setAssistantStatus}
              />
            </OverlayPanel>

            <NavigationSearch />
            <li className="feedback-item" data-tip data-for="feedback-tooltip">
              <Button
                className="p-button-secondary p-d-none p-d-md-inline-flex"
                iconPos="right"
                onClick={() => history.push("/feedback")}
              >
                <img src={feedback} alt="" />
              </Button>
              <Button
                className="p-button-secondary p-d-md-none"
                iconPos="right"
                onClick={() => history.push("/feedback")}
              >
                <img src={feedback} alt="" />
              </Button>
            </li>
            <ReactTooltip className="topbar-tooltip" id="feedback-tooltip" place="bottom">
              {t("navigationBar.topbar_feedback")}
            </ReactTooltip>

            {/* =============== MESSAGES ============================*/}
            {/* <li className="messages-item" data-tip data-for="msg-tooltip">
              <img src={messages} alt="" />
            </li>
            <ReactTooltip className="topbar-tooltip" id="msg-tooltip" place="bottom">
              {t("navigationBar.topbar_messages")}
            </ReactTooltip> */}
            {!isOperator && !isSupervisor ? (
              <li className={notificationsItemClassName} data-tip data-for="notifications-tooltip">
                <button type="button" className="p-link" onClick={props.onTopbarNotification}>
                  <img src={bell} alt="" />
                  {props.notificationInfo.approval > 0 && (
                    <span className="topbar-badge">{props.notificationInfo.approval}</span>
                  )}
                </button>
                <ul className="notifications-menu fade-in-up">
                  <li role="menuitem">
                    <button
                      type="button"
                      className="p-link"
                      tabIndex="0"
                      onClick={() => history.push("/approval")}
                    >
                      <i className="pi pi-check-circle" />
                      <div className="notification-item">
                        <div className="notification-summary">
                          {t("navigationBar.approval_requests")}
                        </div>
                        <div className="notification-detail">
                          {t("navigationBar.approval_requests_nofi_num", {
                            approvalRequestNum: props.notificationInfo.approval,
                          })}
                        </div>
                      </div>
                    </button>
                  </li>
                </ul>
              </li>
            ) : null}
            <li className={profileItemClassName}>
              <div className="main-btn">
                <button
                  type="button"
                  className="p-link p-d-flex p-ai-center"
                  onClick={props.onTopbarUserMenu}
                >
                  <img src={props.userInfo.picUrl} alt="diamond-layout" className="profile-image" />
                  <div className="profile-info">
                    <span className="profile-name">{props.userInfo.name}</span>
                    <i className="pi pi-chevron-down" />
                    <br />
                    {props.userInfo.role && (
                      <span className="profile-role">{props.userInfo.role}</span>
                    )}
                  </div>
                </button>
              </div>
              <ul className="profile-menu fade-in-up">
                <li>
                  <button
                    type="button"
                    className="p-link"
                    onClick={() => history.push("/account-options")}
                  >
                    <i className="pi pi-user" />
                    <span>Profile</span>
                  </button>
                </li>
                {isSuperUser ? (
                  <li>
                    <button
                      type="button"
                      className="p-link"
                      onClick={() => history.push("/manage-accounts")}
                    >
                      <i className="pi pi-users" />
                      <span>{t("accountOptions.manage_account_title")}</span>
                    </button>
                    <button
                      type="button"
                      className="p-link"
                      onClick={() => history.push("/manage-notifications")}
                    >
                      <i className="pi pi-bell" />
                      <span>{t("accountOptions.manage_notifications_title")}</span>
                    </button>
                  </li>
                ) : null}
                <li>
                  <button
                    type="button"
                    className="p-link"
                    onClick={() => {
                      logout();
                      window.location = "/";
                    }}
                  >
                    <i className="pi pi-power-off" />
                    <span>Logout</span>
                  </button>
                </li>
              </ul>
              {/* ENABLE ONCLICK FUNCTION ONCE WE HAVE WEATHER WIDGET */}
              {/*
              <button
                className="dropdown-btn"
                // onClick={() => setIsDropdown(!isDropdown)}
              >
                <i className={isDropdown ? "opac-0 pi pi-arrow-down" : "pi pi-arrow-down"} />
              </button>
              */}
            </li>
          </ul>
        </div>
      </div>
      <div className={isDropdown ? "topbar-dropdown" : "closed topbar-dropdown"}>
        {/* Temporary */}
        <h1>hello i am children</h1>
        <button onClick={() => setIsDropdown(!isDropdown)} className="dropdown-btn-hide">
          <p>hide</p>
        </button>
      </div>
    </div>
  );
};

export default AppTopbar;
