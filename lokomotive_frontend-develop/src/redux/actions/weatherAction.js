import { GET_WEATHER_DATA, GET_WEATHER_ERROR } from "../types/weatherTypes";
import axios from 'axios';
import * as Constants from "../../constants";

export const getWeatherData = (latitude, longitude) => async dispatch => {
  try {
    const res = await axios.get(`${Constants.WEATHER_PREFIX}&lat=${latitude}&lon=${longitude}&appid=${Constants.WEATHER_SECRET}`)
    dispatch({
      type: GET_WEATHER_DATA,
      payload: res.data
    })
  }
  catch(error) {
    dispatch({
      type: GET_WEATHER_ERROR,
      payload: error
    })
  }
}