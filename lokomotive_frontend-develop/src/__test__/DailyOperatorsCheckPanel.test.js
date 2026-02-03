import React from "react";
import { mount, shallow } from "enzyme";
import DailyOperatorsCheckPanel from "../components/DailyOperatorsCheckPanel";
import VINSearch from "../components/ShareComponents/helpers/VINSearch";

describe("DailyOperatorsCheckPanel component", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test("Should render without crashing", () => {
    shallow(<DailyOperatorsCheckPanel />);
  });

  test("Should render VINSearch", () => {
    const wrapper = mount(<DailyOperatorsCheckPanel />);
    expect(wrapper.containsMatchingElement(<VINSearch />)).toEqual(true);
  });
});
