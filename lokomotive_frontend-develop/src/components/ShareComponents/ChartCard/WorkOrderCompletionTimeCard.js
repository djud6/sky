import React from "react";
import { useTranslation } from "react-i18next";
import ChartCard from "../ChartCard/ChartCard";
import WorkOrderCompletionTimeChart from "./WorkOrderCompletionTimeChart";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";


const WorkOrderCompletionTimeCard = ({data, dataReady, error, height, }) => {
    const { t } = useTranslation();
    return (
        <ChartCard title={t("Work Order Completion Time")} 
        // tooltipName={"Check"}
        >
        {dataReady ? (
            error ? (
            <FullWidthSkeleton height={height} error />
            ) : (
                <div className="row no-gutters text-center">
                    <WorkOrderCompletionTimeChart
                        data={data}
                        height={height}
                    />
                </div>
            )
        ) : (
            <FullWidthSkeleton height={height} />
        )}
        </ChartCard>
    );
};

export default WorkOrderCompletionTimeCard;