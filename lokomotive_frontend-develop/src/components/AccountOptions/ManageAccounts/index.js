import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { faUsers } from "@fortawesome/free-solid-svg-icons";
import { Button } from "primereact/button";
import AddUser from "./AddUser";
import EditUser from "./EditUser";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import "../../../styles/AccountOptions/ManageAccounts.scss";
import "../../../styles/helpers/button3.scss";

const ManageAccounts = ({updateUserInformation}) => {
  const [mode, setMode] = useState(null);
  const { t } = useTranslation();

  return (
    <div className="manage-accounts">
      <div className="header-container">
        <PanelHeader
          icon={faUsers}
          text={t("accountOptions.manage_account_title")}
          disableBg
        />
      </div>
      <div className="main-container">
        {!mode &&
          <div className="manage-options p-d-flex p-jc-around p-flex-wrap">
            <div 
              className="option-container img-add-user"
              onClick={() => setMode("addUser")}
            >
              <div className="footer-btn">
                <div className="btn-3 p-mr-4">
                  <Button
                    label={t("accountOptions.add_user_title")}
                    icon="pi pi-arrow-right"
                    iconPos="right"
                    onClick={() => setMode("addUser")}
                  />
                </div>
              </div>
            </div>
            <div 
              className="option-container img-edit-user"
              onClick={() => setMode("editUser")}
            >
              <div className="footer-btn">
                <div className="btn-3 p-mr-4">
                  <Button
                    label={t("accountOptions.edit_card_title")}
                    icon="pi pi-arrow-right"
                    iconPos="right"
                    onClick={() => setMode("editUser")}
                  />
                </div>
              </div>
            </div>
          </div>
        }
        {mode === "addUser" && <AddUser setMode={setMode} />}
        {mode === "editUser" && <EditUser setMode={setMode} updateUserInformation={updateUserInformation} />}
      </div>
    </div>
  );
};

export default ManageAccounts;
