import { useState, useEffect, lazy, Suspense } from "react";
import { useHistory, BrowserRouter as Router, Switch, Route, Redirect } from "react-router-dom";
import axios from "axios";
import _ from "lodash";
import Pusher from "pusher-js/with-encryption";
import { useTranslation } from "react-i18next";
import { useDispatch, useSelector } from "react-redux";
import { getUserInformation } from "../../redux/actions/apiCallAction";
import * as Constants from "../../constants";
import NavigationItems from "../../routes/NavigationItems";
import VINSearch from "../../components/ShareComponents/helpers/VINSearch";
import PrivateRoute from "../PrivateRoute";
import AppTopbar from "../../components/ShareComponents/Navigation/AppTopbar";
import AppMenu from "../../components/ShareComponents/Navigation/AppMenu";
import AppRightMenu from "../../components/ShareComponents/Navigation/AppRightMenu";
import AppSearch from "../../components/ShareComponents/AppSearch";
import { updateAudioData } from "../../redux/actions/audioControllAction";
import bgVid from "../../images/background/main_bg.mp4";
import GasEmissionsCalculator from "../../components/GHG_Calculator/GasEmissionsCalculator";

// For gear icon
// import AppConfig from "../../AppConfig";
// import PrimeReact from "primereact/api";
import classNames from "classnames";
import "primereact/resources/themes/saga-blue/theme.css";
import "primereact/resources/primereact.min.css";
import "primeicons/primeicons.css";
import "primeflex/primeflex.css";
import "./PrimeInterface.scss";
import {
  getAuthHeader,
  hasModulePermission,
  getRolePermissions,
  tokenRefresh,
  setAgreementHeader,
  getAgreementStatus,
  logout,
} from "../../helpers/Authorization";
import { Dialog } from "primereact/dialog";
import { Button } from "primereact/button";
import { Checkbox } from "primereact/checkbox";
import { useIdleTimer } from "react-idle-timer";
import { timeoutAlert } from "../../components/ShareComponents/CommonAlert";
import { FRONTEND_TIMEOUT } from "../../constants";
import FirstTimePwd from "../../components/ShareComponents/FirstTimePwd";
import SystemAssistant from "../../components/ShareComponents/SystemAssistant";
import PageSkeleton from "../../components/ShareComponents/CustomSkeleton/PageSkeleton";
import ErrorBoundary from "../../components/ShareComponents/ErrorBoundary";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import { isMobileDevice } from "../../helpers/helperFunctions";

const Profile = lazy(() => import("../../components/AccountOptions/Profile"));
const ManageAccounts = lazy(() => import("../../components/AccountOptions/ManageAccounts"));
const ManageNotifications = lazy(() =>
  import("../../components/AccountOptions/ManageNotifications")
);
const AssetDetailPanel = lazy(() => import("../../components/AssetDetailPanel"));
const AssetTransferPanel = lazy(() => import("../../components/TransfersPanel/TransferAsset"));
const ApprovalPanel = lazy(() => import("../../components/ApprovalPanel"));
const FeedbackPanel = lazy(() => import("../../components/FeedbackPanel"));

const VINSearchWrapper = () => {
  let history = useHistory();

  return (
    <VINSearch
      onVehicleSelected={(vehicle) => {
        if (vehicle) history.push("/asset-details/" + vehicle.VIN);
      }}
    />
  );
};

const Home = ({ history }) => {
  const rolePermissions = getRolePermissions();
  let authHeader = getAuthHeader();

  if (authHeader !== null) {
    if (rolePermissions.role.toLowerCase() === "supervisor") {
      return <Redirect to="/assets" />;
    } else {
      return <Redirect to="/dashboard" />;
    }
  }

  return <div />;
};

