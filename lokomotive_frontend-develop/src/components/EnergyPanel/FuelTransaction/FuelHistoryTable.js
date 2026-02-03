import React, { useState, useEffect } from "react";
import axios from "axios";
import { getAuthHeader } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import { capitalize } from "../../../helpers/helperFunctions";
import Table from "../../ShareComponents/Table/Table";
import FuelOrderDetails from "../FuelOrdersHistory/FuelOrderDetails";
import Spinner from "../../ShareComponents/Spinner";
import { isMobileDevice } from "../../../helpers/helperFunctions";
import ConsoleHelper from "../../../helpers/ConsoleHelper";

const FuelHistoryTable = ({ vin }) => {
    const isMobile = isMobileDevice();
    const [dataReady, setDataReady] = useState(false);
    const [fuelHistory, setFuelHistory] = useState(null);
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [mobileDetails, setMobileDetails] = useState(false);

    useEffect(() => {
        const cancelTokenSource = axios.CancelToken.source();
        axios
            .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Fuel/Get/Costs/VIN/${vin}`, {
                ...getAuthHeader(),
                cancelToken: cancelTokenSource.token,
            })
            .then((response) => {
                const fuelHistory = response.data.map((data) => {
                    data.fuel_type = capitalize(data.fuel_type);
                    data.volume_unit = capitalize(data.volume_unit);
                    return data;
                });
                setFuelHistory(fuelHistory);
                setDataReady(true);
            })
            .catch((error) => {
                setDataReady(true);
                ConsoleHelper(error);
            });
        return () => {
            cancelTokenSource.cancel("cancel the asynchronous api call");
        };
    }, [vin]);

    useEffect(() => {
        if (selectedOrder) {
            setMobileDetails(true);
        }
    }, [selectedOrder]);

    let fuelHistoryHeaders;
    let fuelTableData;

    if (dataReady && fuelHistory) {
        fuelHistoryHeaders = [
            {
                header: "Fuel type",
                colFilter: {
                    field: "fuel_type",
                    filterOptions: {
                        filterAs: "dropdown",
                    },
                },
            },
            { header: "Volume", colFilter: { field: "volume" } },
            {
                header: "Volume Unit",
                colFilter: {
                    field: "volume_unit",
                    filterOptions: {
                        filterAs: "dropdown",
                    },
                },
            },
            { header: "Total Cost", colFilter: { field: "total_cost" } },
            { header: "Taxes", colFilter: { field: "taxes" } },
            {
                header: "Currency",
                colFilter: {
                    field: "currency",
                    filterOptions: {
                        filterAs: "dropdown",
                    },
                },
            },
        ];
        fuelTableData = fuelHistory.map((order) => {
            return {
                id: order.id,
                dataPoint: order,
                cells: [
                    order.fuel_type,
                    order.volume,
                    order.volume_unit,
                    order.total_cost.toFixed(2),
                    order.taxes.toFixed(2),
                    order.currency,
                ],
            };
        });
    }
    return (
        <React.Fragment>
            {dataReady && fuelHistory ? (
                isMobile ? (
                    <React.Fragment>
                        {selectedOrder && mobileDetails ? (
                            <FuelOrderDetails
                                selectedOrder={selectedOrder}
                                setSelectedOrder={setSelectedOrder}
                                setMobileDetails={setMobileDetails}
                            />
                        ) : (
                            <div className="darkTable p-mb-5">
                                <Table
                                    tableHeaders={fuelHistoryHeaders}
                                    tableData={fuelTableData}
                                    dataReady={dataReady}
                                    onSelectionChange={(order) => setSelectedOrder(order)}
                                    hasSelection
                                />
                            </div>
                        )}
                    </React.Fragment>
                ) : (
                    <React.Fragment>
                        <div className={`darkTable`}>
                            <Table
                                tableHeaders={fuelHistoryHeaders}
                                tableData={fuelTableData}
                                dataReady={dataReady}
                                onSelectionChange={(order) => setSelectedOrder(order)}
                                hasSelection
                            />
                        </div>
                        {selectedOrder && (
                            <FuelOrderDetails
                                selectedOrder={selectedOrder}
                                setSelectedOrder={setSelectedOrder}
                                setMobileDetails={setMobileDetails}
                            />
                        )}
                    </React.Fragment>
                )
            ) : (
                <Spinner />
            )}
        </React.Fragment>
    );
};

export default FuelHistoryTable;
