import React, { useEffect, useState } from "react";
import { Toolbar } from "primereact/toolbar";
import { useTranslation } from "react-i18next";
import PartsCostTable from "./PartsCostTable";
import LaborCostTable from "./LaborCostTable";

const PartsLaborCostDetails = ({
  request,
  partsInfo = [],
  laborInfo = [],
  issues,
  maintenanceID,
  costDataReady,
  setCostDataReady,
}) => {
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

  const rightToolbarTemplate = () => {
    return (
      <div className="p-d-flex p-flex-column p-mr-2">
        <h5 className="p-mb-1 p-mt-2">
          {t("partsCost.parts_cost_subtotal")} &#36;{partsSum}
        </h5>
        <h5 className="p-mb-1 p-mb-2">
          {t("partsCost.parts_tax_subtotal")} &#36;{partsTaxSum}
        </h5>
        <h5 className="p-mb-1">
          {t("laborCost.labor_cost_subtotal")} &#36;{laborSum}
        </h5>
        <h5 className="p-mb-0">
          {t("laborCost.labor_tax_subtotal")} &#36;{laborTaxSum}
        </h5>
        <h3>
          {t("laborCost.total")} &#36;{totalAmount}
        </h3>
      </div>
    );
  };

  return (
    <div className="p-p-3">
      <div>
        <PartsCostTable
          request={request}
          partsInfo={partsInfo}
          issues={issues}
          maintenanceID={maintenanceID}
          costDataReady={costDataReady}
          setCostDataReady={setCostDataReady}
        />
      </div>
      <div className="p-mt-5">
        <LaborCostTable
          request={request}
          laborInfo={laborInfo}
          issues={issues}
          maintenanceID={maintenanceID}
          costDataReady={costDataReady}
          setCostDataReady={setCostDataReady}
        />
      </div>
      <Toolbar className="p-my-4" right={rightToolbarTemplate}>
        {""}
      </Toolbar>
    </div>
  );
};

export default PartsLaborCostDetails;
