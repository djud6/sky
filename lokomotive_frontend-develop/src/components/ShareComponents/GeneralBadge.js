import React from "react";
import { Tooltip } from "primereact/tooltip";
import { useTranslation } from "react-i18next";

const GeneralBadge = ({ data, colorTheme, tooltipContent }) => {
  const { t } = useTranslation();

  let colorClass = "badge-secondary";

  if (!colorTheme && data.toUpperCase() === t("general.yes").toUpperCase())
    colorClass = "badge-success";
  if (colorTheme) colorClass = colorTheme;

  return (
    <React.Fragment>
      <Tooltip target=".badgeTooptip" content={tooltipContent} />
      <span className={`badge badge-pill ${colorClass} ${tooltipContent ? "badgeTooptip" : ""}`}>
        {data}
      </span>
    </React.Fragment>
  );
};

export default GeneralBadge;
