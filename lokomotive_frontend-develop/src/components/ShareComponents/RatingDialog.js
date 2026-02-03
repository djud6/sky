import React, { useState } from "react";
import { Dialog } from "primereact/dialog";
import { Rating } from "primereact/rating";
import { Button } from "primereact/button";
import { useTranslation } from "react-i18next";
import CustomTextArea from "./CustomTextArea";
import "../../styles/ShareComponents/RatingDialog.scss";

function RatingDialog({ headerTitle, btn1Label, btn1Action, btn2Action }) {
  const { t } = useTranslation();
  const [dialogStatus, setDialogStatus] = useState(true);
  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState("");

  const renderFooter = () => {
    return (
      <div>
        <Button
          label={btn1Label}
          icon="pi pi-times"
          onClick={() => {
            setDialogStatus(false);
            btn1Action();
          }}
          className="p-button-text"
        />
        <Button
          label={t("general.submit")}
          icon="pi pi-check"
          onClick={() => {
            btn2Action(rating, feedback);
          }}
          disabled={!rating}
          autoFocus
        />
      </div>
    );
  };

  return (
    <Dialog
      className="custom-main-dialog"
      header={headerTitle}
      visible={dialogStatus}
      onHide={() => setDialogStatus(false)}
      style={{ width: "40vw" }}
      breakpoints={{ "1440px": "75vw", "980px": "85vw", "600px": "90vw" }}
      footer={renderFooter}
      closable={false}
    >
      <div className="p-field">
        <label>{t("general.rating")}</label>
        <Rating
          value={rating}
          className="custom-rating-icon"
          onChange={(e) => setRating(e.value)}
        />
      </div>
      <div className="p-field">
        <label>{t("general.feedback")}</label>
        <CustomTextArea
          className="w-100"
          rows={5}
          value={feedback}
          required
          onChange={setFeedback}
          leftStatus
        />
      </div>
    </Dialog>
  );
}

export default RatingDialog;
