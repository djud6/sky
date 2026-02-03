import React from "react";
import { useTranslation } from "react-i18next";
import GeneralBadge from "../../ShareComponents/GeneralBadge";
import "../../../styles/helpers/button5.scss";

const UserInfoCard = ({ userInfo }) => {
  const { t } = useTranslation();

  return (
    <React.Fragment>
      <div className="title">
        <span>{t("accountOptions.info_card_title")}</span>
      </div>
      <table className="table p-mb-2 p-mr-2" frame="void">
        <tbody>
          <tr>
            <th scope="row">{t("accountOptions.profile_first_name")}</th>
            <td>{userInfo.user.first_name}</td>
          </tr>
          <tr>
            <th scope="row">{t("accountOptions.profile_last_name")}</th>
            <td>{userInfo.user.last_name}</td>
          </tr>
          <tr>
            <th scope="row">{t("accountOptions.profile_role")}</th>
            <td className="text-capitalize">{userInfo.detailed_user.role_permissions.role}</td>
          </tr>
          <tr>
            <th scope="row">{t("accountOptions.profile_superuser")}</th>
            <td>
              {userInfo.user.is_superuser
                ? t("accountOptions.super_user")
                : t("accountOptions.normal_user")}
            </td>
          </tr>
          <tr>
            <th scope="row">{t("accountOptions.profile_active")}</th>
            <td>
              {userInfo.user.is_active ? (
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
            </td>
          </tr>
          <tr>
            <th scope="row">{t("accountOptions.profile_email")}</th>
            <td>{userInfo.user.email}</td>
          </tr>
          <tr>
            <th scope="row">{t("accountOptions.profile_costAllowance")}</th>
            <td>
              ${" "}
              {userInfo.detailed_user.cost_allowance
                ? userInfo.detailed_user.cost_allowance.toLocaleString()
                : "0.00"}
            </td>
          </tr>
          <tr>
            <th scope="row">{t("accountOptions.profile_business_unit")}</th>
            <td className="text-capitalize">
              {userInfo.detailed_user.business_unit
                ? userInfo.detailed_user.business_unit.name
                : t("general.not_applicable")}
            </td>
          </tr>
          <tr>
            <th scope="row">{t("accountOptions.profile_location")}</th>
            <td>
              {userInfo.detailed_user.location.map((location, idx) => {
                return (
                  <span key={idx} className="badge badge-pill badge-secondary p-mr-1">
                    {location.location_name}
                  </span>
                );
              })}
            </td>
          </tr>
        </tbody>
      </table>
    </React.Fragment>
  );
};

export default UserInfoCard;
