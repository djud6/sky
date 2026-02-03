import React from "react";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import RequestProgress from "../RequestProgress";
import "../../../styles/ShareComponents/DetailsView/DetailsViewMobile.scss";

const DetailsViewMobile = ({
  header,
  titles,
  values,
  description,
  additionalDescr,
  files,
  editBtn,
  onEdit,
  optionalActionGroup,
  actionBtn1,
  onActionBtn1,
  disabledBtn1,
  actionBtn2,
  onActionBtn2,
  disabledBtn2,
  progressSteps,
  progressContents,
  progressActive,
  enableMore,
  detailsSection,
  setMoreDetails,
  setDetailsSection,
}) => {
  const { t } = useTranslation();

  const setActiveSection = (section) => {
    setDetailsSection(section);
    setMoreDetails(true);
  };

  return (
    <div className="details-view-mobile">
      <h4 className="header">{header}</h4>
      <div className="p-d-flex p-flex-column">
        {titles &&
          titles.map((title, index) => {
            return (
              <div key={index} className="p-d-flex p-jc-between main-details">
                <span className="title">{title}</span>
                <span className="value">{values[index]}</span>
              </div>
            );
          })}
      </div>
      {description && (
        <div className="p-d-flex p-flex-column main-details description">
          <span className="title">{description[0]}</span>
          <span className="value">{description[1]}</span>
          {description[2] && <span className="value">{description[2]}</span>}
        </div>
      )}
      {files && files.length !== 0 ? (
        <div className="p-d-flex p-flex-column main-details files">
          <span className="title">{t("general.attached_files")}</span>
          {files.map((file, index) => {
            return (
              <span className="p-pb-1 value" key={index}>
                <a target="_blank" rel="noopener noreferrer" href={file.file_url}>
                  {file.file_name}
                </a>
              </span>
            );
          })}
        </div>
      ) : null}
      {additionalDescr && <div>{additionalDescr}</div>}
      {optionalActionGroup}
      {(editBtn || actionBtn1 || actionBtn2) && (
        <React.Fragment>
          <hr />
          <div className="p-mt-2 p-mb-3 p-d-flex p-flex-column">
            <h4 className="header-grey">{t("general.quick_actions")}</h4>
            {editBtn && (
              <div className="button-container detail-edit-btn">
                <Button
                  className="w-100"
                  icon="pi pi-pencil"
                  label={editBtn}
                  onClick={() => onEdit()}
                />
              </div>
            )}
            {actionBtn1 && (
              <div className={`button-container ${actionBtn1[2]}`}>
                <Button
                  className="w-100"
                  icon={`pi ${actionBtn1[1]}`}
                  label={actionBtn1[0]}
                  onClick={() => onActionBtn1()}
                  disabled={disabledBtn1}
                />
              </div>
            )}
            {actionBtn2 && (
              <div className={`button-container ${actionBtn2[2]}`}>
                <Button
                  className="w-100"
                  icon={`pi ${actionBtn2[1]}`}
                  label={actionBtn2[0]}
                  onClick={() => onActionBtn2()}
                  disabled={disabledBtn2}
                />
              </div>
            )}
          </div>
        </React.Fragment>
      )}
      {progressSteps && (
        <div className="p-mt-5">
          <hr />
          <h3 className="header-grey">{t("requestProgress.tab_title")}</h3>
          <div className="p-mt-5">
            <RequestProgress
              steps={progressSteps}
              contents={progressContents}
              activeStep={progressActive}
              layout="vertical"
            />
          </div>
        </div>
      )}
      {enableMore && (
        <div className="more-details">
          <hr />
          <h4 className="header-grey p-mb-4">{t("general.more_details")}</h4>
          {detailsSection.map((section, index) => {
            return (
              <div key={index} className="options">
                <Button
                  className="p-d-flex p-jc-between p-button-link"
                  onClick={() => setActiveSection(section)}
                >
                  <span>{section}</span>
                  <i className="pi pi-angle-right" style={{ fontSize: "1.5em" }}>
                    {""}
                  </i>
                </Button>
                {index !== detailsSection.length - 1 && <hr />}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default DetailsViewMobile;
