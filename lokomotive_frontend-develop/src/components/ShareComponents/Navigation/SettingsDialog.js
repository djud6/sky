import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { InputSwitch } from "primereact/inputswitch";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import { Slider } from "primereact/slider";
import { useTranslation } from "react-i18next";
import { updateAudioData } from "../../../redux/actions/audioControllAction";
import settings from "../../../images/menu/icon_sidebar_settings.png";
import "../../../styles/dialogStyles.scss";
import "../../../styles/Navigation/settingsDialog.scss";
import "../../../styles/helpers/slider1.scss";

function SettingsDialog({ setIsSettingsPanelDisplayed, configPanelPosition }) {
  const { t } = useTranslation();
  const { sound, systemVolume } = useSelector((state) => state.ctrlAudios);
  const [isSoundOn, setIsSoundOn] = useState(sound && localStorage.getItem("sound"));
  const dispatch = useDispatch();
  // the volume of Howl library is between 0 and 1, so we need to convert from our scale of 0 to 5
  const [volume, setVolume] = useState(systemVolume * 5);

  return (
    <Dialog
      className="custom-main-dialog sidebar-dialog"
      baseZIndex={1000}
      visible
      position={window.innerWidth > 991 ? "bottom-left" : ""}
      header={() => (
        <React.Fragment>
          <img src={settings} alt="settings" /> {t("settings.settings").toUpperCase()}
        </React.Fragment>
      )}
      footer={() => (
        <div style={{ textAlign: "center", color: "white" }}>
          <span>{t("settings.software_version")}</span>
          <br />
          <span>{t("settings.copy_rights")}</span>
        </div>
      )}
      onHide={() => {
        setIsSettingsPanelDisplayed(false);
        dispatch(updateAudioData(isSoundOn, volume));
      }}
      style={{
        left: configPanelPosition < 85 ? configPanelPosition * 3.5 : configPanelPosition * 2.2,
      }}
      breakpoints={{ "1280px": "40vw", "991px": "90vw" }}
      draggable={false}
    >
      <div className="options p-pt-2">
        <div className="p-mt-4">
          <React.Fragment>
            <div className="p-d-flex p-jc-between p-button-link">
              <span>{t("settings.sound_effects")}</span>
              <InputSwitch
                checked={isSoundOn}
                onChange={(e) => {
                  setIsSoundOn(e.value);
                  localStorage.setItem("sound", e.value);
                }}
              />
            </div>
            <div className="p-mt-2">
              <span>
                {t("settings.sound_volume")} : {volume}
              </span>
              <Slider
                value={volume}
                className="p-mt-2 p-mb-4"
                min={0}
                step={1}
                max={5}
                onChange={(e) => {
                  setVolume(e.value);
                }}
              />
            </div>
          </React.Fragment>
        </div>
        <hr />
        <Button className="p-d-flex p-jc-between p-button-link" onClick={() => {}}>
          <span>{t("settings.privacy_policy")}</span>
          <i className="pi pi-angle-right">{""}</i>
        </Button>
        <hr />
        <Button className="p-d-flex p-jc-between p-button-link" onClick={() => {}}>
          <span>{t("settings.help_and_faqs")}</span>
          <i className="pi pi-angle-right">{""}</i>
        </Button>
      </div>
    </Dialog>
  );
}

export default SettingsDialog;
