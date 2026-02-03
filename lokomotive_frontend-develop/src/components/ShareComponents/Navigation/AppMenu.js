import React, { useState, useEffect } from "react";
import { Link, useHistory } from "react-router-dom";
import { logout, getRolePermissions } from "../../../helpers/Authorization";
import { Button } from "primereact/button";
import { faChevronLeft } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useTranslation } from "react-i18next";
import AppSubmenu from "./AppSubmenu";
import { AiOutlineUser } from "react-icons/ai";
import settings from "../../../images/menu/icon_sidebar_settings.png";
import settingsHover from "../../../images/menu/icon_sidebar_settings_hover.png";
// import accessibility from "../../../images/menu/icon_sidebar_accessibility.png";
import logOut from "../../../images/menu/icon_sidebar_log-out.png";
import feedback from "../../../images/menu/topbar_menu_feedback.png";
import bell from "../../../images/menu/topbar_menu_notifications.png";
import "../../../styles/Navigation/sidebar.scss";
import "../../../styles/Navigation/compactSidebar.scss";
import SettingsDialog from "./SettingsDialog";

const AppMenu = (props) => {
  const { t } = useTranslation();
  const [isMouseOverSettings, setIsMouseOverSettings] = useState(false);
  const [isSettingsPanelDisplayed, setIsSettingsPanelDisplayed] = useState(false);
  const [configPanelPosition, setConfigPanelPosition] = useState(null);
  const [isOperator, setIsOperator] = useState(false);
  const [isSupervisor, setIsSupervisor] = useState(false);

  const isInteractive = props.isInteractive;

  useEffect(() => {
    const rolePermissions = getRolePermissions();

    if (rolePermissions.role === "operator") {
      setIsOperator(true);
    }
    if (rolePermissions.role.toLowerCase() === "supervisor") setIsSupervisor(true);
  }, []);

  const toggleCompactMenu = () => {
    props.setIsCompact((prevValue) => !prevValue);
  };

  let logo_img_url = process.env.PUBLIC_URL + "/assets/layout/images/logo_lokomotive_light.png";
  const history = useHistory();

  return (
    <div
      className={`dark-sidebar layout-sidebar ${props.isCompact && "layout-sidebar-compact"}`}
      onClick={props.onMenuClick}
    >
      <div
        className={`logo ${
          props.isCompact && props.isSlim() && !props.mobileMenuActive && "logo-hide"
        }`}
      >
        <div className="logo-image h-100">
          <Link to="/dashboard" className="home-btn-sidebar">
            <img id="app-logo" className="logo-image" src={logo_img_url} alt="Aukai Logo" />
          </Link>
        </div>
        <div className="logo-back-btn p-ml-2">
          <Button
            className="p-button-link mobile-back-btn"
            onClick={() => props.setMobileMenuActive(false)}
          >
            <FontAwesomeIcon icon={faChevronLeft} size={"2x"} color="white" />
          </Button>
        </div>
      </div>
      {props.menuMode === "slim" && !props.mobileMenuActive ? (
        <div onClick={toggleCompactMenu} className="menu-compact-toggle-container">
          <i
            className={`pi pi-angle-left menu-compact-toggle ${props.isCompact && "rotate-icon"}`}
          />
        </div>
      ) : null}
      <div className="layout-menu-container p-d-flex p-flex-column p-ai-strech p-ac-between">
        <AppSubmenu
          items={props.model}
          badges={props.badges}
          menuMode={props.menuMode}
          isCompact={props.isCompact}
          parentMenuItemActive
          menuActive={props.active}
          mobileMenuActive={props.mobileMenuActive}
          root
          onMenuitemClick={props.onMenuitemClick}
          onRootMenuitemClick={props.onRootMenuitemClick}
          isInteractive={props.isInteractive}
        />

        {props.menuMode === "static" && window.innerWidth >= 992 ? (
          <div
            className="sidebar-static-bottom-btn-group"

          >
            <div className="setting-button"
            onClick={(e) => {
              if (isInteractive) {
                props.setMobileMenuActive(false);
                setIsSettingsPanelDisplayed(true);
                setConfigPanelPosition(e.target.offsetLeft);
              }
              //console.log("Is Interactive? " + isInteractive)
            }}
          >
            <div
              className="setting-button"
              onMouseEnter={() => {setIsMouseOverSettings(true)}}
              onMouseLeave={() => {setIsMouseOverSettings(false)}}
            >

              <img src={isMouseOverSettings ? settingsHover : settings} alt="settings" width="18" height="18" />
              <span className="btn-text layout-root-menuitem">{t("settings.settings")}</span>
            </div>
          </div>
          </div>
        ) : (
          <div className="sidebar-bottom-btn-group p-pt-3">
            <div className="settings-btn">
              <div
                className={isMouseOverSettings ? "config-button-hovered" : "config-button"}
                onClick={(e) => {
                  if (isInteractive) {
                    setIsSettingsPanelDisplayed(true);
                    setConfigPanelPosition(e.target.offsetLeft);
                    //console.log("Is Interactive? " + isInteractive)
                  }
                }}
                onMouseEnter={() => {
                  setIsMouseOverSettings(true);
                }}
                onMouseLeave={() => {
                  setIsMouseOverSettings(false);
                }}
              >
                <img src={settings} alt="settings" />
              </div>
              <span className={isMouseOverSettings ? "config-txt-hovered" : "config-txt"}>
                {t("settings.settings")}
              </span>
            </div>
          </div>
        )}

        <div className="sidebar-bottom-nav p-mt-5">
          <hr className="p-mb-4" />
          {!isOperator && !isSupervisor ? (
            <div className="sidebar-bottom-nav-group">
              <button
                onClick={(e) => {
                  props.setMobileMenuActive(false);
                  history.push("/approval");
                }}
              >
                <div className="overlay-badge">
                  <img src={bell} alt="approvals" />
                  {props.notificationInfo.approval > 0 && (
                    <span className="p-badge p-badge-danger p-ml-2 false">
                      {props.notificationInfo.approval}
                    </span>
                  )}
                </div>

                <span style={{ paddingLeft: 5 }}>{t("navigationItems.approvals")}</span>
              </button>
            </div>
          ) : null}
          <div className="sidebar-bottom-nav-group">
            <button
              onClick={(e) => {
                props.setMobileMenuActive(false);
                history.push("/feedback");
              }}
            >
              <img src={feedback} alt="feedback" />
              <span>{t("navigationItems.feedback")}</span>
            </button>
          </div>

          <hr className="p-mt-4" />

          <div className="sidebar-bottom-nav-group">
            <button
              className="sidebar-profile-btn p-mt-3"
              onClick={() => {
                props.setMobileMenuActive(false);
                history.push("/account-options");
              }}
            >
              <AiOutlineUser />
              <span>Profile</span>
            </button>
          </div>
          <div className="sidebar-bottom-nav-group">
            <button
              type="button"
              className="p-link"
              onClick={() => {
                props.setMobileMenuActive(false);
                history.push("/manage-accounts");
              }}
            >
              <i className="pi pi-users sidebar-manage-acc" />
              <span>{t("accountOptions.manage_account_title")}</span>
            </button>
          </div>
          <div className="sidebar-bottom-nav-group">
            <button
              onClick={(e) => {
                props.setMobileMenuActive(false);
                setIsSettingsPanelDisplayed(true);
                setConfigPanelPosition(e.target.offsetLeft);
              }}
            >
              <img src={settings} alt="settings" />
              <span>{t("settings.settings")}</span>
            </button>
          </div>
          {/* <div className="sidebar-bottom-nav-group">
            <button>
              <img src={accessibility} alt="" />
              <span>Accessibility</span>
            </button>
          </div> */}
          <div className="sidebar-bottom-nav-group">
            <button
              onClick={() => {
                logout();
                window.location = "/";
              }}
            >
              <img src={logOut} alt="" />
              <span>Log Out</span>
            </button>
          </div>
        </div>
      </div>

      {isSettingsPanelDisplayed && (
        <SettingsDialog
          setIsSettingsPanelDisplayed={setIsSettingsPanelDisplayed}
          configPanelPosition={configPanelPosition}
        />
      )}
    </div>
  );
};

export default AppMenu;
