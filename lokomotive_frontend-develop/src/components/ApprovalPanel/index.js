import React, { useState, useEffect } from "react";
import axios from "axios";
import _ from "lodash";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { TabView, TabPanel } from "primereact/tabview";
import { faBell } from "@fortawesome/free-solid-svg-icons";
import * as Constants from "../../constants";
import { getAuthHeader } from "../../helpers/Authorization";
import CommonApprovalPanel from "./CommonApprovalPanel";
import PanelHeader from "../ShareComponents/helpers/PanelHeader";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import "../../styles/ShareComponents/Table/table.scss";
import "../../styles/ShareComponents/TabStyles/subTab.scss";

const ApprovalPanel = () => {
  const { t } = useTranslation();
  const [approvals, setApprovals] = useState([]);
  const [sentRequests, setSentRequests] = useState([]);
  const [dataReady, setDataReady] = useState(false);
  const [selectedApproval, setSelectedApproval] = useState(null);
  const [selectedSentRequest, setSelectedSentRequest] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    if (!!!dataReady) {
      setApprovals([]);
      setSentRequests([]);
      setSelectedApproval(null);
      setSelectedSentRequest(null);
      const cancelTokenSource = axios.CancelToken.source();
      let approvalRequest = axios.get(`${Constants.ENDPOINT_PREFIX}/api/v1/Approval/Get/Approve`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      });
      let sentRequestRequest = axios.get(
        `${Constants.ENDPOINT_PREFIX}/api/v1/Approval/Get/Requested`,
        { ...getAuthHeader(), cancelToken: cancelTokenSource.token }
      );
      axios
        .all([approvalRequest, sentRequestRequest])
        .then(
          axios.spread((...responses) => {
            const approvals = responses[0].data;
            const sentRequests = responses[1].data;
            for (var i in approvals) {
              if (approvals[i].is_approved === null) {
                approvals[i].is_approved = t("requestProgress.awaiting_approval");
                approvals[i].approval_status_code = 1;
              } else if (approvals[i].is_approved === true) {
                approvals[i].is_approved = t("approvalPanel.approved_label");
                approvals[i].approval_status_code = 3;
              } else {
                approvals[i].is_approved = t("approvalPanel.rejected_label");
                approvals[i].approval_status_code = 2;
              }
            }
            for (var y in sentRequests) {
              if (sentRequests[y].is_approved === null)
                sentRequests[y].is_approved = t("requestProgress.awaiting_approval");
              else if (sentRequests[y].is_approved === true)
                sentRequests[y].is_approved = t("approvalPanel.approved_label");
              else sentRequests[y].is_approved = t("approvalPanel.rejected_label");
            }
            setApprovals(approvals);
            setSentRequests(sentRequests);
            setDataReady(true);
          })
        )
        .catch((error) => {
          ConsoleHelper(error);
        });
      return () => {
        //Doing clean up work, cancel the asynchronous api call
        cancelTokenSource.cancel("cancel the asynchronous api call");
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataReady]);

  // Sort Approval Data
  let sortedApprovals = _.sortBy(approvals, (approval) => approval.approval_status_code);

  return (
    <div>
      <PanelHeader icon={faBell} text={t("approvalPanel.page_title")} />
      <TabView className="darkSubTab darkTable">
        <TabPanel
          header={`${
            isMobile
              ? t("approvalPanel.approval_tab_mobile").toUpperCase()
              : t("approvalPanel.approval_tab").toUpperCase()
          }`}
        >
          <CommonApprovalPanel
            requests={sortedApprovals}
            selectedRequest={selectedApproval}
            setSelectedRequest={setSelectedApproval}
            dataReady={dataReady}
            setDataReady={setDataReady}
            approvable
          />
        </TabPanel>
        <TabPanel
          header={`${
            isMobile
              ? t("approvalPanel.request_tab_mobile").toUpperCase()
              : t("approvalPanel.request_tab").toUpperCase()
          }`}
        >
          <CommonApprovalPanel
            requests={sentRequests}
            selectedRequest={selectedSentRequest}
            setSelectedRequest={setSelectedSentRequest}
            dataReady={dataReady}
            setDataReady={setDataReady}
          />
        </TabPanel>
      </TabView>
    </div>
  );
};

export default ApprovalPanel;
