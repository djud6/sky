import React, { useState } from "react";
import axios from "axios";
import swal from "sweetalert";
import queryString from "query-string";
import * as Constants from "../../constants";
import { useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Dialog } from "primereact/dialog";
import { loadingAlert, errorAlert } from "../ShareComponents/CommonAlert";  // <== IMPORTA AQUI
import ConsoleHelper from "../../helpers/ConsoleHelper";
import "../../styles/LoginForm/newpwd.scss";
import "../../styles/dialogStyles.scss";

const RequestPwdConfirmation = (props) => {
  let history = useHistory();
  const { t } = useTranslation();
  const [visible, setVisible] = useState(true);

  const parsed = queryString.parse(props.location.search);

  const accept = () => {
    setVisible(false);
    loadingAlert();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/password-reset-complete/`, {
        token: parsed.token,
        uidb64: parsed.uidb64,
      })
      .then((res) => {
        successAlert();
      })
      .catch((err) => {
        ConsoleHelper(err);
        errorAlert(err.customErrorMsg, accept);
      });
  };

  const reject = () => {
    setVisible(false);
    history.push("/"); // ou outra ação para "cancelar"
  };

  const successAlert = () => {
    return swal({
      title: t("general.success"),
      text: t("loginForm.request_password_sent_text"),
      icon: "success",
      buttons: { return: t("general.return") },
    }).then((value) => {
      if (value === "return") {
        history.push("/");
      }
    });
  };

  const dialogFooter = (
    <div>
      <button className="p-button p-component p-button-text" onClick={reject}>
        {t("general.cancel")}
      </button>
      <button className="p-button p-component p-button-primary" onClick={accept}>
        {t("general.accept")}
      </button>
    </div>
  );

  return (
    <div className="new-pwd-wrapper">
      <div className="inner-wrapper">
        <Dialog
          visible={visible}
          style={{ width: "40vw" }}
          breakpoints={{ "1280px": "40vw", "960px": "65vw", "768px": "80vw", "500px": "90vw" }}
          header={t("loginForm.request_password_header")}
          footer={dialogFooter}
          onHide={reject}
          className="custom-main-dialog"
        >
          <p>{t("loginForm.request_password_body")}</p>
        </Dialog>
      </div>
    </div>
  );
};

export default RequestPwdConfirmation;
