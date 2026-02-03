import axios from "axios";
import i18n from "i18next";
import { logout } from "./helpers/Authorization";
import ConsoleHelper from "./helpers/ConsoleHelper";


// Will handle all the api error and insert the custom error into customErrorMsg field
const apiErrorHandler = (error) => {
  // Any status codes that falls outside the range of 2xx cause this function to trigger

  // Deal with unauth error
  if (error?.response?.status === 401) {
    logout();
  }

  // Do something with response error msg
  let errorMsg = i18n.t("errorMsg.api_default");
  if (!!error && !!!error.response) {
    // network error
    errorMsg = i18n.t("errorMsg.network_issue");
  }

  // api server return error
  if (!!error && !!error.response && !!error.response.data) {
    errorMsg = error.response.data.error_message_user;
    ConsoleHelper(
      "Error code:" +
        error.response.data.error_code +
        " Error message:" +
        error.response.data.error_message_dev
    );
  }

  let customError = { ...error, customErrorMsg: errorMsg };
  return Promise.reject(customError);
};

axios.interceptors.response.use(
  (response) => response,
  (error) => apiErrorHandler(error)
);