const PrimeInterface = () => {
  const { t } = useTranslation();
  const { initDataLoaded, userInfo, userConfig } = useSelector((state) => state.apiCallData);

  if (!initDataLoaded) {
    logout();
  }

  const [inputStyle, setInputStyle] = useState("outlined");
  const [ripple, setRipple] = useState(false);
  const [colorScheme, setColorScheme] = useState("light");
  const [menuTheme, setMenuTheme] = useState("layout-sidebar-blue");

  const [menuActive, setMenuActive] = useState(false);
  const [menuMode, setMenuMode] = useState("slim");
  const [isCompact, setIsCompact] = useState(false);
  const [overlayMenuActive, setOverlayMenuActive] = useState(false);
  const [staticMenuDesktopInactive, setStaticMenuDesktopInactive] = useState(false);
  const [staticMenuMobileActive, setStaticMenuMobileActive] = useState(false);
  const [searchActive, setSearchActive] = useState(false);
  const [topbarUserMenuActive, setTopbarUserMenuActive] = useState(false);
  const [topbarNotificationMenuActive, setTopbarNotificationMenuActive] = useState(false);
  const [rightMenuActive, setRightMenuActive] = useState(false);
  const [configActive, setConfigActive] = useState(false);
  const [warningMsg, setWarningMsg] = useState(false);
  const [agreementDialog, setAgreementDialog] = useState(false);
  const [agreementChecked, setAgreementChecked] = useState(false);
  const [assitantStatus, setAssistantStatus] = useState(false);
  const [channel, setChannel] = useState(null);
  const dispatch = useDispatch();
  const [badges, setBadges] = useState({
    issues: 0,
    repairs: 0,
    maintenances: 0,
    incidents: 0,
    opChecks: 0,
  });
  const [notificationInfo, setNotificationInfo] = useState({ total: 0, approval: 0 });
  let userInformation = {
    name: userInfo.user.first_name + " " + userInfo.user.last_name,
    role: userInfo.detailed_user.role_permissions.role,
    ...(userInfo.detailed_user.image_url.toLowerCase() !== "na"
      ? { picUrl: userInfo.detailed_user.image_url }
      : { picUrl: process.env.PUBLIC_URL + "/user_img_placeholder.jpg" }),
    company: userInfo.detailed_user.company ? userInfo.detailed_user.company.company_name : "na",
  };

  const updateUserInformation = () => {
    const authHeader = getAuthHeader();
    let userInfoRequests = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Info`,
      authHeader
    );
    axios.all([userInfoRequests]).then(
      axios.spread((...responses) => {
        const userInfoResponse = !!responses[0] ? responses[0].data : 0;
        dispatch(getUserInformation(responses[0].data));
        userInformation = {
          name: userInfoResponse.user.first_name + " " + userInfoResponse.user.last_name,
          role: userInfoResponse.detailed_user.role_permissions.role,
          ...(userInfoResponse.detailed_user.image_url.toLowerCase() !== "na"
            ? { picUrl: userInfoResponse.detailed_user.image_url }
            : { picUrl: process.env.PUBLIC_URL + "/user_img_placeholder.jpg" }),
          company: userInfoResponse.detailed_user.company
            ? userInfoResponse.detailed_user.company.company_name
            : "na",
        };
      })
    );
  };

  const timeout = FRONTEND_TIMEOUT;
  const handleOnIdle = () => {
    pause();
    timeoutAlert(timeout, () => reset());
  };
  const { reset, pause } = useIdleTimer({
    timeout: timeout,
    onIdle: handleOnIdle,
    debounce: 500,
  });

  useEffect(() => {
    tokenRefresh();
  }, []);

  useEffect(() => {
    const agreementStatus = getAgreementStatus();
    if (!agreementStatus) {
      setAgreementDialog(true);
      setAssistantStatus(true);
    }
  }, []);

  useEffect(() => {
    if (userConfig && userConfig.sound !== undefined && userConfig.sound_percentage !== undefined) {
      const { sound, sound_percentage } = userConfig;
      dispatch(updateAudioData(sound, sound_percentage / 20));
    }
  }, [dispatch, userConfig]);

  useEffect(() => {
    const pusher = new Pusher("4cef4fa8a44a53ed190b", {
      cluster: "us2",
      encrypted: true,
      authEndpoint: `${Constants.ENDPOINT_PREFIX}/api-auth/v1/pusher/auth`,
      auth: {
        headers: getAuthHeader().headers,
      },
    });

    if (userInformation.company && userInformation.company.length > 0) {
      setChannel(pusher.subscribe(`private-encrypted-${userInformation.company}`));
    }

    return () => pusher.unsubscribe(`private-encrypted-${userInformation.company}`);
  }, [userInformation.company]);

  useEffect(() => {
    if (channel) {
      if (userInfo.detailed_user.role_permissions.role.toLowerCase() === "operator") {
        channel.bind("opcheck_done", function (data) {
          setBadges((b) => ({
            ...b,
            opChecks: b.opChecks - 1,
          }));
        });
      } else {
        channel.bind("repair_created", function () {
          setBadges((b) => ({
            ...b,
            repairs: b.repairs + 1,
          }));
        });
        channel.bind("repair_cancelled", function () {
          setBadges((b) => ({
            ...b,
            repairs: b.repairs - 1,
          }));
        });
        channel.bind("repair_complete", function () {
          setBadges((b) => ({
            ...b,
            repairs: b.repairs - 1,
          }));
        });
        channel.bind("repair_incomplete", function () {
          setBadges((b) => ({
            ...b,
            repairs: b.repairs + 1,
          }));
        });
        channel.bind("issue_created", function () {
          setBadges((b) => ({
            ...b,
            issues: b.issues + 1,
          }));
        });
        channel.bind("issue_resolved", function (data) {
          setBadges((b) => ({
            ...b,
            issues: b.issues - data.count,
          }));
        });
        channel.bind("issue_unresolved", function () {
          setBadges((b) => ({
            ...b,
            issues: b.issues + 1,
          }));
        });
        channel.bind("maintenance_created", function (data) {
          setBadges((b) => ({
            ...b,
            maintenances: b.maintenances + data.count,
          }));
        });
        channel.bind("maintenance_incomplete", function () {
          setBadges((b) => ({
            ...b,
            maintenances: b.maintenances + 1,
          }));
        });
        channel.bind("maintenance_complete", function () {
          setBadges((b) => ({
            ...b,
            maintenances: b.maintenances - 1,
          }));
        });
        channel.bind("maintenance_cancelled", function () {
          setBadges((b) => ({
            ...b,
            maintenances: b.maintenances - 1,
          }));
        });
        channel.bind("accident_created", function () {
          setBadges((b) => ({
            ...b,
            incidents: b.incidents + 1,
          }));
        });
        channel.bind("accident_resolved", function () {
          setBadges((b) => ({
            ...b,
            incidents: b.incidents - 1,
          }));
        });
        channel.bind("opcheck_done", function (data) {
          setBadges((b) => ({
            ...b,
            opChecks: b.opChecks - 1,
          }));
        });
        channel.bind("approval_created", function (data) {
          if (data.location === userInformation.location_id) {
            setNotificationInfo((b) => ({
              approval: b.approval + 1,
              total: parseInt(b.total) + parseInt(data.count),
            }));
          }
        });
        channel.bind("approval_approved", function (data) {
          if (data.location === userInformation.location_id) {
            setNotificationInfo((b) => ({
              approval: b.approval - 1,
              total: b.total - 1,
            }));
          }
        });
        channel.bind("approval_denied", function (data) {
          if (data.location === userInformation.location_id) {
            setNotificationInfo((b) => ({
              approval: b.approval - 1,
              total: b.total - 1,
            }));
          }
        });
      }
    }
    return () => channel && channel.unbind();
  }, [channel]);

  let menuClick = false;
  let searchClick = false;
  let userMenuClick = false;
  let notificationMenuClick = false;
  let rightMenuClick = false;
  let configClick = false;
  let userNavItems = [];

  NavigationItems.forEach((item) => {
    if (!hasModulePermission(item.module)) return;
    let navItem = { ...item };

    if (!!item.items) {
      let navSubMenu = [];
      item.items.forEach((subItem) => {
        if (!!subItem && !hasModulePermission(subItem.module)) return;

        navSubMenu.push({ ...subItem });
      });
      if (navSubMenu.length > 0) {
        navItem.items = navSubMenu;
        navItem.to = navSubMenu[0].to;
      } else {
        navItem.items = [];
        navItem.to = "/assets";
      }
    }
    userNavItems.push(navItem);
  });

  useEffect(() => {
    const authHeader = getAuthHeader();
    let repairRequests = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Count/Unresolved`,
      authHeader
    );
    let unresolvedIssues = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Issues/Count/Unresolved`,
      authHeader
    );
    let maintenanceRequests = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Maintenance/Count/Incomplete`,
      authHeader
    );
    let incidentRequest = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Accident/Count/Unresolved`,
      authHeader
    );
    let dailyOpChecks = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/DailyOperationalChecks/noDailyCheck`,
      authHeader
    );
    let ApprovalRequests = axios.get(
      `${Constants.ENDPOINT_PREFIX}/api/v1/Approval/Get/Approve`,
      authHeader
    );

    axios
      .all([
        repairRequests,
        unresolvedIssues,
        maintenanceRequests,
        incidentRequest,
        dailyOpChecks,
        ApprovalRequests,
      ])
      .then(
        axios.spread((...responses) => {
          const repairResponse = responses[0];
          const issuesResponse = responses[1];
          const maintenanceResponse = responses[2];
          const incidentResponse = responses[3];
          const opChecksResponse = responses[4];
          const approvalResponse = responses[5];

          if (userInfo.detailed_user.role_permissions.role.toLowerCase() === "operator") {
            setBadges((b) => ({
              ...b,
              issues: 0,
              repairs: 0,
              maintenances: 0,
              incidents: 0,
              opChecks: opChecksResponse.data.length,
            }));
          } else {
            setBadges((b) => ({
              ...b,
              issues: issuesResponse.data.count,
              repairs: repairResponse.data.count,
              maintenances: maintenanceResponse.data.count,
              incidents: incidentResponse.data.count,
              opChecks: opChecksResponse.data.length,
            }));
          }

          let approvals = approvalResponse.data;
          let needApprovals = _.filter(approvals, (approval) => {
            return approval.is_approved === null;
          });
          let needApprovalsNum = needApprovals.length > 0 ? needApprovals.length : 0;
          let totalNofiNum = needApprovalsNum;
          setNotificationInfo({
            approval: needApprovalsNum,
            total: totalNofiNum,
          });
        })
      )
      .catch((errors) => {
        ConsoleHelper("Errors: " + errors);
      });
  }, []);

  useEffect(() => {
    if (staticMenuMobileActive) {
      blockBodyScroll();
    } else {
      unblockBodyScroll();
    }
  }, [staticMenuMobileActive]);

  useEffect(() => {
    function handleResize() {
      setMenuMode("static");
    }
    window.addEventListener("resize", handleResize);
    handleResize();
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const onDocumentClick = () => {
    if (!searchClick && searchActive) {
      onSearchHide();
    }

    if (!userMenuClick) {
      setTopbarUserMenuActive(false);
    }

    if (!notificationMenuClick) {
      setTopbarNotificationMenuActive(false);
    }

    if (!rightMenuClick) {
      setRightMenuActive(false);
    }

    if (!menuClick) {
      if (isSlim()) {
        setMenuActive(false);
      }

      if (overlayMenuActive || staticMenuMobileActive) {
        hideOverlayMenu();
      }

      unblockBodyScroll();
    }

    if (configActive && !configClick) {
      setConfigActive(false);
    }

    searchClick = false;
    configClick = false;
    userMenuClick = false;
    rightMenuClick = false;
    notificationMenuClick = false;
    menuClick = false;
  };

  const onMenuClick = () => {
    menuClick = true;
  };

  const onMenuButtonClick = (event) => {
    menuClick = true;
    setTopbarUserMenuActive(false);
    setTopbarNotificationMenuActive(false);
    setRightMenuActive(false);

    if (isOverlay()) {
      setOverlayMenuActive((prevOverlayMenuActive) => !prevOverlayMenuActive);
    }

    if (isDesktop()) {
      setStaticMenuDesktopInactive(
        (prevStaticMenuDesktopInactive) => !prevStaticMenuDesktopInactive
      );
    } else {
      setStaticMenuMobileActive((prevStaticMenuMobileActive) => !prevStaticMenuMobileActive);
    }

    event.preventDefault();
  };

  const onMenuitemClick = (event) => {
    if (!event.item.items) {
      hideOverlayMenu();

      if (isSlim()) {
        setMenuActive(false);
      }
    }
  };

  const onRootMenuitemClick = () => {
    setMenuActive((prevMenuActive) => !prevMenuActive);
  };

  const onTopbarUserMenuButtonClick = (event) => {
    userMenuClick = true;
    setTopbarUserMenuActive((prevTopbarUserMenuActive) => !prevTopbarUserMenuActive);

    hideOverlayMenu();

    event.preventDefault();
  };

  const onTopbarNotificationMenuButtonClick = (event) => {
    notificationMenuClick = true;
    setTopbarNotificationMenuActive(
      (prevTopbarNotificationMenuActive) => !prevTopbarNotificationMenuActive
    );

    hideOverlayMenu();

    event.preventDefault();
  };

  const toggleSearch = () => {
    setSearchActive((prevSearchActive) => !prevSearchActive);
    searchClick = true;
  };

  const onSearchClick = () => {
    searchClick = true;
  };

  const onSearchHide = () => {
    setSearchActive(false);
    searchClick = false;
  };

  const onRightMenuClick = () => {
    rightMenuClick = true;
  };

  const onRightMenuButtonClick = (event) => {
    rightMenuClick = true;
    setRightMenuActive((prevRightMenuActive) => !prevRightMenuActive);
    hideOverlayMenu();
    event.preventDefault();
  };

  const hideOverlayMenu = () => {
    setOverlayMenuActive(false);
    setStaticMenuMobileActive(false);
    unblockBodyScroll();
  };

  const blockBodyScroll = () => {
    if (document.body.classList) {
      document.body.classList.add("blocked-scroll");
    } else {
      document.body.className += " blocked-scroll";
    }
  };

  const unblockBodyScroll = () => {
    if (document.body.classList) {
      document.body.classList.remove("blocked-scroll");
    } else {
      document.body.className = document.body.className.replace(
        new RegExp("(^|\\b)" + "blocked-scroll".split(" ").join("|") + "(\\b|$)", "gi"),
        " "
      );
    }
  };

  const isSlim = () => {
    return menuMode === "slim";
  };

  const isOverlay = () => {
    return menuMode === "overlay";
  };

  const isDesktop = () => {
    return window.innerWidth > 991;
  };

  const containerClassName = classNames(
    "layout-wrapper",
    // `${isMobileDevice() ? "" : ""}`,
    {
      "layout-overlay": menuMode === "overlay",
      "layout-static": menuMode === "static",
      "layout-slim": menuMode === "slim",
      "layout-sidebar-dim": colorScheme === "dim",
      "layout-sidebar-dark": colorScheme === "dark",
      "layout-overlay-active": overlayMenuActive,
      "layout-mobile-active": staticMenuMobileActive,
      "layout-static-inactive": staticMenuDesktopInactive && menuMode === "static",
      "p-input-filled": inputStyle === "filled",
      "p-ripple-disabled": !ripple,
    },
    colorScheme === "light" ? menuTheme : ""
  );

  const handleAgreementChecked = () => {
    setAgreementHeader(true);
    setAgreementDialog(false);
    axios
      .post(
        `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Update/Agreement`,
        {
          agreement_accepted: true,
        },
        getAuthHeader()
      )
      .then((res) => {
        setAgreementHeader(true);
      })
      .catch((error) => {
        ConsoleHelper(error);
      });
  };

  const renderAgreementFooter = () => {
    return (
      <div className={`p-mt-4 p-d-flex p-jc-between ${!isDesktop() && "flex-wrap"}`}>
        <div className="p-d-flex p-flex-column">
          <div className="p-d-flex p-jc-start">
            <Checkbox
              inputId="agreement"
              checked={agreementChecked}
              onChange={(e) => setAgreementChecked(e.checked)}
            />
            <label htmlFor="agreement" className="p-checkbox-label p-mb-0 p-ml-2 font-weight-bold">
              {t("firstTimeAgreement.agreement_checkbox")}
            </label>
          </div>
          {warningMsg && (
            <div className="text-left">
              <i className="pi pi-exclamation-circle text-danger" style={{ fontSize: "12px" }} />
              <span className="p-ml-2 text-danger">
                {t("firstTimeAgreement.agreement_warning_msg")}
              </span>
            </div>
          )}
        </div>
        <Button
          label={t("general.confirm")}
          icon="pi pi-check"
          onClick={handleAgreementChecked}
          disabled={!agreementChecked}
          className={!isDesktop() && "w-100 mt-2"}
        />
      </div>
    );
  };

  return (
    <Router>
      <div className={containerClassName} data-theme={colorScheme} onClick={onDocumentClick}>
        <div
          className={`layout-content-wrapper ${
            isSlim() && isCompact && isDesktop() && "layout-content-wrapper-compact"
          }`}
        >
          <video playsInline autoPlay muted loop className="bg-vid">
            <source src={bgVid} type="video/mp4" />
          </video>
          <AppTopbar
            notificationInfo={notificationInfo}
            userInfo={userInformation}
            routers={userNavItems}
            topbarNotificationMenuActive={topbarNotificationMenuActive}
            topbarUserMenuActive={topbarUserMenuActive}
            onMenuButtonClick={onMenuButtonClick}
            onSearchClick={toggleSearch}
            onTopbarNotification={onTopbarNotificationMenuButtonClick}
            onTopbarUserMenu={onTopbarUserMenuButtonClick}
            onRightMenuClick={onRightMenuButtonClick}
            onRightMenuButtonClick={onRightMenuButtonClick}
            assitantStatus={assitantStatus}
            setAssistantStatus={setAssistantStatus}
          />
          <div className="layout-content">
            <div className="layout-content-inner">
              {/* First time login changepwd */}
              {userInfo.detailed_user.first_time_login && <FirstTimePwd />}

              {/* First time login agreement */}
              {!userInfo.detailed_user.first_time_login && (
                <Dialog
                  header={t("firstTimeAgreement.agreement_title")}
                  visible={agreementDialog}
                  style={{ width: "50vw" }}
                  breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
                  footer={renderAgreementFooter()}
                  onHide={() => setWarningMsg(true)}
                  maximizable
                >
                  <p className="p-mx-3">{t("firstTimeAgreement.agreement_content")}</p>
                </Dialog>
              )}

              {/* First time login Assistant */}
              {isDesktop() &&
                assitantStatus &&
                !agreementDialog &&
                !userInfo.detailed_user.first_time_login && (
                  <SystemAssistant setAssistantStatus={setAssistantStatus} />
                )}

              <Switch>
                <ErrorBoundary>
                  <Suspense fallback={<PageSkeleton />}>
                    <Route path="/" component={Home} exact />
                    <Route path="/ghg_calculator">
                      <GasEmissionsCalculator />
                    </Route>
                    <Route path="/account-options" exact>
                      <Profile />
                    </Route>
                    <Route path="/manage-accounts" exact>
                      <ManageAccounts updateUserInformation={updateUserInformation} />
                    </Route>
                    <Route path="/manage-notifications" exact>
                      <ManageNotifications />
                    </Route>
                    <Route path="/asset-details" exact>
                      <VINSearchWrapper />
                    </Route>
                    <Route path="/asset-details/:vin">
                      <AssetDetailPanel />
                    </Route>
                    <Route path="/transfers/asset-transfer/:vin">
                      <AssetTransferPanel />
                    </Route>
                    <Route path="/approval">
                      <ApprovalPanel />
                    </Route>
                    <Route path="/feedback">
                      <FeedbackPanel />
                    </Route>
                    {NavigationItems.map((item) => {
                      if (!!item.separator) return null;
                      if (item.items === undefined) {
                        return (
                          <PrivateRoute
                            key={item.label}
                            path={item.to}
                            module={item.module}
                            exact={item.exact}
                            component={item.content}
                          />
                        );
                      } else {
                        return item.items.map((subitem) => {
                          return (
                            <PrivateRoute
                              key={subitem.label}
                              path={subitem.to}
                              module={subitem.module}
                              exact={subitem.exact}
                              component={subitem.content}
                            />
                          );
                        });
                      }
                    })}
                  </Suspense>
                </ErrorBoundary>
              </Switch>
            </div>
          </div>
        </div>
        <AppMenu
          model={userNavItems}
          badges={badges}
          menuMode={menuMode}
          isCompact={isCompact}
          setIsCompact={setIsCompact}
          isSlim={isSlim}
          active={menuActive}
          setMobileMenuActive={setStaticMenuMobileActive}
          mobileMenuActive={staticMenuMobileActive}
          onMenuClick={onMenuClick}
          onMenuitemClick={onMenuitemClick}
          onRootMenuitemClick={onRootMenuitemClick}
          notificationInfo={notificationInfo}
          isInteractive={!assitantStatus}
        />
        <AppRightMenu rightMenuActive={rightMenuActive} onRightMenuClick={onRightMenuClick} />
        <AppSearch
          searchActive={searchActive}
          onSearchClick={onSearchClick}
          onSearchHide={onSearchHide}
        />
      </div>
    </Router>
  );
};

export default PrimeInterface;
