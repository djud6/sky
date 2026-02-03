import React from 'react';
import { useTranslation } from "react-i18next";

const IssueTypeBadge = ({ issueType, isCritical }) => {
    const { t } = useTranslation();
    let colorClass;
    if (typeof issueType !== "undefined") {
        issueType === t("general.critical")
            ? colorClass = "badge-danger"
            : colorClass = "badge-warning"
    }
    if (typeof isCritical !== "undefined") {
        isCritical
            ? colorClass = "badge-danger" 
            : colorClass = "badge-warning";
    };
    //when repair.is_critical doesn't exist (non-critical repairs case) make sure "badge-warning" applies
    if (typeof issueType === "undefined" && typeof isCritical === "undefined") {
        colorClass = "badge-warning";
    };

    return (
        <span className={`badge badge-pill ${colorClass}`}>
            { 
                colorClass === "badge-danger"
                ? t("general.critical")
                : t("general.non_critical")
                }
        </span>
    )
}

export default IssueTypeBadge;
