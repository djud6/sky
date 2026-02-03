import React from "react";
import { useTranslation } from "react-i18next";
import { TabView, TabPanel } from "primereact/tabview";
import LinkedAssets from "./LinkedAssets";
import ChildrenHistory from "./ChildrenHistory";
import AggregateCost from "./AggregateCost";

const LinkedAssetTab = ({ asset, setForceUpdate }) => {
  const { t } = useTranslation();
  return (
    <div className="detail-cost-tab">
      <TabView className="darkSubTab-2">
        <TabPanel header={t("motherChildAsset.linked_asset_tab_title")}>
          <LinkedAssets asset={asset} setForceUpdate={setForceUpdate} />
        </TabPanel>
        <TabPanel header={t("motherChildAsset.history_of_children_tab_title")}>
          <ChildrenHistory asset={asset} setForceUpdate={setForceUpdate} />
        </TabPanel>
        <TabPanel header={t("motherChildAsset.aggregate_cost_title")}>
          <AggregateCost asset={asset} setForceUpdate={setForceUpdate} />
        </TabPanel>
      </TabView>
    </div>
  );
};

export default LinkedAssetTab;
