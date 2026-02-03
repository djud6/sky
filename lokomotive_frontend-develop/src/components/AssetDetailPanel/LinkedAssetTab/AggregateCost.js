import React, { useState, useEffect } from "react";
import axios from "axios";
import * as Constants from "../../../constants";
import { useMediaQuery } from "react-responsive";
import { useTranslation } from "react-i18next";
import useWindowSize from "../../ShareComponents/helpers/useWindowSize";
import moment from "moment";
import { getAuthHeader } from "../../../helpers/Authorization";
import DatePicker from "../../ShareComponents/DatePicker";
import Tooltip from "../../ShareComponents/Tooltip/Tooltip";
import LoadingAnimation from "../../ShareComponents/LoadingAnimation";
import AggregateCostTable from "./AggregateCostTable";
import "../../../styles/AssetDetailsPanel/AggregateCost.scss";

const AggregateCost = ({ asset }) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const { width } = useWindowSize();
  const [dataReady, setDataReady] = useState(false);
  const [dataLoading, setDataLoading] = useState(false);
  const [costData, setCostData] = useState(null);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [isMobileTable, setIsMobileTable] = useState(false);
  const breakPoint = { sm: 540, md: 768, lg: 1024 };

  useEffect(() => {
    const addClassName = (className) => {
      if (!dateClassList.contains(className)) {
        dateClassList.forEach((el) => {
          el.includes("custom-bp") && dateClassList.remove(el);
        });
        dateClassList.add(className);
      }
    };
    const rightWidth = document.querySelector(".asset-details-more-body")?.offsetWidth;
    const dateClassList = document.querySelector(".date-search-container")?.classList;

    if (rightWidth && dateClassList) {
      if (rightWidth > breakPoint.lg) {
        setIsMobileTable(false);
        addClassName("custom-bp-xl");
      } else {
        setIsMobileTable(true);
        if (rightWidth > breakPoint.md) {
          addClassName("custom-bp-lg");
        } else if (rightWidth > breakPoint.sm && rightWidth <= breakPoint.md) {
          addClassName("custom-bp-md");
        } else addClassName("custom-bp-sm");
      }
    } else {
      if (isMobile && dateClassList) {
        setIsMobileTable(true);
        if (width > breakPoint.sm && width <= breakPoint.md) {
          addClassName("custom-bp-md");
        } else addClassName("custom-bp-sm");
      }
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [width]);

  useEffect(() => {
    setDataReady(false);
    if (asset && startDate && endDate) {
      const cancelTokenSource = axios.CancelToken.source();
      const aggregateCostAPI = `${
        Constants.ENDPOINT_PREFIX
      }/api/v1/Asset/Get/AssetAndChildrenCosts/VIN/${asset.VIN}/${moment(startDate).format(
        "YYYY-MM-DD"
      )}:${moment(endDate).format("YYYY-MM-DD")}`;
      setDataLoading(true);
      axios
        .get(aggregateCostAPI, {
          ...getAuthHeader(),
          cancelToken: cancelTokenSource.token,
        })
        .then((res) => {
          setDataLoading(false);
          setDataReady(true);
          setCostData(res.data);
        })
        .catch((err) => {
          console.log(err);
          setDataLoading(false);
          setDataReady(false);
        });
    }
  }, [asset, startDate, endDate]);
  return (
    <div
      className={`linked-asset-container aggregate-cost-container ${
        !isMobile ? "p-mt-5" : "p-mt-3"
      }`}
    >
      <div className="row date-search-container">
        <div className="p-d-flex p-ai-center form-select-date p-my-2">
          <div className="select-date-title form-tooltip">
            <span className="p-d-flex p-flex-row">
              {t("general.from")}
              <Tooltip
                label={"start-date-tooltip"}
                description={t("maintenanceForecastPanel.tooltip_date_start")}
              />
            </span>
          </div>
          <DatePicker onChange={setStartDate} initialDate={startDate} />
        </div>
        <div className="p-d-flex p-ai-center form-select-date p-my-2">
          <div className="select-date-title form-tooltip">
            <span className="p-d-flex p-flex-row">
              {t("general.to")}
              <Tooltip
                label={"end-date-tooltip"}
                description={t("maintenanceForecastPanel.tooltip_date_end")}
              />
            </span>
          </div>
          <DatePicker onChange={setEndDate} initialDate={endDate} minDate={startDate} />
        </div>
      </div>
      {dataReady ? (
        <div className="p-mb-5">
          <div className="section-table">
            <AggregateCostTable costData={costData} width={width} isMobileTable={isMobileTable} />
          </div>
        </div>
      ) : dataLoading ? (
        <LoadingAnimation />
      ) : null}
    </div>
  );
};

export default AggregateCost;
