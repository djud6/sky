import React, { useState } from "react";
import axios from "axios";
import * as Constants from "../../constants";
import { getAuthHeader } from "../../helpers/Authorization";
import { useTranslation } from "react-i18next";
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { generalErrorAlert } from "../ShareComponents/CommonAlert";
import ConsoleHelper from "../../helpers/ConsoleHelper";

const AssetDetailsLog = ({ asset, setDataReady }) => {
  const { t } = useTranslation();
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);

  const sendComment = () => {
    setLoading(true);
    let commandRequest = {
      VIN: asset.VIN,
      content: comment,
    };
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .post(`${Constants.ENDPOINT_PREFIX}/api/v1/Asset/Add/Comment`, commandRequest, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        setComment("");
        setDataReady(false);
        setLoading(false);
      })
      .catch((error) => {
        setLoading(false);
        generalErrorAlert(error.customErrorMsg);
        ConsoleHelper(error);
      });
  }
  
  return (
    <div className="p-d-flex p-flex-column">
      <h4 className="font-weight-bold">{t("assetDetailPanel.new_comment_title")}</h4>
      <div className="p-mt-1 p-d-flex p-jc-between">
        <div className="asset-details-log">
          <InputText
            value={comment}
            placeholder={t("assetDetailPanel.new_comment_placeholder")}
            onChange={(e) => setComment(e.target.value)}
          />
        </div>
        <div className="asset-details-log-btn">
          <Button 
            label={t("general.send_btn")} 
            icon="pi pi-send"
            onClick={sendComment}
            disabled={!comment}
            loading={loading}
          />
        </div>
      </div>
    </div>
  )
}

export default AssetDetailsLog;