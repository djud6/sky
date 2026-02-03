import React from "react";
import { mount } from "enzyme";
import AssetDetailPanel from "../components/AssetDetailPanel";
import { MemoryRouter } from "react-router-dom";
import IssuesTab from "../components/AssetDetailPanel/IssuesTab";
import RepairsTab from "../components/AssetDetailPanel/RepairsTab";
import MaintenanceTab from "../components/AssetDetailPanel/MaintenanceTab";
import IncidentsTab from "../components/AssetDetailPanel/IncidentsTab";

describe("AssetDetailPanel component", () => {
  test("Renders all tabs", () => {
    const wrapper = mount(
      <MemoryRouter initialentries={["/asset-details/TEST_VIN_1"]}>
        <AssetDetailPanel />
      </MemoryRouter>
    );
    expect(
      wrapper.containsAllMatchingElements([
        <IssuesTab />,
        <RepairsTab />,
        <MaintenanceTab />,
        <IncidentsTab />,
      ])
    ).toEqual(true);
  });
});
