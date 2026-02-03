import React from "react";
import { useDispatch } from "react-redux";
import { useHistory } from "react-router-dom";
import { CTRL_AUDIO_PLAY } from "../../redux/types/audioTypes";
import "../../styles/ShareComponents/QuickAccessTabs.scss";

const QuickAccessTabs = ({ tabs, activeTab, urls }) => {
  const history = useHistory();
  const dispatch = useDispatch();
  const onUrl = (url) => {
    history.push(url);
  };

  return (
    <div className="p-m-1">
      <div className="quick-access-tabs">
        {tabs.map((tab, index) => (
          <div
            id={tab}
            key={index}
            className={`
              access-tab
              ${tab === activeTab ? "active-tab" : ""}
            `}
            onClick={() => {
              dispatch({ type: CTRL_AUDIO_PLAY, payload: "main_tab" });
              onUrl(urls[index]);
            }}
          >
            <span>{tab}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default QuickAccessTabs;
