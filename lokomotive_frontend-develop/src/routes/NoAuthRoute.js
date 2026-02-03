import React from "react";
import { BrowserRouter as Router, Switch, Route, Redirect } from "react-router-dom";
import LoginForm from "../components/LoginForm";
import RequestPwdConfirmation from "../components/LoginForm/RequestPwdConfirmation";

const NoAuthRoute = ({ authHeader }) => {
  return (
    <Router>
      <Switch>
        <Route exact path="/" component={LoginForm} />
        <Route
          exact
          path="/request-new-password"
          render={(props) => <RequestPwdConfirmation {...props} />}
        />
        <Route>{authHeader == null && <Redirect to="/" />}</Route>
      </Switch>
    </Router>
  );
};

export default NoAuthRoute;
