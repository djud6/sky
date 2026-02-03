import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { faCog } from "@fortawesome/free-solid-svg-icons";
import { faHardHat } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const PartsLaborCostMobile = ({ partsInfo = [], laborInfo = [] }) => {
  const { t } = useTranslation();
  const [totalAmount, setTotalAmount] = useState(false);
  const [partsSum, setPartsSum] = useState(0);
  const [partsTaxSum, setPartsTaxSum] = useState(0);
  const [laborSum, setLaborSum] = useState(0);
  const [laborTaxSum, setLaborTaxSum] = useState(0);

  useEffect(() => {
    setPartsSum(0);
    setLaborSum(0);
    let parts_sum = 0;
    let parts_taxes_sum = 0;
    let labor_sum = 0;
    let labor_taxes_sum = 0;
    let total_sum = 0;
    function taxesSubTotal(cost) {
      return cost.taxes;
    }
    function costSubTotal(cost) {
      return cost.total_cost;
    }
    function sum(prev, next) {
      return prev + next;
    }
    if (partsInfo.length > 0) {
      parts_sum = partsInfo.map(costSubTotal).reduce(sum);
      parts_taxes_sum = partsInfo.map(taxesSubTotal).reduce(sum);
    }
    if (laborInfo.length > 0) {
      labor_sum = laborInfo.map(costSubTotal).reduce(sum);
      labor_taxes_sum = laborInfo.map(taxesSubTotal).reduce(sum);
    }

    total_sum = parseFloat(parts_sum + labor_sum).toFixed(2);
    parts_sum = parts_sum - parts_taxes_sum;
    labor_sum = labor_sum - labor_taxes_sum;

    setPartsSum(parseFloat(parts_sum).toFixed(2));
    setPartsTaxSum(parseFloat(parts_taxes_sum).toFixed(2));
    setLaborSum(parseFloat(labor_sum).toFixed(2));
    setLaborTaxSum(parseFloat(labor_taxes_sum).toFixed(2));
    setTotalAmount(total_sum);
  }, [partsInfo, laborInfo]);

  return (
    <div className="cost-summary-panel">
      <div className="p-d-flex">
        <div className="overall-cost">${totalAmount}</div>
        <div className="parts-cost-container p-d-flex p-flex-column align-items-center">
          <FontAwesomeIcon className="parts-icon" icon={faCog} />
          <div className="parts-cost-label">{t("partsCost.parts_title_mobile").toUpperCase()}</div>
          <div className="parts-cost-value">${partsSum}</div>
          <div className="parts-cost-tax">${partsTaxSum}</div>
        </div>
        <div className="labour-cost-container p-d-flex p-flex-column align-items-center">
          <FontAwesomeIcon className="labour-icon" icon={faHardHat} />
          <div className="labour-cost-label">{t("laborCost.labor_title_mobile").toUpperCase()}</div>
          <div className="labour-cost-value">${laborSum}</div>
          <div className="labour-cost-tax">${laborTaxSum}</div>
        </div>
      </div>
    </div>
  );
};

export default PartsLaborCostMobile;
