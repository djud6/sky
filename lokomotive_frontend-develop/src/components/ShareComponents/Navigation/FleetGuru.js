import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import { InputText } from "primereact/inputtext";
import { fleetGuruContents } from "./FleetGuruContents";
import robotOn from "../../../images/menu/topbar_menu_robot_on.png";
import "../../../styles/helpers/button4.scss";

const FleetGuru = ({ setOnFleetGuru, setAssistantStatus }) => {
  const { t } = useTranslation();
  const [selectedTopic, setSelectedTopic] = useState("");
  const [filteredTopics, setFilteredTopics] = useState([]);
  const [searchField, setSearchField] = useState("");
  const isMobile = useMediaQuery({ query: `(max-width: 991px)` });

  useEffect(() => {
    if (searchField) {
      setSelectedTopic("");
      const filtered = fleetGuruContents.filter((content) => {
        return t(content.title).toLowerCase().includes(searchField.toLowerCase());
      });
      setFilteredTopics(filtered);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchField]);

  const handleClick = (event) => {
    const selected = event.target.id;
    setSelectedTopic(selected);
  };

  return (
    <div className="fleet-guru-container">
      <div className="header-search">
        <div className="gretting-msg">{t("fleetGuru.greeting_msg")}</div>
        <div className="search-bar">
          <div className="p-inputgroup">
            <Button icon="pi pi-search" />
            <InputText
              style={{ borderTopLeftRadius: 0, borderBottomLeftRadius: 0 }}
              placeholder={t("fleetGuru.searchbar_placeholder")}
              value={searchField}
              onChange={(e) => setSearchField(e.target.value)}
            />
          </div>
        </div>
      </div>
      <div className="content-field">
        {!searchField && !selectedTopic && (
          <div className="contents">
            <div className="header">{t("fleetGuru.default_header")}</div>
            {/* If no search input provided */}
            {fleetGuruContents.slice(0, 3).map((topic, index) => {
              return (
                <React.Fragment>
                  <div
                    key={index}
                    className="topic-title"
                    id={topic["scope"]}
                    onClick={handleClick}
                  >
                    {t(topic["title"])}
                    <i className="pi pi-chevron-right" style={{ fontSize: "16px" }} />
                  </div>
                  {index !== 2 && <hr />}
                </React.Fragment>
              );
            })}
            {!isMobile && (
              <Button
                className="assistant-back-btn"
                onClick={() => {
                  setOnFleetGuru(false);
                  setAssistantStatus(true);
                }}
              >
                <span>{t("fleetGuru.show_me_around")}</span>
                <div className="assistant-back-img">
                  <img src={robotOn} alt="" />
                </div>
              </Button>
            )}
          </div>
        )}
        {searchField && !selectedTopic ? (
          filteredTopics.length === 0 ? (
            <div className="contents">
              <div className="header text-center">{t("fleetGuru.no_topics_found")}</div>
            </div>
          ) : (
            <div className="contents">
              <div className="header">{t("fleetGuru.related_header")}</div>
              {filteredTopics.map((topic, index) => {
                return (
                  <React.Fragment>
                    <div
                      key={index}
                      className="topic-title"
                      id={topic["scope"]}
                      onClick={handleClick}
                    >
                      {t(topic["title"])}
                      <i className="pi pi-chevron-right" style={{ fontSize: "16px" }} />
                    </div>
                    {index !== filteredTopics.length - 1 && <hr />}
                  </React.Fragment>
                );
              })}
            </div>
          )
        ) : null}
        {selectedTopic && (
          <div className="topic-details">
            <div className="no-style-btn p-my-3">
              <Button
                label={t("general.back")}
                className="p-button-link"
                icon="pi pi-chevron-left"
                onClick={() => setSelectedTopic("")}
              />
            </div>
            <div className="artical">
              <div className="article-title">{t(`fleetGuru.title_${selectedTopic}`)}</div>
              <div className="article-details">{t(`fleetGuru.detail_${selectedTopic}`)}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FleetGuru;
