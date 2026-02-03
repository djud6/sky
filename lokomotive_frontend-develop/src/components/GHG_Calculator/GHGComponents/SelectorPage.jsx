import React from "react";
import EmissionScopeTabs from "./EmissionScopeTabs";
import FleetSelector from "./FleetSelector";
import RegionSelector from "./RegionSelector";
import ScopeExplanation from "./ScopeExplanation";

const SelectorPage = () => {
    return (
        <>
            <EmissionScopeTabs />
            <RegionSelector />
            <FleetSelector />
            <ScopeExplanation />
        </>
    )
}

export default SelectorPage