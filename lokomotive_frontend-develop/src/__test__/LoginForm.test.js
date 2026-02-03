import React from "react";
import { shallow } from "enzyme";
import LoginForm from "../components/LoginForm";

describe("LoginForm Component", () => {
  test("Should render without crashing", () => {
    shallow(<LoginForm />);
  });
});
