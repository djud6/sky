import React from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { RadioButton } from "primereact/radiobutton";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { 
  faChartArea, 
  faScrewdriver, 
  faTag, 
  faDonate,
  faRecycle,
  faTimesCircle,
  faHandHoldingUsd
} from "@fortawesome/free-solid-svg-icons";
import * as Constants from "../../../constants";
import CardWidget from "../../ShareComponents/CardWidget";

const DisposalMethod = ({ disposalMethod, setDisposalMethod }) => {
  const { t } = useTranslation();
  const isBigScreen = useMediaQuery({ query: "(min-width: 1290px)" });
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const disposalMethods = [
    {name: t("removalPanel.company_directed_sale"), key: 'C', icon: faChartArea}, 
    {name: t("removalPanel.auction"), key: 'A', icon: faTag}, 
    {name: t("removalPanel.donate"), key: 'D', icon: faDonate}, 
    {name: t("removalPanel.repurpose"), key: 'R', icon: faRecycle},
    {name: t("removalPanel.scrap"), key: 'S', icon: faScrewdriver},
    {name: t("removalPanel.write_off"), key: 'W', icon: faTimesCircle},
    {name: t("removalPanel.trade_in"), key: 'T', icon: faHandHoldingUsd}
  ];

  return (
    <React.Fragment>
      <div className="disposal-method-form p-sm-12 p-md-12 p-lg-6 p-xl-6">
        <h5 className="p-mb-3">
          {t("removalPanel.disposal_method_title")}
        </h5>
        <CardWidget status={Object.keys(disposalMethod).length!==0} YN blueBg>
          <label className="h5">
            {t("removalPanel.disposal_method_label")}
          </label>
          <div className="p-d-flex p-flex-wrap p-mt-3">
          {disposalMethods.map((method, index) => {
            return (
              <div key={index} className={`method-items-outer ${isBigScreen ? "w-50" : "w-100"}`}>
                <div 
                  key={method.key} 
                  className={`method-items ${disposalMethod.key === method.key ? "selected" : ""}`}
                >
                  <RadioButton 
                    inputId={method.key}
                    name="replacementResaon" 
                    value={method}
                    onChange={(e) => setDisposalMethod(e.value)}  
                    checked={disposalMethod.key === method.key}
                  />
                  <FontAwesomeIcon 
                    className="p-ml-3 p-mr-2" 
                    icon={method.icon} 
                    color={`${disposalMethod.key === method.key ? "#ffffff" : "#c4c4c4"}`}
                  />
                  <label className="p-mb-0" htmlFor={method.key}>{method.name}</label>
                </div>
              </div>
            )
          })}
          </div>
        </CardWidget>
      </div>
      {!isMobile && <div className="p-sm-12 p-md-12 p-lg-6 p-xl-6">{""}</div>}
    </React.Fragment>
  )
}

export default DisposalMethod;