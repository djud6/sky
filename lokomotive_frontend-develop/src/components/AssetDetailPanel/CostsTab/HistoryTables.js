import React, { useState, useEffect } from "react";
import axios from "axios";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { getAuthHeader } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import { capitalize } from "../../../helpers/helperFunctions";
import Spinner from "../../ShareComponents/Spinner";
import Table from "../../ShareComponents/Table/Table";
import ConsoleHelper from "../../../helpers/ConsoleHelper";

export const FuelHistory = ({ vin }) => {
  const [dataReady, setDataReady] = useState(false);
  const [fuelHistory, setFuelHistory] = useState(null);

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
      {
        header: "Date Created",
        colFilter: {
          field: "date_created",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },
      {
        header: "Date Modified",
        colFilter: {
          field: "date_modified",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
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
          moment(order.date_created).format("YYYY-MM-DD"),
          moment(order.date_modified).format("YYYY-MM-DD"),
        ],
      };
    });
  }
  return (
    <React.Fragment>
      {dataReady && fuelHistory ? (
        <div className={`darkTable`}>
          <Table
            tableHeaders={fuelHistoryHeaders}
            tableData={fuelTableData}
            dataReady={dataReady}
            globalSearch={false}
          />
        </div>
      ) : (
        <Spinner />
      )}
    </React.Fragment>
  );
};

