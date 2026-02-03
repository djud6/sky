import { GET_WEATHER_DATA, RESET_WEATHER_DATA, GET_WEATHER_ERROR } from "../types/weatherTypes";
import ConsoleHelper from "../../helpers/ConsoleHelper";

const initialState = {
  timeRecorded: null,
  currentWeather: null,
  error: null,
};

export const weatherReducer = (state = initialState, action = {}) => {
  switch (action.type) {
    case GET_WEATHER_DATA:
      return {
        ...state,
        currentWeather: action.payload,
        timeRecorded: Date.now(),
      };

    case RESET_WEATHER_DATA:
      return {
        ...state,
        timeRecorded: null,
        currentWeather: null,
        error: null,
      };

    case GET_WEATHER_ERROR:
      ConsoleHelper(action.payload);
      return {
        ...state,
        error: action.payload,
      };

    default:
      return state;
  }
};
