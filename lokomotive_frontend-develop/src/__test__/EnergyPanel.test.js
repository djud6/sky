import React from "react";
import { mount, shallow } from "enzyme";
import FuelTrackingPanel from "../components/EnergyPanel";
import PanelHeader from "../components/ShareComponents/helpers/PanelHeader";

describe("EnergyPanel component", () => {
  test("Should render without crashing", () => {
    shallow(<FuelTrackingPanel />);
  });

  test("Should render PanelHeader", () => {
    const wrapper = mount(<FuelTrackingPanel />);
    expect(wrapper.containsMatchingElement(<PanelHeader text="Fuel Tracking" />)).toEqual(true);
  });
});
