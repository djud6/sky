import i18next from "i18next";
import swal from "sweetalert";
import { logout } from "../../helpers/Authorization";
import moment from "moment";
import { FRONTEND_BUFF_TIME } from "../../constants";
import "../../styles/swalOverrides.scss";

export const loadingAlert = (lonadingTitle) => {
  return swal({
    title: lonadingTitle ? lonadingTitle : `${i18next.t("swal.loading_request")}`,
    text: `${i18next.t("swal.loading_text")}`,
    button: false,
    closeOnClickOutside: false,
    closeOnEsc: false,
  });
};

export const successAlert = (command = "", wholeMsg, confirmHandler = () => {}) => {
  return swal({
    title: `${i18next.t("swal.success")}`,
    text: wholeMsg ? wholeMsg : `${i18next.t("swal.request_success", { object: command })}`,
    icon: "success",
    buttons: { ok: true, cancel: false },
  }).then(() => {
    confirmHandler();
  });
};

export const errorAlert = (errorMsg, retryHandle) => {
  return swal({
    title: `${i18next.t("swal.error")}`,
    text: errorMsg,
    icon: "error",
    buttons: { resend: "Try Again", cancel: "Cancel" },
  }).then((value) => {
    if (value === "resend") retryHandle();
  });
};

export const generalErrorAlert = (errorMsg) => {
  return swal({
    title: `${i18next.t("swal.error")}`,
    text: errorMsg,
    icon: "error",
    buttons: { cancel: "Close" },
  });
};

export const timeoutAlert = (timeout, stayLoginHandle) => {
  let buff_time = FRONTEND_BUFF_TIME;

  let timeoutHandle = setTimeout(() => {
    logout();
  }, buff_time);

  let intervalHandle = setInterval(() => {
    document.getElementsByClassName("swal-text")[0].innerText = i18next.t(
      "swal.timeout_instruction",
      {
        buff_time: moment(moment.duration(buff_time).asMilliseconds()).format("mm:ss"),
      }
    );
    buff_time = buff_time - 1000;
  }, 1000);

  return swal({
    title: i18next.t("swal.timeout_warning"),
    icon: "error",
    text: `${i18next.t("swal.timeout_instruction", {
      buff_time: moment(moment.duration(buff_time).asMilliseconds()).format("mm:ss"),
    })}`,
    dangerMode: true,
    buttons: {
      confirm: `${i18next.t("swal.logout_button")}`,
      cancel: `${i18next.t("swal.stay_login_button")}`,
    },
  }).then((value) => {
    if (value) logout();
    else stayLoginHandle();
    clearTimeout(timeoutHandle);
    clearInterval(intervalHandle);
  });
};