export const InsuranceHistory = ({ vin }) => {
  const [dataReady, setDataReady] = useState(false);
  const [insuranceHistory, setInsuranceHistory] = useState(null);

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Insurance/Get/Costs/VIN/${vin}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        setInsuranceHistory(response.data);
        setDataReady(true);
      })
      .catch((error) => {
        ConsoleHelper(error);
        setDataReady(true);
      });
    return () => {
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [vin]);

  let insuranceHistoryHeaders;
  let insuranceTableData;
  if (dataReady && insuranceHistory) {
    insuranceHistoryHeaders = [
      {
        header: "Date Created",
        colFilter: {
          field: "date_created",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },
      {
        header: "Date Updated",
        colFilter: {
          field: "date_updated",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },

      { header: "Incident ID", colFilter: { field: "accident_custom_id" } },
      { header: "Deductible", colFilter: { field: "deductible" } },
      {
        header: "Total Cost",
        colFilter: {
          field: "total_cost",
        },
      },
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
    insuranceTableData = insuranceHistory.map((order) => {
      return {
        id: order.id,
        dataPoint: order,
        cells: [
          moment(order.date_created).format("YYYY-MM-DD"),
          moment(order.date_updated).format("YYYY-MM-DD"),
          order.accident_custom_id,
          order.deductible,
          order.total_cost,
          order.currency,
        ],
      };
    });
  }

  return (
    <React.Fragment>
      {dataReady && insuranceHistory ? (
        <div className={`darkTable`}>
          <Table
            tableHeaders={insuranceHistoryHeaders}
            tableData={insuranceTableData}
            dataReady={dataReady}
            globalSearch={false}
          />
        </div>
      ) : (
        <Spinner />
      )}
    </React.Fragment>
  );
};

export const RentalHistory = ({ vin }) => {
  const [dataReady, setDataReady] = useState(false);
  const [rentalHistory, setRentalHistory] = useState(null);

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Rental/Get/Costs/VIN/${vin}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        const history = response.data.map((data) => {
          if (data.maintenance_work_order) {
            data.request_id = `${data.maintenance_work_order}`
          } else if (data.repair_work_order) {
            data.request_id = `${data.repair_work_order}`
          } else if (data.accident_custom_id) {
            data.request_id = `${data.accident_custom_id}`
          } else if (data.VIN) {
            data.request_id = `Asset Rental`
          }
          return data;
        });
        setRentalHistory(history);
        setDataReady(true);
      })
      .catch((error) => {
        ConsoleHelper(error);
        setDataReady(true);
      });
    return () => {
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [vin]);

  let rentalHistoryHeaders;
  let rentalTableData;
  if (dataReady && rentalHistory) {
    rentalHistoryHeaders = [
      {
        header: "Date Created",
        colFilter: {
          field: "date_created",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },
      {
        header: "Date Updated",
        colFilter: {
          field: "date_updated",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },

      { header: "Request ID", colFilter: { field: "request_id" } },
      {
        header: "Total Cost",
        colFilter: {
          field: "total_cost",
        },
      },
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
    rentalTableData = rentalHistory.map((order) => {
      return {
        id: order.id,
        dataPoint: order,
        cells: [
          moment(order.date_created).format("YYYY-MM-DD"),
          moment(order.date_updated).format("YYYY-MM-DD"),
          order.request_id,
          order.total_cost,
          order.currency,
        ],
      };
    });
  }

  return (
    <React.Fragment>
      {dataReady && rentalHistory ? (
        <div className={`darkTable`}>
          <Table
            tableHeaders={rentalHistoryHeaders}
            tableData={rentalTableData}
            dataReady={dataReady}
            globalSearch={false}
          />
        </div>
      ) : (
        <Spinner />
      )}
    </React.Fragment>
  );
};

export const LicenseHistory = ({ vin }) => {
  const [dataReady, setDataReady] = useState(false);
  const [licenseHistory, setLicenseHistory] = useState(null);

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/License/Get/Costs/VIN/${vin}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        setLicenseHistory(response.data);
        setDataReady(true);
      })
      .catch((error) => {
        ConsoleHelper(error);
        setDataReady(true);
      });
    return () => {
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [vin]);

  let licenseHistoryHeaders;
  let licenseTableData;
  if (dataReady && licenseHistory) {
    licenseHistoryHeaders = [
      {
        header: "Date Created",
        colFilter: {
          field: "date_created",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },
      {
        header: "Date Modified",
        colFilter: {
          field: "date_modified",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },
      {
        header: "License Plate Renewal",
        colFilter: {
          field: "license_plate_renewal",
        },
      },
      { header: "License Registration", colFilter: { field: "license_registration" } },
      {
        header: "Total Cost",
        colFilter: {
          field: "total_cost",
        },
      },
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
    licenseTableData = licenseHistory.map((order) => {
      return {
        id: order.id,
        dataPoint: order,
        cells: [
          moment(order.date_created).format("YYYY-MM-DD"),
          moment(order.date_modified).format("YYYY-MM-DD"),
          order.license_plate_renewal,
          order.license_registration,
          order.total_cost,
          order.taxes,
          order.currency,
        ],
      };
    });
  }

  return (
    <React.Fragment>
      {dataReady && licenseHistory ? (
        <div className={`darkTable`}>
          <Table
            tableHeaders={licenseHistoryHeaders}
            tableData={licenseTableData}
            dataReady={dataReady}
            globalSearch={false}
          />
        </div>
      ) : (
        <Spinner />
      )}
    </React.Fragment>
  );
};


export const AcquisitionHistory = ({ vin }) => {
  const { t } = useTranslation();
  const [dataReady, setDataReady] = useState(false);
  const [acquisitionHistory, setAcquisitionHistory] = useState(null);

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Acquisition/Get/Costs/VIN/${vin}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        const costs = response.data.map((data) => {
          data.total_cost = data.total_cost.toFixed(2);
          data.taxes = data.taxes.toFixed(2);
          data.administrative_cost = data.administrative_cost.toFixed(2);
          data.misc_cost = data.misc_cost.toFixed(2);
          return data;
        });
        setAcquisitionHistory(costs);
        setDataReady(true);
      })
      .catch((error) => {
        ConsoleHelper(error);
        setDataReady(true);
      });
    return () => {
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [vin]);

  let tableHeaders;
  let tableData;
  if (dataReady && acquisitionHistory) {
    tableHeaders = [
      {
        header: t("costsTab.misc_cost"),
        colFilter: {
          field: "misc_cost",
        },
      },
      {
        header: t("costsTab.administrative_cost"),
        colFilter: {
          field: "administrative_cost",
        },
      },
      {
        header: t("costsTab.total_cost"),
        colFilter: {
          field: "total_cost",
        },
      },
      {
        header: t("costsTab.taxes"),
        colFilter: {
          field: "taxes",
        },
      },
      {
        header: t("general.date_created"),
        colFilter: {
          field: "date_created",
          filterOptions: { filterAs: "dateRange", dateFormat: "YYYY-MM-DD" },
        },
      },
      {
        header: t("general.created_by"),
        colFilter: {
          field: "created_by",
          filterOptions: {
            filterAs: "dropdown",
          },
        },
      },
    ];
    tableData = acquisitionHistory.map((order) => {
      return {
        id: order.id,
        dataPoint: order,
        cells: [
          order.misc_cost,
          order.administrative_cost,
          order.total_cost,
          order.taxes,
          moment(order.date_created).format("YYYY-MM-DD"),
          order.created_by,
        ],
      };
    });
  }

  return (
    <React.Fragment>
      {dataReady && acquisitionHistory ? (
        <div className={`darkTable`}>
          <Table
            tableHeaders={tableHeaders}
            tableData={tableData}
            dataReady={dataReady}
            globalSearch={false}
          />
        </div>
      ) : (
        <Spinner />
      )}
    </React.Fragment>
  );
};

export const DeliveryHistory = ({ vin }) => {
  const { t } = useTranslation();
  const [dataReady, setDataReady] = useState(false);
  const [deliveryHistory, setDeliveryHistory] = useState(null);

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api/v1/Delivery/Get/Costs/VIN/${vin}`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        const history = response.data.map((data) => {
          if (data.maintenance_work_order) {
            data.request_id = `${data.maintenance_work_order}`
          } else if (data.repair_work_order) {
            data.request_id = `${data.repair_work_order}`
          } else if (data.disposal_custom_id) {
            data.request_id = `${data.disposal_custom_id}`
          } else if (data.asset_request_custom_id) {
            data.request_id = `ID: ${data.asset_request_custom_id}`
          }
          return data;
        });
        setDeliveryHistory(history);
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

  let historyHeaders;
  let tableData;

  if (dataReady && deliveryHistory) {
    historyHeaders = [
      {
        header: t("costsTab.request_id"),
        colFilter: {
          field: "request_id",
        },
      },
      {
        header: t("costsTab.delivery_submit_label"),
        colFilter: {
          field: "price",
        },
      },
      {
        header: t("costsTab.taxes"),
        colFilter: {
          field: "taxes",
        },
      },
      {
        header: t("costsTab.total_cost"),
        colFilter: {
          field: "total_cost",
        },
      },
    ];

    tableData = deliveryHistory.map((history) => {
      return {
        id: history.id,
        dataPoint: history,
        cells: [
          history.request_id,
          history.price.toFixed(2),
          history.taxes.toFixed(2),
          history.total_cost.toFixed(2),
        ],
      };
    });
  }
  return (
    <React.Fragment>
      {dataReady && deliveryHistory ? (
        <div className={`darkTable`}>
          <Table
            tableHeaders={historyHeaders}
            tableData={tableData}
            dataReady={dataReady}
            globalSearch={false}
          />
        </div>
      ) : (
        <Spinner />
      )}
    </React.Fragment>
  );
};