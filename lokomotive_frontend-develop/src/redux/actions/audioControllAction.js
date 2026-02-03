import axios from "axios";
import { AUDIO_DATA_UPDATE } from "../types/audioTypes";
import { getAuthHeader } from "../../helpers/Authorization";
import * as Constants from "../../constants";
import ConsoleHelper from "../../helpers/ConsoleHelper";

export const updateAudioData = (isSoundOn, volume) => async (dispatch) => {
  try {
    const volumePercentage = volume * 20;
    dispatch({
      type: AUDIO_DATA_UPDATE,
      sound: isSoundOn,
      systemVolume: volumePercentage / 100,
    });
    const { data } = await axios.get(`${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Info`, {
      ...getAuthHeader(),
    });

    const { sound, sound_percentage } = data.user_config;

    if (sound !== isSoundOn || volumePercentage !== sound_percentage) {
      const headers = getAuthHeader();
      headers.headers["Content-Type"] = "application/json";
      const data = { sound: isSoundOn, sound_percentage: volumePercentage };

      await axios.post(
        `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Update/Configuration`,
        data,
        headers
      );
    }
  } catch (error) {
    ConsoleHelper(error);
  }
};
