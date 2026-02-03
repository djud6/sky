import { Howl, Howler } from "howler";
import { AUDIO_DATA_UPDATE, CTRL_AUDIO_PLAY } from "../types/audioTypes";

const addNewAudio = (audioName) => {
  return new Howl({
    src: [`${process.env.PUBLIC_URL}/assets/audio/${audioName}`],
    format: ["wav"],
    volume: 0.4,
    preload: true,
    pool: 10,
  });
};

let signInAudio = addNewAudio("sign-in.wav");
let menuClickAudio = addNewAudio("side-menu-click.wav");
let mainTabAudio = addNewAudio("main-tab.wav");
let tableDetailAudio = addNewAudio("details-view.mp3");
let subTabAudio = addNewAudio("sub-tabs.wav");
let submitAudio = addNewAudio("submit.wav");
let successAlertAudio = addNewAudio("success-msg.wav");
let errorAlertAudio = addNewAudio("error-msg.wav");
let warningAlertAudio = addNewAudio("warning-msg.wav");

const sound = localStorage.getItem("sound") === "1" ? true : false;

const initialState = {
  sound: sound,
  systemVolume: 0.4,
};

if (sound) {
  Howler.mute(false);
} else {
  Howler.mute(true);
}

export const audioReducer = (state = initialState, action) => {
  let currCtrlAudio;

  if (action.payload === "sign_in_audio") {
    currCtrlAudio = signInAudio;
  } else if (action.payload === "menu_click") {
    currCtrlAudio = menuClickAudio;
  } else if (action.payload === "main_tab") {
    currCtrlAudio = mainTabAudio;
  } else if (action.payload === "table_detail") {
    currCtrlAudio = tableDetailAudio;
  } else if (action.payload === "sub_tab") {
    currCtrlAudio = subTabAudio;
  } else if (action.payload === "submit") {
    currCtrlAudio = submitAudio;
  } else if (action.payload === "success_alert") {
    currCtrlAudio = successAlertAudio;
  } else if (action.payload === "error_alert") {
    currCtrlAudio = errorAlertAudio;
  } else if (action.payload === "warning_alert") {
    currCtrlAudio = warningAlertAudio;
  }

  switch (action.type) {
    case CTRL_AUDIO_PLAY:
      if (state.sound) currCtrlAudio.play();
      return state;

    case AUDIO_DATA_UPDATE:
      Howler.mute(!action.sound);
      if (action.systemVolume !== undefined) {
        Howler.volume(action.systemVolume);
        return { ...state, sound: action.sound, systemVolume: action.systemVolume };
      }

      return { ...state, sound: action.sound };

    default:
      return state;
  }
};
