import React, { useEffect, useRef } from "react";
import VINLink from "../helpers/VINLink";
import { useTranslation } from "react-i18next";
import worstRobot from "../../../images/robots/top5-kpi/worst-perform.png";
import bestRobot from "../../../images/robots/top5-kpi/best-perform.png";
import "../../../styles/ShareComponents/ChartCard/leaderboardChartStyle.scss";

const LeaderboardChart = ({ chartParams, width }) => {
  const { t } = useTranslation();
  const leadboard = useRef(null);
  let parentNode = leadboard.current?.parentNode?.parentNode;
  let leadboardNode = leadboard.current;
  let totalHeight = parentNode?.offsetHeight;

  useEffect(() => {
    if (leadboardNode && width) {
      let leadboardHeight = leadboardNode.offsetHeight;
      let restHeight = 0;

      const nodes = [...parentNode?.childNodes];
      nodes.forEach((node, index) => {
        if (index !== nodes.length - 1) {
          restHeight += node.offsetHeight;
        }
      });
      let chartHeight = totalHeight - restHeight;

      if (leadboardHeight > chartHeight) {
        let scaleVal = Math.floor((chartHeight / leadboardHeight) * 10) / 10;
        let translateVal = (leadboardHeight - leadboardHeight * scaleVal) / 2 + 10;

        leadboardNode.style.transform = `translateY(-${translateVal}px) scale(${scaleVal})`;
      } else {
        leadboardNode.style.transform = `translateY(0) scale(1)`;
      }
    }
  }, [parentNode, leadboardNode, width, totalHeight]);

  return (
    <div className="leaderboard-container" ref={leadboard}>
      <div className="p-d-flex p-flex-wrap p-col-12">
        <div className="p-sm-12 p-md-12 p-lg-12 p-xl-6 p-d-flex table-outer-container">
          <div className="perform-robot-img perform-robot-img-worst">
            <img src={worstRobot} alt="fleet_guru_worst" />
          </div>
          <div className="board-table">
            <div className="title">{t("leaderboardChart.worst_performing")}</div>
            <div className="table-container">
              <div className="table-title table-title-worst p-d-flex">
                <div className="row-left">{t("general.vin")}</div>
                <div className="row-right">{t("leaderboardChart.number_of_issues")}</div>
              </div>
              {chartParams
                .slice(-5)
                .reverse()
                .map((item, index) => {
                  return (
                    <div key={index}>
                      <div className="table-row p-d-flex">
                        <div className="row-left">
                          <VINLink classnames="text-white" vin={item[0]} />
                        </div>
                        <div className="row-right">{item[1]}</div>
                      </div>
                      <hr />
                    </div>
                  );
                })}
            </div>
          </div>
        </div>
        <div className="p-sm-12 p-md-12 p-lg-12 p-xl-6 p-d-flex table-outer-container">
          <div className="board-table">
            <div className="title">{t("leaderboardChart.best_performing")}</div>
            <div className="table-container">
              <div className="table-title table-title-best p-d-flex">
                <div className="row-left">{t("general.vin")}</div>
                <div className="row-right">{t("leaderboardChart.number_of_issues")}</div>
              </div>
              {chartParams.slice(0, 5).map((item, index) => {
                return (
                  <div key={index}>
                    <div className="table-row p-d-flex">
                      <div className="row-left">
                        <VINLink classnames="text-white" vin={item[0]} />
                      </div>
                      <div className="row-right">{item[1]}</div>
                    </div>
                    <hr />
                  </div>
                );
              })}
            </div>
          </div>
          <div className="perform-robot-img perform-robot-img-best">
            <img src={bestRobot} alt="fleet_guru_worst" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeaderboardChart;
