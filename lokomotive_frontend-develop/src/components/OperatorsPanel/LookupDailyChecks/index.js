import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { faCalendarCheck } from "@fortawesome/free-solid-svg-icons";
import InspectionsTable from "./InspectionsTable";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import "../../../styles/ShareComponents/Table/table.scss";

const LookupDailyChecksPanel = () => {
  const { t } = useTranslation();
  const [vehicle, setVehicle] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  return (
    <div>
      {isMobile && 
        <QuickAccessTabs
          tabs={["Daily Check", "Unfinished", "Lookup"]}
          activeTab={"Lookup"}
          urls={["/operators", "/operators/unfinished-checks", "/operators/lookup"]}
        />
      }
      <PanelHeader
        icon={faCalendarCheck}
        text={t("lookupDailyCheckPanel.page_title")}
      />
      {!isMobile && 
        <QuickAccessTabs
          tabs={["Daily Check", "Unfinished Checks", "Lookup"]}
          activeTab={"Lookup"}
          urls={["/operators", "/operators/unfinished-checks", "/operators/lookup"]}
        />
      }
      <div className={`${isMobile ? "p-pb-4" : "p-mt-5"}`}>
        <VINSearch
          onVehicleSelected={(v) => {
            setVehicle(v);
          }}
        />
      </div>
      <div className={`${isMobile ? "p-mt-3 p-mb-5" : "p-mt-5"}`}>
        <InspectionsTable vehicle={vehicle} />
      </div>
    </div>
  );
};

export default LookupDailyChecksPanel;
