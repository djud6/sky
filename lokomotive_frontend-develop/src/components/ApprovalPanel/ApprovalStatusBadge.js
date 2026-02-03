import React from "react";
import { useTranslation } from "react-i18next";

const ApprovalStatusBadge = ({ isApproved }) => {
  const { t } = useTranslation();
  let colorClass;
  if (isApproved.toLowerCase() === t("requestProgress.awaiting_approval").toLowerCase()) {
    colorClass = "badge-secondary";
  } else if (isApproved.toLowerCase() === t("approvalPanel.approved_label").toLowerCase()) {
    colorClass = "badge-success";
  } else {
    colorClass = "badge-danger";
  }

  return <span className={`badge badge-pill ${colorClass}`}>{isApproved}</span>;
};

export default ApprovalStatusBadge;
