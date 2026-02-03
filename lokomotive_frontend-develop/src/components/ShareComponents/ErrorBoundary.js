import React from "react";
import * as Sentry from "@sentry/browser";
import ConsoleHelper from "../../helpers/ConsoleHelper";
import Error404 from "./Error404";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null, errorInfo: null, eventId: null };
  }

  componentDidUpdate(previousProps) {
    if (previousProps.location && (previousProps.location.pathname !== this.props.location.pathname)) {
      this.setState({ error: false, errorInfo: null, eventId: null });
    }
  }

  componentDidCatch(error, errorInfo) {
    ConsoleHelper(error);
    // Catch errors in any components below and re-render with error message
    this.setState({
      error: error,
      errorInfo: errorInfo,
    });
    Sentry.withScope((scope) => {
      scope.setExtras(errorInfo);
      const eventId = Sentry.captureException(error);
      this.setState({ eventId });
    });
  }

  render() {
    if (this.state.errorInfo) {
      // Error path
      if (this.state.error) {
        //render fallback UI
        return <Error404 />;
      } else {
        //when there's not an error, render children untouched
        return this.props.children;
      }
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
