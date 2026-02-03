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

const VehicleUtilChartCard = ({chartParams, height}) => {

    const [chartOriginalData, setOriData] = useState(null);
    const [chartData, setChartData] = useState(null);
    const [dataReady, setDataReady] = useState(null);
    const [timeUnit, setTimeUnit] = useState("week");
    const [error, setError] = useState(null);

    const [startDate, setStartDate] = useState(new Date('2022-01-01'));
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
            .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Asset/Get/Utilization/${formatDate(startDate)}:${formatDate(endDate)}`, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                // setLocationTriggers(response.data);
                setDataReady({});
                const combinedData = combineData(response.data);
                setOriData(combinedData);
                const timeUnitSelected = timeUnit ? timeUnit : 'week';
                // const monthlyValues = combinedData['daily_averages'].daily_averages;
                let chartDataVal = null;
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
                setChartData(chartDataVal);
            })
            .catch((error) => {
                ConsoleHelper(error);
                setError(error);
            });
    };

    function combineData(data) {
        const combinedData = {
            "yearly_average_per_asset": {
                "yearly_average_per_asset_hour": 0.0,
                "yearly_average_per_asset_mileage": 0.0
            },
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
        combinedData.yearly_average_per_asset.yearly_average_per_asset_hour = data.Hours.yearly_average_per_asset.yearly_average_per_asset;
        combinedData.yearly_average_per_asset.yearly_average_per_asset_mileage = data.Mileage.yearly_average_per_asset.yearly_average_per_asset;

        // Combine daily averages
        data.Hours.daily_averages.daily_averages.forEach(hourEntry => {
            const mileageEntry = data.Mileage.daily_averages.daily_averages.find(mileageEntry => mileageEntry.date === hourEntry.date);
            if (!mileageEntry) {
                return;
            }
            combinedData.daily_averages.daily_averages.push({
                "date": new Date(hourEntry.date),
                "average_mileage_label": combinedData.yearly_average_per_asset.yearly_average_per_asset_hour,
                "average_hours_label": combinedData.yearly_average_per_asset.yearly_average_per_asset_mileage,
                "daily_average_per_asset_hour": hourEntry.daily_average_per_asset,
                "daily_average_per_asset_mileage": mileageEntry.daily_average_per_asset
            });
        });

        // Combine weekly averages
        data.Hours.weekly_averages.weekly_averages.forEach(hourEntry => {
            const mileageEntry = data.Mileage.weekly_averages.weekly_averages.find(mileageEntry =>
                mileageEntry.start_date === hourEntry.start_date);
            if (!mileageEntry) {
                return;
            }
            combinedData.weekly_averages.weekly_averages.push({
                // "start_date": hourEntry.start_date,
                // "end_date": hourEntry.end_date,
                "date": new Date(hourEntry.start_date),
                "average_mileage_label": combinedData.yearly_average_per_asset.yearly_average_per_asset_hour,
                "average_hours_label": combinedData.yearly_average_per_asset.yearly_average_per_asset_mileage,
                "weekly_average_per_asset_hour": hourEntry.weekly_average_per_asset,
                "weekly_average_per_asset_mileage": mileageEntry.weekly_average_per_asset
            });
        });

        // Combine monthly averages
        data.Hours.monthly_averages.monthly_averages.forEach(hourEntry => {
            const mileageEntry = data.Mileage.monthly_averages.monthly_averages.find(mileageEntry => mileageEntry.month === hourEntry.month);
            if (!mileageEntry) {
                return;
            }
            combinedData.monthly_averages.monthly_averages.push({
                // "month": hourEntry.month,
                "date": new Date(hourEntry.month + '-01'),
                "average_mileage_label": combinedData.yearly_average_per_asset.yearly_average_per_asset_hour,
                "average_hours_label": combinedData.yearly_average_per_asset.yearly_average_per_asset_mileage,
                "monthly_average_per_asset_hour": hourEntry.monthly_average_per_asset,
                "monthly_average_per_asset_mileage": mileageEntry.monthly_average_per_asset
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
                title={t("vehicleUtilChartCard.title")}
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
                                                chartName="vehicle-util"
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

export default VehicleUtilChartCard;
