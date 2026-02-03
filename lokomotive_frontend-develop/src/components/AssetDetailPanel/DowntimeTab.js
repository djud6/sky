import React, { useEffect, useState } from "react";
import axios from "axios";
import { useMediaQuery } from "react-responsive";
import { getAuthHeader } from "../../helpers/Authorization";
import * as Constants from "../../constants";
import { useTranslation } from "react-i18next";
import SecondaryInfoView from "../ShareComponents/DetailView/SecondaryInfoView";
import FullWidthSkeleton from "../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import DowntimeChartCard from "../ShareComponents/ChartCard/DowntimeChartCard";
import ConsoleHelper from "../../helpers/ConsoleHelper";

const DowntimeTab = ({ vin }) => {
  const { t } = useTranslation();
  const [data, setData] = useState(null);
  const [downtime, setDowntime] = useState(null);
  const [dataReady, setDataReady] = useState(false);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Accident/Downtime/Asset/${vin}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        setData(response.data);
        const params = [
          {
            data: response.data["percent_non_preventable"],
            label: t("downTime.non_preventable_hours"),
            full: 100,
          },
          {
            data: response.data["percent_preventable"],
            label: t("downTime.preventable_hours"),
            full: 100,
          },
        ];
        setDowntime(params);
        setDataReady(true);
      })
      .catch((error) => {
        ConsoleHelper(error);
      });
    return () => {
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vin, dataReady]);

  let secondaryInfoTitles = [
    t("downTime.non_preventable_hours"),
    t("downTime.percent_non_preventable"),
    t("downTime.preventable_hours"),
    t("downTime.percent_preventable"),
  ];
  let secondaryInfoValues = [];
  if (data) {
    secondaryInfoValues = [
      data.non_preventable_hours,
      `${data.percent_non_preventable.toFixed(2)}%`,
      data.preventable_hours,
      `${data.percent_preventable.toFixed(2)}%`,
    ];
  }

  return (
    <div className={`${isMobile ? "p-mb-5 p-mt-3" : "p-mt-5"}`}>
      {data ? (
        <div className="p-mx-2">
          <div>
            <h5 className="downtime-tab-title p-mb-3">{t("downTime.fleet_downtime_tab_title")}</h5>
            <div className="downtime-container p-mb-3">
              <SecondaryInfoView titles={secondaryInfoTitles} values={secondaryInfoValues} />
            </div>
          </div>
          {!(data.non_preventable_hours === 0 && data.preventable_hours === 0) && (
            <DowntimeChartCard
              chartParams={downtime}
              title={`${t("downTime.asset_downtime_title")} ${vin}`}
              dataReady={dataReady}
            />
          )}
        </div>
      ) : (
        <React.Fragment>
          <FullWidthSkeleton height="400px" />
        </React.Fragment>
      )}
    </div>
  );
};

export default DowntimeTab;
