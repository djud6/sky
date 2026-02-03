import React from "react";
import { shallow } from "enzyme";
import RemoveAssetPanel from "../components/RemovalPanel";

describe("RemovePanel Component", () => {
  test("Should render without crashing", () => {
    shallow(<RemoveAssetPanel />);
  });
});
