import { useEffect } from "react";
import ReactGA from "react-ga";
import "./custom.scss";
import { getAuthHeader } from "./helpers/Authorization";
import Spinner from "./components/ShareComponents/Spinner";
import { Suspense } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import PrimeInterface from "./routes/PrimeInterface";
import NoAuthRoute from "./routes/NoAuthRoute";
import smoothscroll from "smoothscroll-polyfill";
import { useSelector } from "react-redux";
import "primereact/resources/themes/saga-blue/theme.css";
import "primereact/resources/primereact.min.css";
import "primeicons/primeicons.css";

// kick off the smooth scroll polyfill!
smoothscroll.polyfill();

// Google Analytics setup
const GOOGLE_ANALYTICS_TRACKING_ID = "UA-192617522-1";
ReactGA.initialize(GOOGLE_ANALYTICS_TRACKING_ID);

const App = () => {
  useEffect(() => {
    ReactGA.pageview(window.location.pathname + window.location.search);

    //to clear query params on page refresh
    window.history.replaceState(null, "", window.location.pathname);
  }, []);

  const { platform } = useSelector((state) => state.apiCallData);
  let authHeader = getAuthHeader(() => platform);
  let screen = <NoAuthRoute />;
  if (authHeader !== null) {
    screen = <PrimeInterface />;
  }
  return (
    <Router>
      <Suspense fallback={<Spinner />}>{screen}</Suspense>
    </Router>
  );
};

export default App;
