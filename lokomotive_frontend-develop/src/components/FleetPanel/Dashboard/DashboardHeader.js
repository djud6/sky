import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { faChartArea } from "@fortawesome/free-solid-svg-icons";
import { useDispatch, useSelector } from "react-redux";
import currentDate from "../../ShareComponents/helpers/CurrentDate";
import InfoCard from "../../ShareComponents/InfoCard";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import { getWeatherData } from "../../../redux/actions/weatherAction";
import "../../../styles/FleetPanel/DashboardHeader.scss";

const DashboardHeader = ({ userInfo, isOperator }) => {
  const dispatch = useDispatch();
  const { t } = useTranslation();
  const { timeRecorded, currentWeather } = useSelector((state) => state.weatherData);
  const [time, setTime] = useState(new Date());
  const [latitude, setLatitude] = useState(null);
  const [longitude, setLongitude] = useState(null);
  // Template reference: https://openweathermap.org/weather-conditions
  const weatherTemplate = {
    "Clear": { des: "Sunny", icon: process.env.PUBLIC_URL + "/assets/images/weather/sunny.png" },
    "Clouds": { des: "Cloudy", icon: process.env.PUBLIC_URL + "/assets/images/weather/cloudy.png" },
    "Snow": { des: "Snowy", icon: process.env.PUBLIC_URL + "/assets/images/weather/snowy.png" },
    "Rain": { des: "Rainy", icon: process.env.PUBLIC_URL + "/assets/images/weather/rainy.png" },
    "Drizzle": { des: "Drizzly", icon: process.env.PUBLIC_URL + "/assets/images/weather/drizzly.png" },
    "Thunderstorm": { des: "Thunderstorm", icon: process.env.PUBLIC_URL + "/assets/images/weather/thunderstorm.png" },
    "Mist": { des: "Misty", icon: process.env.PUBLIC_URL + "/assets/images/weather/misty.png" },
    "Smoke": { des: "Smoky", icon: process.env.PUBLIC_URL + "/assets/images/weather/misty.png" },
    "Haze": { des: "Hazy", icon: process.env.PUBLIC_URL + "/assets/images/weather/misty.png" },
    "Dust": { des: "Dusty", icon: process.env.PUBLIC_URL + "/assets/images/weather/dusty.png" },
    "Fog": { des: "Foggy", icon: process.env.PUBLIC_URL + "/assets/images/weather/misty.png" },
    "Sand": { des: "Sandy", icon: process.env.PUBLIC_URL + "/assets/images/weather/dusty.png" },
    "Ash": { des: "Ash", icon: process.env.PUBLIC_URL + "/assets/images/weather/ashy.png" },
    "Squall": { des: "Squall", icon: process.env.PUBLIC_URL + "/assets/images/weather/squall.png" },
    "Tornado": { des: "Tornado", icon: process.env.PUBLIC_URL + "/assets/images/weather/tornado.png" }
  }

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    navigator.geolocation.getCurrentPosition(function(position) {
      setLatitude(position.coords.latitude);
      setLongitude(position.coords.longitude);
    });

    return function cleanup() {
      clearInterval(timer);
    }
  }, []);

  useEffect(() => {
    if (latitude && longitude) {
      if (!timeRecorded) {
        dispatch(getWeatherData(latitude, longitude));
      } else {
        // Limit api call to 15 mins.
        const diff = Math.abs(Date.now() - timeRecorded);
        const minutes = Math.floor((diff/1000)/60);
        if (minutes > 15) dispatch(getWeatherData(latitude, longitude));
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [latitude, longitude])

  return (
    <div className="fleet-main-header">
      <div className="header-left">
        <PanelHeader
          icon={faChartArea}
          text={t("fleetPanel.welcome_back_userInfo_name", { userInfo_name: userInfo.first_name })}
          currentDate={"disabled"}
        />
        {!isOperator && <p className="info-text">{t("fleetPanel.greeting_message_1")}</p>}
      </div>
      <div className="header-right">
        <div className="weather-widget">
          <InfoCard>
            <div className="weather-widget-inner">
              <div className="weather-left">
                <div className="time">{currentDate()}</div>
                <div className="time">{time.toLocaleTimeString()}</div>
                <div className="description">
                  {currentWeather ?
                    <div>{weatherTemplate[currentWeather.weather[0].main]["des"]}</div>
                    :
                    <div>{"-----"}</div>
                  }
                </div>
                <div className="temp">
                  {currentWeather ? currentWeather.main.temp.toFixed() : "--"}
                  <span>&deg;</span>
                </div>
              </div>
              <div className="weather-right">
                <div className="loc-name">
                  {currentWeather ? currentWeather.name : "------"}
                </div>
                <div className="temp-range">
                  H:{currentWeather ? currentWeather.main.temp_max.toFixed() : "--"}<span>&deg;</span>
                  {"  "}
                  L:{currentWeather ? currentWeather.main.temp_min.toFixed() : "--"}<span>&deg;</span>
                </div>
              </div>
            </div>
          </InfoCard>
          <div className="weather-img">
            {currentWeather ?
              <img src={weatherTemplate[currentWeather.weather[0].main]["icon"]} alt="weather-icon" />
              :
              <img src={process.env.PUBLIC_URL + "/assets/images/weather/default.png"} alt="weather-icon" />
            }
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardHeader;