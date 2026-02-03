import React from "react";
import "../../styles/ShareComponents/AdditionalAlert.scss";

const AdditionalAlert = ({
  title,
  text,
  warningMsg,
  confirmBtn,
  cancelBtn,
  onConfirm,
  onCancel,
}) => {
  return (
    <div className="alert-overlay opac">
      <div className="alert-container">
        <i className="pi pi-exclamation-triangle" />
        {title && <p className="alert-primary-txt">{title}</p>}
        {text && <p className="alert-desc-txt">{text}</p>}
        {warningMsg && <p className="alert-primary-txt">{warningMsg}</p>}
        <div className="alert-button-cont">
          {cancelBtn && (
            <button onClick={onCancel} className="alert-no-btn">
              {cancelBtn}
            </button>
          )}
          {confirmBtn && (
            <button onClick={onConfirm} className="alert-yes-btn">
              {confirmBtn}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdditionalAlert;
