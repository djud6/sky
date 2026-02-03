import React, { useCallback, useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { NavLink } from "react-router-dom";
import { CSSTransition } from "react-transition-group";
import classNames from "classnames";
import { useTranslation } from "react-i18next";
import dashboard from "../../../images/menu/icon_menu_dashboard.png";
import transfers from "../../../images/menu/icon_menu_transfers.png";
import repairs from "../../../images/menu/icon_menu_repairs.png";
import maintenance from "../../../images/menu/icon_menu_maintenance.png";
import incidents from "../../../images/menu/icon_menu_incidents.png";
import issues from "../../../images/menu/icon_menu_issues.png";
import operators from "../../../images/menu/icon_menu_operators.png";
import disposal from "../../../images/menu/icon_menu_disposal.png";
import assets from "../../../images/menu/icon_menu_assets.png";
import energy from "../../../images/menu/icon_menu_energy.png";
import inventory from "../../../images/menu/icon_menu_inventory.png";
import dashboardHighlighted from "../../../images/menu/icon_menu_dashboard_highlighted.png";
import transfersHighlighted from "../../../images/menu/icon_menu_transfers_highlighted.png";
import repairsHighlighted from "../../../images/menu/icon_menu_repairs_highlighted.png";
import maintenanceHighlighted from "../../../images/menu/icon_menu_maintenance_highlighted.png";
import incidentsHighlighted from "../../../images/menu/icon_menu_incidents_highlighted.png";
import issuesHighlighted from "../../../images/menu/icon_menu_issues_highlighted.png";
import operatorsHighlighted from "../../../images/menu/icon_menu_operators_highlighted.png";
import disposalHighlighted from "../../../images/menu/icon_menu_disposal_highlighted.png";
import assetsHighlighted from "../../../images/menu/icon_menu_assets_highlighted.png";
import energyHighlighted from "../../../images/menu/icon_menu_energy_highlighted.png";
import inventoryHighlighted from "../../../images/menu/icon_menu_inventory_highlighted.png";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { useLocation } from "react-router-dom";

const iconNames = new Map();

iconNames.set("dashboard", dashboard);
iconNames.set("transfers", transfers);
iconNames.set("repairs", repairs);
iconNames.set("maintenance", maintenance);
iconNames.set("incidents", incidents);
iconNames.set("issues", issues);
iconNames.set("operators", operators);
iconNames.set("disposal", disposal);
iconNames.set("assets", assets);
iconNames.set("energy", energy);
iconNames.set("inventory", inventory);

const iconNamesHighlighted = new Map();

iconNamesHighlighted.set("dashboard", dashboardHighlighted);
iconNamesHighlighted.set("transfers", transfersHighlighted);
iconNamesHighlighted.set("repairs", repairsHighlighted);
iconNamesHighlighted.set("maintenance", maintenanceHighlighted);
iconNamesHighlighted.set("incidents", incidentsHighlighted);
iconNamesHighlighted.set("issues", issuesHighlighted);
iconNamesHighlighted.set("operators", operatorsHighlighted);
iconNamesHighlighted.set("disposal", disposalHighlighted);
iconNamesHighlighted.set("assets", assetsHighlighted);
iconNamesHighlighted.set("energy", energyHighlighted);
iconNamesHighlighted.set("inventory", inventoryHighlighted);

const AppSubmenu = (props) => {
  const { t } = useTranslation();
  const [activeIndex, setActiveIndex] = useState(null);
  const dispatch = useDispatch();
  const [selectedMenuItemName, setSelectedMenuItemName] = useState(null);
  const [prevHoveredLabel, setPrevHoveredLabel] = useState(null);
  const location = useLocation();

  useEffect(() => {
    if (!props.isInteractive) {

    }
  }, [props.isInteractive]);

  useEffect(() => {
    if (!props.mobileMenuActive) {
      document.querySelectorAll(".layout-root-menuitem").forEach(function (item) {
        item.classList.remove("active-dropdown-mobile");
        item.removeAttribute("style");
      });
      setSelectedMenuItemName(null);
    }
  }, [props.mobileMenuActive]);

  useEffect(() => {
    document.querySelectorAll(".layout-menu-enter-done li").forEach((ele) => {
      ele.addEventListener("click", (e) => {
        e.target
          .closest(".layout-root-menuitem")
          .setAttribute("style", `margin-bottom: 0px !important`);
      });
    });

    document.querySelector(".layout-menu-container").addEventListener("scroll", (e) => {
      if (!isMobile()) {
        const selectedMenuItem = document.querySelector(".active-dropdown-mobile");
        const attachedSubMenu = document.querySelector(
          ".active-dropdown-mobile .layout-menu-enter-done"
        );
        if (attachedSubMenu) {
          attachedSubMenu.setAttribute(
            "style",
            `top: ${selectedMenuItem?.offsetTop - e.target?.scrollTop}px !important`
          );
        }
      }
    });

    window.addEventListener("resize", () => {
      if (isMobile()) {
        const attachedSubMenus = document.querySelectorAll(".layout-menu-enter-done");
        attachedSubMenus?.forEach(function (item) {
          item.removeAttribute("style");
        });
      }
      document.querySelectorAll("li.layout-root-menuitem").forEach((ele) => {
        ele.setAttribute("style", `margin-bottom: 0 px`);
      });
    });
  }, []);

  const onMenuItemClick = (event, item, index) => {
    if (item.disabled) {
      event.preventDefault();
      return;
    }
    //execute command
    if (item.command) {
      item.command({ originalEvent: event, item: item });
      event.preventDefault();
    }
    if (item.items) {
      event.preventDefault();
    }
    if (props.root) {
      props.onRootMenuitemClick({
        originalEvent: event,
      });
    }
    if (item.items) {
      setActiveIndex(index === activeIndex ? null : index);
    }

    props.onMenuitemClick({
      originalEvent: event,
      item: item,
    });

    event.target.closest("li.layout-root-menuitem").classList.remove("active-dropdown-mobile");
    event.stopPropagation();
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "menu_click" });
  };

  const onMenuItemMouseEnter = (index) => {
    if (props.root && props.menuActive && !isMobile()) {
      setActiveIndex(index);
    }
  };

  const visible = (item) => {
    return typeof item.visible === "function" ? item.visible() : item.visible !== false;
  };

  const isMobile = () => {
    return window.innerWidth <= 991;
  };

  const isSlim = useCallback(() => {
    return props.menuMode === "slim";
  }, [props.menuMode]);

  const isCompact = useCallback(() => {
    return props.isCompact;
  }, [props.isCompact]);

  const getLink = (item, index) => {
    const menuitemIconClassName = classNames(
      "layout-menuitem-icon",
      !!item.icon ? item.icon : "pi pi-fw"
    );
    let imageOrIcon = (
      <>
        {item.image && <img src={item.image} className={menuitemIconClassName} alt={item.label} />}
        {item.icon && <i className={menuitemIconClassName} />}
        {item.items && <i className="pi pi-fw pi-angle-down layout-submenu-toggler" />}
      </>
    );
    let label = (
      <span className={`layout-menuitem-text ${isCompact() && props.root && "p-d-none"}`}>
        {t(item.label)}
      </span>
    );
    let badge = item.badgeKey && props.badges[item.badgeKey] > 0 && (
      <span className={`p-badge p-ml-2 ${isCompact() && props.root && "p-badge-dot"}`}>
        {!(isCompact() && props.root) && props.badges[item.badgeKey]}
      </span>
    );

    // Display differently based on menu is in slim mode or not
    const content = isSlim() ? (
      // Slim mode
      props.root ? (
        <>
          <div className="p-overlay-badge">
            {imageOrIcon}
            {badge}
          </div>
          {label}
        </>
      ) : (
        <>
          {label}
          {badge}
        </>
      )
    ) : (
      <>
        {/* {imageOrIcon} */}
        {label}
        {badge}
      </>
    );
    const commonLinkProps = {
      style: item.style,
      className: classNames(
        item.class,
        "p-ripple",
        {
          "p-disabled": item.disabled,
          "p-link": !item.to,
        },
        isSlim() ? "p-pt-3" : "",
        isCompact() && props.root ? "p-pb-3" : ""
      ),
      target: item.target,
      onClick: (e) => onMenuItemClick(e, item, index),
      onMouseEnter: () => onMenuItemMouseEnter(index),
    };

    if (item.url) {
      return (
        <a href={item.url} rel="noopener noreferrer" {...commonLinkProps}>
          {content}
        </a>
      );
    } else if (!item.to) {
      return (
        <button type="button" {...commonLinkProps}>
          {content}
        </button>
      );
    }

    return (
      <NavLink to={item.to} activeClassName="active-route" {...commonLinkProps}>
        {content}
      </NavLink>
    );
  };

  const isMenuActive = (item, index) => {
    return (
      item.items &&
      (props.root && (!isSlim() || (isSlim() && (props.mobileMenuActive || activeIndex !== null)))
        ? true
        : activeIndex === index)
    );
  };

  const getItems = () => {
    const mobileDropdown = (e, itemLabel) => {
      e.target
        .closest("ul.layout-menu")
        .querySelectorAll("li.layout-root-menuitem")
        .forEach((ele) => {
          if (e.target !== ele) {
            ele.classList.remove("active-dropdown-mobile");
            setSelectedMenuItemName(null);
          }
          ele.setAttribute("style", `margin-bottom: 0 px`);
        });

      // if the previously hovered element is hovered again, make sure it still has the active styling
      // Users should still be able to toggle the active styling when clicking
      if (
        (prevHoveredLabel !== itemLabel || e.type === "click") &&
        e.target.classList.contains("active-dropdown-mobile")
      ) {
        e.target.classList.remove("active-dropdown-mobile");
      } else {
        e.target.classList.add("active-dropdown-mobile");
        setSelectedMenuItemName({ [itemLabel]: true });

        const attachedSubMenu = document.querySelector(
          ".active-dropdown-mobile .layout-menu-enter-done"
        );

        document.querySelectorAll("div.layout-content, div.topbar-right").forEach((element) => {
          element.addEventListener("click", (e) => {
            if (!isMobile()) {
              attachedSubMenu?.setAttribute("style", `display: none !important`);
              document
                .querySelector(".active-dropdown-mobile")
                ?.classList.remove("active-dropdown-mobile");
              setSelectedMenuItemName(null);
            }
          });
        });

        if (!isMobile()) {
          const menuContainer = document.querySelector(".layout-menu-container");

          if (attachedSubMenu) {
            attachedSubMenu.setAttribute(
              "style",
              `top: ${e.target.offsetTop - menuContainer.scrollTop}px !important`
            );
          }
        } else {
          if (e.target.classList.contains("active-dropdown-mobile")) {
            e.target.setAttribute("style", `margin-bottom: ${attachedSubMenu.clientHeight + 30}px`);
          }
        }
      }
      setPrevHoveredLabel(itemLabel);
    };

    const transitionTimeout = props.mobileMenuActive
      ? 0
      : isSlim() && props.root
      ? { enter: 400, exit: 400 }
      : props.root
      ? 0
      : { enter: 1000, exit: 450 };
    return props.items.map((item, i) => {
      if (visible(item)) {
        if (!item.separator) {
          const menuitemClassName = classNames({
            "layout-root-menuitem": props.root,
            "layout-root-menuitem-compact": isCompact() && props.root,
            "active-menuitem": activeIndex === i && !item.disabled,
            "active-root-menu": location.pathname.indexOf(item.to) !== -1 && props.root,
          });
          const link = getLink(item, i);
          const rootMenuItem = props.root && (
            <div className={`layout-root-menuitem `}>
              <div className="dot-indicator-container">
                <span className="dot-indicator" />
                <span className="dot-indicator" />
              </div>

              <img
                className="sidebar-mobile-icon"
                src={
                  (selectedMenuItemName && selectedMenuItemName[item.label]) ||
                  !location.pathname.indexOf(item.to)
                    ? iconNamesHighlighted.get(t(item.label).toLowerCase())
                    : iconNames.get(t(item.label).toLowerCase())
                }
                alt="n/a"
              />
              <div className="layout-menuitem-root-text" style={{ textTransform: "uppercase" }}>
                {t(item.label)}
                {props.root && props.badges[item.badgeKey] > 0 && (
                  <span className={`p-badge p-ml-2`}>{props.badges[item.badgeKey]}</span>
                )}
              </div>
              {/* <i className="pi pi-chevron-down" /> */}
            </div>
          );

          return (
            <li
              key={item.label || i}
              className={menuitemClassName}
              role="menuitem"
              onClick={(e) => {
                if(props.isInteractive){
                  mobileDropdown(e, item.label);
                }
                
              }}
              onMouseEnter={(e) => {
                if (!isMobile() && e.target.classList.contains("layout-root-menuitem") && props.isInteractive) {
                  mobileDropdown(e, item.label);
                }
              }}
            >
              {link}
              {rootMenuItem}
              <CSSTransition
                classNames="layout-menu"
                timeout={transitionTimeout}
                in={isMenuActive(item, i)}
                unmountOnExit
              >
                <AppSubmenu
                  items={visible(item) && item.items}
                  badges={props.badges}
                  menuActive={props.menuActive}
                  menuMode={props.menuMode}
                  isCompact={props.isCompact}
                  parentMenuItemActive={activeIndex === i}
                  onMenuitemClick={props.onMenuitemClick}
                />
              </CSSTransition>
            </li>
          );
        } else {
          return (
            <li
              className="menu-separator"
              style={item.style}
              key={`separator${i}`}
              role="separator"
            />
          );
        }
      }

      return null;
    });
  };

  useEffect(() => {
    if (!props.menuActive && isSlim()) {
      setActiveIndex(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.menuActive]);

  if (!props.items) {
    return null;
  }

  const items = getItems();
  return (
    <ul
      className={`layout-menu ${isCompact() && isSlim() && "layout-menu-compact"} ${
        !props.root && "layout-menu-enter-done"
      }`}
      role="menu"
    >
      {items}
    </ul>
  );
};

export default AppSubmenu;
