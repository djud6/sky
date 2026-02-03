import "react-app-polyfill/ie11";
import React from "react";
import ReactDOM from "react-dom";
import * as serviceWorker from "./serviceWorker";
import "./i18n";
import "./apiSetup";
import * as Sentry from "@sentry/react";
import { Integrations } from "@sentry/tracing";
import App from "./App";
import { Provider } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { store, persistor } from "./redux/store";

Sentry.init({
  dsn: "https://13077d74a9e949d2bc1a17e9277f16e6@o576493.ingest.sentry.io/5730114",
  autoSessionTracking: true,
  integrations: [new Integrations.BrowserTracing()],

  // Set tracesSampleRate to 1.0 to capture 100% of transactions for performance monitoring.
  // Recommend adjusting this value in production
  tracesSampleRate: 1.0,
  beforeSend: (event) => {
    if (window.location.hostname === "localhost") {
      return null;
    }
    return event;
  },
});

ReactDOM.render(
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <App />
    </PersistGate>
  </Provider>,
  document.getElementById("root")
);

serviceWorker.unregister();
