import React, {useEffect, useState} from "react";
import {useTranslation} from "react-i18next";
import ChartCard from "./ChartCard";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";
import DatePicker from "../../DatePicker/DateRangePicker";
import "../../../styles/ShareComponents/ChartCard/AvgMaintenanceChartCard.scss";
import axios from "axios";
import * as Constants from "../../../constants";
import {getAuthHeader} from "../../../helpers/Authorization";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import PieChart from "./CustomPieChart";
import SolidGaugeChart from "./SolidGaugeChart";

const MTBFChartCard = ({chartParams, height}) => {

    const [chartOriginalData, setOriData] = useState(null);
    const [chartData, setChartData] = useState(null);
    const [dataReady, setDataReady] = useState(null);
    const [timeUnit, setTimeUnit] = useState("week");
    const [error, setError] = useState(null);

    const [startDate, setStartDate] = useState(new Date('2022-01-01'));
    const [endDate, setEndDate] = useState(new Date());

    const {t} = useTranslation();

    const onRangeChanged = (range) => {
        range = range[0];
        if (null !== range.endDate && null !== range.startDate) {
            setStartDate(range.startDate);
            setEndDate(range.endDate);
            setDataReady(null);
        }
    };

    const dateRangePicker = dataReady ? (
        <div className="w-50">
            <DatePicker
                startDate={startDate}
                endDate={endDate}
                onRangeChanged={onRangeChanged}
            />
        </div>
    ) : null;

    const all_filter = dataReady ? (
        <div>
            {dateRangePicker}
        </div>
    ) : null;

    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${month}-${day}-${year}`;
    }

    const getData = () => {
        if (!startDate || !endDate) {
            return;
        }
        const cancelTokenSource = axios.CancelToken.source();
        axios
            .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Get/MeanTimeBetweenFailure/${formatDate(startDate)}:${formatDate(endDate)}`, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                setDataReady({});

                const dataTransfer = [];

                const full = 100;
                const all_value = response.data.total_repair_count + response.data.total_incidence_count + response.data.mean_days_between_failures;
                const repair_percent = response.data.total_repair_count / all_value * 100;
                const incidence_percent = response.data.total_incidence_count / all_value * 100;
                const mtbf_percent = response.data.mean_days_between_failures / all_value * 100;

                dataTransfer.push({label: 'Repair', data: repair_percent, full: full});
                dataTransfer.push({label: 'Incidence', data: incidence_percent, full: full});
                dataTransfer.push({label: 'Mean Days Between Failure', data: mtbf_percent, full: full});

                setChartData(dataTransfer)
            })
            .catch((error) => {
                ConsoleHelper(error);
                setError(error);
            });
    };
    // useEffect

    useEffect(() => {
        getData()
    }, [startDate, endDate])

    useEffect(() => {
        getData()
    }, [timeUnit])

    useEffect(() => {
    }, [chartData])

    // let labels;  let colors = ["#32D500", "#FD291C", "#FD7A22", "#1A76C4", "#404040"];
    let labels;
    let colors = ["#32D500", "#FD7A22", "#1A76C4", "#404040"];


    useEffect(() => {
        if (dataReady && chartData) {
            // eslint-disable-next-line
            labels = chartData.map((chartData) => chartData.label);
        }
    }, [dataReady]);

    return (
        <div className="chartcard-dropdown h-100">
            <ChartCard
                title={t("MTBFChartCard.title")}
                filter={all_filter}
                // tooltipName={"leader_board"}
            >
                {
                    dataReady && chartData ? (
                            !error ? (
                                <div className="p-d-flex p-flex-column">
                                    <div className="p-px-5 p-mt-3 avg-m-chart" style={{height: height}}>
                                        <div className="row no-gutters text-center">
                                            <br/>
                                            <SolidGaugeChart
                                                data={chartData}
                                                innerRadius={35}
                                                labels={labels}
                                                colors={colors}
                                                size={"350px"}
                                                legend={false}
                                                fontSize={11.5}
                                                isMobile
                                                withoutPercent={true}
                                            />
                                        </div>
                                    </div>
                                </div>
                            ) : <FullWidthSkeleton height={height}/>
                        ) :
                        <FullWidthSkeleton height={height}/>
                }
            </ChartCard>
        </div>
    );
};

export default MTBFChartCard;
