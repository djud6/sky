import SecureLS from "secure-ls";
import {
  AUTH_HEADER_KEY,
  AUTH_ROLE_KEY,
  AUTH_USER_KEY,
  AUTH_AGREEMENT_KEY,
  ENCRYPTION_SECRET,
  AUTH_TOKEN_EXPIRE_KEY,
} from "../constants";
import axios from "axios";
import moment from "moment";
import * as Constants from "../constants";
import ConsoleHelper from "./ConsoleHelper";

const ls = new SecureLS({ encodingType: "des", encryptionSecret: ENCRYPTION_SECRET });
export function getAuthHeader(platform) {
  let token = null;
  try {
    token = ls.get(AUTH_HEADER_KEY);
  } catch (error) {
    ConsoleHelper(error);
    logout();
  }

  if (!!token && token.length !== 0) {
    if (platform) {
      const innerPlatform = platform();
      if (!innerPlatform || innerPlatform !== 'lokomotive') {
        logout();
        return null;
      }
    }
    return { auth: false, headers: { Authorization: `Token ${token}` } };
  } else {
    return null;
  }
}

export function setToken(newToken, expireDate) {
  ls.set(AUTH_HEADER_KEY, newToken);
  ls.set(AUTH_TOKEN_EXPIRE_KEY, expireDate);
}

export function getToken() {
  return ls.get(AUTH_HEADER_KEY);
}

export function setAuthHeader(newToken, expireDate, role, user) {
  ls.set(AUTH_HEADER_KEY, newToken);
  ls.set(AUTH_TOKEN_EXPIRE_KEY, expireDate);
  ls.set(AUTH_ROLE_KEY, role);
  ls.set(AUTH_USER_KEY, user);
}

export function setAgreementHeader(agreement) {
  ls.set(AUTH_AGREEMENT_KEY, agreement);
}

export function removeAuth() {
  ls.remove(AUTH_HEADER_KEY);
  ls.remove(AUTH_TOKEN_EXPIRE_KEY);
  ls.remove(AUTH_ROLE_KEY);
  ls.remove(AUTH_USER_KEY);
  ls.remove(AUTH_AGREEMENT_KEY);
}

export function getRolePermissions() {
  try {
    let role_permission = ls.get(AUTH_ROLE_KEY);
    if (!!!role_permission) logout();
    return role_permission;
  } catch (error) {
    ConsoleHelper(error);
    logout();
  }
}

export function getSuperUserPermission() {
  try {
    let superUser_permission = ls.get(AUTH_USER_KEY);
    return superUser_permission.is_superuser;
  } catch (error) {
    ConsoleHelper(error);
    logout();
  }
}

export function getUserInfo() {
  try {
    let user_info = ls.get(AUTH_USER_KEY);
    return {
      firstName: user_info.first_name,
      lastName: user_info.last_name,
      email: user_info.email,
    };
  } catch (error) {
    ConsoleHelper(error);
    logout();
  }
}

export function getAgreementStatus() {
  try {
    let agreement_status = ls.get(AUTH_AGREEMENT_KEY);
    return agreement_status;
  } catch (error) {
    ConsoleHelper(error);
    logout();
  }
}

export function getExpireDate() {
  return ls.get(AUTH_TOKEN_EXPIRE_KEY);
}

export function hasModulePermission(moduleName) {
  let role_permission = getRolePermissions();
  return !!role_permission ? role_permission[moduleName] : false;
}

export function logout() {
  removeAuth();
  window.location = "/";
  window.localStorage.clear();
  return null;
}

export function tokenRefresh() {
  let expireDate = getExpireDate();
  let timer = moment.duration(moment(expireDate).diff(moment())).as("seconds") * 1000;

  setTimeout(() => {
    axios
      .post(
        `${Constants.ENDPOINT_PREFIX}/api-auth/v1/Refresh`,
        {
          token: getToken(),
        },
        getAuthHeader()
      )
      .then((r) => {
        setToken(r.data.token, r.data.token_expiration);
        tokenRefresh();
      })
      .catch((e) => {
        ConsoleHelper(e);
      });
  }, timer);
}
