import React from "react";
import axios from "axios";
import { getAuthHeader } from "../helpers/Authorization";
import { ENDPOINT_PREFIX } from "../constants/index";
import ConsoleHelper from "../helpers/ConsoleHelper"

async function FetchData(url, authHeader, cancelTokenSource) {
  const res = await axios.get(`${ENDPOINT_PREFIX}/${url}`, {
    ...authHeader,
    cancelToken: cancelTokenSource.token,
  });
  return res.data;
}

function useRequestedData(urlArray) {
  const [dataArray, setDataArray] = React.useState([]);
  const [dataReady, setDataReady] = React.useState(false);
  const [errors, setErrors] = React.useState(null);

  const cancelTokenSource = axios.CancelToken.source();
  React.useEffect(() => {
    const authHeader = getAuthHeader();
    if (typeof urlArray === "string") {
      FetchData(urlArray, authHeader, cancelTokenSource)
        .then((response) => {
          setDataArray(response);
          setDataReady(true);
        })
        .catch((err) => {
          ConsoleHelper("error", err);
          setErrors(err.customErrorMsg);
          setDataReady(true);
        });
    } else {
      const responceData = urlArray.map((url) => FetchData(url, authHeader, cancelTokenSource));
      Promise.allSettled(responceData)
        .then((results) => {
          results.forEach((result, i) => {
            if (result.status === "fulfilled") {
              setDataArray((prev) => [...prev, result.value]);
            } else {
              setDataArray((prev) => [...prev, undefined]);
              setErrors((prev) => ({ ...prev, [i]: result.reason }));
            }
          });
        })
        .finally(() => setDataReady(true));
    }

    return () => {
      //Doing clean up work, cancel the asynchronous api call
      cancelTokenSource.cancel("cancel the asynchronous api call from custom hook");
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(urlArray)]);

  if (typeof urlArray === "string") return [dataReady, dataArray, errors];
  else return [dataReady, ...dataArray, errors];
}

export { useRequestedData };