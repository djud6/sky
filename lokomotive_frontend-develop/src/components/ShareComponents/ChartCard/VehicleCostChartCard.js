import React, {useState, useEffect} from "react";
import {useTranslation} from "react-i18next";
import ChartCard from "./ChartCard";
import LeaderboardChart from "./LeaderboardChart";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import "../../../styles/ShareComponents/ChartCard/ChartCard.scss";
import DatePicker from "../../DatePicker/DateRangePicker";
import avgBackground from "./avg-maintenance-img.png";
import "../../../styles/ShareComponents/ChartCard/AvgMaintenanceChartCard.scss";
import axios from "axios";
import * as Constants from "../../../constants";
import {getAuthHeader} from "../../../helpers/Authorization";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import MultipleAxesCard from "./MultipleAxesCard";

const VehicleCostChartCard = ({chartParams, height}) => {

    const [chartOriginalData, setOriData] = useState(null);
    const [chartData, setChartData] = useState(null);
    const [dataReady, setDataReady] = useState(null);
    const [timeUnit, setTimeUnit] = useState("day");
    const [error, setError] = useState(null);

    const [startDate, setStartDate] = useState(new Date('2023-05-01'));
    const [endDate, setEndDate] = useState(new Date());

    const {t} = useTranslation();

    const dateRangeFilter = dataReady ? (
        <FormDropdown
            className="w-100"
            defaultValue={'Day'}
            onChange={(code) => {
                if (code === 0) {
                    setTimeUnit('day');
                } else if (code === 1) {
                    setTimeUnit('week');
                } else if (code === 2) {
                    setTimeUnit('month');
                } else {
                    setTimeUnit('year');
                }
            }}
            options={
                [
                    {name: 'Day', code: 0},
                    {name: 'Week', code: 1},
                    {name: 'Month', code: 2},
                    // {name: 'Year', code: 3},
                ]
            }
            loading={!dataReady}
            disabled={!dataReady}
            dataReady={dataReady}
            plain_dropdown
        />
    ) : null;

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
            <br/>
            {dateRangeFilter}
        </div>
    ) : null;

    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    const getData = () => {
        if (!startDate || !endDate) {
            return;
        }
        const cancelTokenSource = axios.CancelToken.source();
        axios
            .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Assets/AverageCostPerUnit/${formatDate(startDate)}:${formatDate(endDate)}`, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                // setLocationTriggers(response.data);
                setDataReady({});
                const combinedData = combineData(response.data);
                setOriData(response.data);
                const timeUnitSelected = timeUnit ? timeUnit : 'day';
                // const monthlyValues = combinedData['daily_averages'].daily_averages;
                let chartDataVal;
                if (timeUnitSelected === 'year') {
                    // year, todo no year date return from BE
                    chartDataVal = [combinedData['yearly_average_per_asset']]
                } else if (timeUnitSelected === 'day') {
                    // day
                    chartDataVal = combinedData['daily_averages'].daily_averages;
                } else if (timeUnitSelected === 'month') {
                    chartDataVal = combinedData['monthly_averages'].monthly_averages;
                } else {
                    // default week
                    chartDataVal = combinedData['weekly_averages'].weekly_averages;
                }
                // console.log("chartDataVal", chartDataVal);
                setChartData(chartDataVal);
            })
            .catch((error) => {
                ConsoleHelper(error);
                setError(error);
            });
    };

    function combineData(data) {
        const combinedData = {
            "daily_averages": {
                "daily_averages": []
            },
            "weekly_averages": {
                "weekly_averages": []
            },
            "monthly_averages": {
                "monthly_averages": []
            }
        };

        // Combine yearly averages
        // combinedData.yearly_average_per_asset.yearly_average_per_asset_hour = data.Hours.yearly_average_per_asset.yearly_average_per_asset;
        // combinedData.yearly_average_per_asset.yearly_average_per_asset_mileage = data.Mileage.yearly_average_per_asset.yearly_average_per_asset;

        // Combine daily averages
        data.daily_costs.forEach(hourEntry => {
            combinedData.daily_averages.daily_averages.push({
                "date": new Date(hourEntry.date),
                "cost": hourEntry.cost,
                "average": data.average_cost_per_unit
            });
        });

        // Combine weekly averages
        data.weekly_costs.forEach(hourEntry => {
            combinedData.weekly_averages.weekly_averages.push({
                "date": new Date(hourEntry.start_date),
                "cost": hourEntry.cost,
                "average": data.average_cost_per_unit
            });
        });

        // Combine monthly averages
        data.monthly_costs.forEach(hourEntry => {
            combinedData.monthly_averages.monthly_averages.push({
                // "month": hourEntry.month,
                "date": new Date(hourEntry.start_date),
                "cost": hourEntry.cost,
                "average": data.average_cost_per_unit
            });
        });

        return combinedData;
    }

    // useEffect

    useEffect(() => {
        getData()
    }, [startDate, endDate])

    useEffect(() => {
        getData()
    }, [timeUnit])

    useEffect(() => {
    }, [chartData])

    return (
        <div className="chartcard-dropdown h-100">
            <ChartCard
                title={t("vehicleCostChartCard.title")}
                subTitle={chartOriginalData ? `Average Asset Cost: $${chartOriginalData.average_cost_per_unit.toFixed(2)}` : null}
                filter={all_filter}
                // tooltipName={"leader_board"}
            >
                {
                    dataReady && chartData ? (
                            !error ? (
                                <div className="p-d-flex p-flex-column">
                                    <div className="p-px-5 p-mt-3 avg-m-chart" style={{height: height}}>
                                        <div className="row no-gutters text-center">
                                            <MultipleAxesCard
                                                chartParams={chartData}
                                                height={height}
                                                timeUnit={timeUnit}
                                                chartName="vehicle-cost"
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

export default VehicleCostChartCard;
