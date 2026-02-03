import { GET_INIT_DATA, GET_USER_DATA } from "../types/apiCallTypes";

export const getInitInfo = (data) => (dispatch) => {
  dispatch({
    type: GET_INIT_DATA,
    payload: data,
  });
};

export const getUserInformation = (data) => (dispatch) => {
  dispatch({
    type: GET_USER_DATA,
    payload: data,
  });
};
