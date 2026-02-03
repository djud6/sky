import React, { useState, useEffect, useRef } from "react";
import { useDispatch } from "react-redux";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { useTranslation } from "react-i18next";
import { Dropdown } from "primereact/dropdown";
import { Calendar } from "primereact/calendar";
import { InputText } from "primereact/inputtext";
import { InputNumber } from "primereact/inputnumber";
import { Slider } from "primereact/slider";
import moment from "moment";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import CustomInputText from "../CustomInputText";
import useWindowSize from "../helpers/useWindowSize";
import * as Constants from "../../../constants";
import LoadingAnimation from "../LoadingAnimation";
import { isMobileDevice, capitalize, validateEmail } from "../../../helpers/helperFunctions";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { useHistory } from "react-router-dom";
import axios from "axios";
import { getAuthHeader } from "../../../helpers/Authorization";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import { MultiSelect } from "primereact/multiselect";
// import "./Table.scss"
import "../../../styles/ShareComponents/datePicker.scss";
import logoBase64 from "../../../assets/base64/logo";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import { ToggleButton } from "primereact/togglebutton";
import { max } from "lodash";
import RangeSliderInput from "./RangeSliderInput";
import {disable} from "@amcharts/amcharts4/.internal/core/utils/Debug";

/**
 * Share table component with pagination and selection controls
 *
 * @param {Array} tableHeaders table column header title array as format [{header:"", colFilter: {filterField:"", filterOptions: {filterType:"", dateFormat:"", filterElement:object}}}] filterType have options: "dropdown", "date", "dateRange" and "custom"
 * @param {Array} tableData Table data array as format [{id:"", dataPoint: {} ,cells:[]}]
 * @param {Boolean} hasSelection Table have selection control or not
 * @param {Boolean} multipleSelection Table has multiple selection (you can select multiple rows)
 * @param {Function} onSelectionChange Call back on selection changed, the param will be {dataPoint}
 * @param {Object} pagination Table pagination params as format {totalPages:10, currentPage:1, onPageChangeHandle:callback}
 * @param {Boolean} dataReady Determine if the table will display spinner or not, default to true
 */
const Table = ({
  tableHeaders = [],
  tableData = [],
  onSelectionChange,
  hasSelection = false,
  multipleSelection = false,
  dataReady = true,
  hasExport = false,
  hasPdfExport = false,
  exportPdfColumns = [],
  rows,
  globalSearch = true,
  disableMobileDetail = false,
  tab = 0,
  persistPage = true,
  timeOrder = true,
  showSearchPref = true,
  showAssetCount = true,
  assets,
}) => {
  const [first, setFirst] = useState(0);
  const [realTableData, setRealTableData] = useState([]);
  const [total, setTotal] = useState(0);
  const [active, setActive] = useState(false);
  const [selectedRowData, setSelectedRowData] = useState(multipleSelection ? [] : null);
  const selectionMode = hasSelection ? (multipleSelection ? "multiple" : "single") : null;
  const [filters, setFilters] = useState({});
  const [globalFilter, setGlobalFilter] = useState(null);
  const dispatch = useDispatch();
  const dtRef = useRef(null);
  const wrapperRef = useRef(null);
  const { t } = useTranslation();
  const size = useWindowSize();
  let isMobile = size.width <= Constants.MOBILE_BREAKPOINT;
  let tableFilters = tableHeaders.map((item) => item.colFilter);
  const [saveFilterDialog, setSaveFilterDialog] = useState(false);
  const [searchPreference, setSearchPreference] = useState(null);
  const [searchPreferenceName, setSearchPreferenceName] = useState("");
  const [preferencesArray, setPreferencesArray] = useState([]);
  const [deleteFilterDialog, setDeleteFilterDialog] = useState(false);
  const [eventTypes, setEventTypes] = useState([]);
  const [checkedFilters, setCheckedFilters] = useState([]);
  const [eventTypeFilter, setEventTypeFilter] = useState([]);
  const [theAllFilter, setTheAllFilter] = useState(true);
  const history = useHistory();

  const [maxHourRange, setMaxHourRange] = useState(0);
  const [maxPriceRange, setMaxPriceRange] = useState(0);
  const [maxMileageRange, setMaxMileageRange] = useState(0);

  const [minPrice, setMinPrice] = useState(undefined);
  const [maxPrice, setMaxPrice] = useState(undefined);
  const priceGap = "1000";

  const [minHours, setMinHours] = useState(undefined);
  const [maxHours, setMaxHours] = useState(undefined);
  const hourGap = "500";

  const [minMileage, setMinMileage] = useState(undefined);
  const [maxMileage, setMaxMileage] = useState(undefined);
  const mileageGap = "500";

  useEffect(() => {
    if (tableData.length !== 0) {
      setRealTableData(tableData);
      // PriceFilterElement()
      // HoursFilterElement();
      setTotal(tableData.length || 0);

      setMinPrice((prev) => {
        if (prev === undefined) {
          return Math.min(...tableData.map((el) => el.dataPoint.total_cost));
        }
        return prev;
      });
      setMaxPrice((prev) => {
        if (prev === undefined) {
          return Math.max(...tableData.map((el) => el.dataPoint.total_cost));
        }
        return prev;
      });
      setMaxPriceRange(Math.max(...tableData.map((el) => el.dataPoint.total_cost)));

      setMinMileage((prev) => {
        if (prev === undefined) {
          return Math.min(
            ...tableData.map((el) => (el.dataPoint.mileage > -1 ? el.dataPoint.mileage : 0))
          );
        }
        return prev;
      });
      setMaxMileage((prev) => {
        if (prev === undefined) {
          return Math.max(...tableData.map((el) => el.dataPoint.mileage));
        }
        return prev;
      });
      setMaxMileageRange(Math.max(...tableData.map((el) => el.dataPoint.mileage)));

      setMinHours((prev) => {
        if (prev === undefined) {
          return Math.min(
            ...tableData.map((el) => (el.dataPoint.hours > -1 ? el.dataPoint.hours : 0))
          );
        }
        return prev;
      });
      setMaxHours((prev) => {
        if (prev === undefined) {
          return Math.max(...tableData.map((el) => el.dataPoint.hours));
        }
        return prev;
      });
      setMaxHourRange(Math.max(...tableData.map((el) => el.dataPoint.hours)));
    }
  }, [tableData]);

  const deletepreference = () => {
    const list = [];
    preferencesArray.map((item) => {
      list.push(item.label);
    });
    setEventTypes(list);
    setDeleteFilterDialog(true);
  };

  const onPageHandler = (e) => {
    if (active || e.first !== 0) {
      setFirst(e.first);
      if ("URLSearchParams" in window && persistPage) {
        let searchParams = new URLSearchParams(window.location.search);
        if (tab === 0) searchParams.set("page1", e.first);
        else searchParams.set("page2", e.first);
        let newRelativePathQuery = window.location.pathname + "?" + searchParams.toString();
        history.replace(newRelativePathQuery);
      }
    }
    setActive(true);
  };

  useEffect(() => {
    if ("URLSearchParams" in window && persistPage) {
      const urlParams = new URLSearchParams(window.location.search);
      const myParam = tab === 0 ? urlParams.get("page1") : urlParams.get("page2");
      if (myParam) setFirst(parseInt(myParam));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab]);

  //get table wrapper inital height and set as min height to avoid jumping
  useEffect(() => {
    if (!isMobileDevice()) {
      let initialHeight = wrapperRef.current.clientHeight;
      wrapperRef.current.style.minHeight = `${initialHeight}px`;
    }
  }, [dataReady]);

  //Reset state every time table is rerendered (via dataReady)
  useEffect(() => {
    setSelectedRowData(multipleSelection ? [] : null);
  }, [dataReady, multipleSelection]);

  const onSelectHandle = (event) => {
    setActive(true);
    setSelectedRowData(event.value);
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "table_detail" });

    let dataPoint = null;
    if (!multipleSelection) {
      //Single select logic
      if (!!event.value) {
        dataPoint = event.value.dataPoint;
      }
    } else {
      //Multiple Select logic
      dataPoint = event.value.map((rowData) => rowData.dataPoint);
    }
    onSelectionChange(dataPoint);
  };

  const bodyTemplate = (data, props) => {
    return (
      <React.Fragment>
        <span className="p-column-title">{props.header}</span>
        <span className="p-body-template">{data.cells[props.field]}</span>
      </React.Fragment>
    );
  };

  const filterFunction = (colIndex) => {
    let filterOption = tableFilters[colIndex]?.filterOptions;

    switch (filterOption?.filterAs) {
      case "dateRange":
        return (value, filter) => {
          let val = moment(value);
          let startDate = !!filter[0] ? moment(filter[0]) : undefined;
          let endDate = !!filter[1] ? moment(filter[1]) : undefined;
          return val.isBetween(startDate, endDate, undefined, "[]");
        };
      case "priceRange":
        return (value, filter) => {
          // Treats N/A values as 0
          if (value < 0) {
            value = 0;
          }
          return value >= filter.minPrice && value <= filter.maxPrice;
        };
      case "hourRange":
        return (value, filter) => {
          if (value < 0) {
            value = 0;
          }
          return value >= filter.minHours && value <= filter.maxHours;
        };
      case "mileageRange":
        return (value, filter) => {
          if (value < 0) {
            value = 0;
          }
          return value >= filter.minMileage && value <= filter.maxMileage;
        };
      default:
        return filterOption?.filterFunction;
    }
  };

  const filterElement = (colIndex) => {
    let filterOption = tableFilters[colIndex]?.filterOptions;

    switch (filterOption?.filterAs) {
      case "dropdown":
        return SelectFilterElement(colIndex);
      case "date":
        return DateFilterElement(colIndex, filterOption.dateFormat);
      case "dateRange":
        return DateFilterElement(colIndex, filterOption.dateFormat, true);
      case "priceRange":
        return PriceFilterElement(colIndex);
      case "hourRange":
        return HoursFilterElement(colIndex);
      case "mileageRange":
        return MileageFilterElement(colIndex);
      default:
        return tableFilters[colIndex]?.filterOptions?.filterElement;
    }
  };

  const monthNavigatorTemplate = (e) => {
    return (
      <Dropdown
        panelClassName="table-cal-dropdown"
        className="p-mx-1 w-auto"
        value={e.value}
        options={e.options}
        onChange={(event) => e.onChange(event.originalEvent, event.value)}
        style={{ lineHeight: 1 }}
      />
    );
  };

  const yearNavigatorTemplate = (e) => {
    return (
      <Dropdown
        panelClassName="table-cal-dropdown"
        className="p-mx-1 w-auto"
        value={e.value}
        options={e.options}
        onChange={(event) => e.onChange(event.originalEvent, event.value)}
        style={{ lineHeight: 1 }}
      />
    );
  };

  useEffect(() => {

    if (!isMobileDevice()&&!isMobile&&dtRef.current.state.filters) {
      Object.entries(dtRef.current.state.filters).forEach(([column, filter]) => {
        if (filter.value && !tableHeaders.find(({ header }) => header === filter.value.header)) {
          delete dtRef.current.state.filters[column];
          switch (filter.value.header) {
            case "Mileage":
              setMinMileage(
                Math.min(
                  ...tableData.map((el) => (el.dataPoint.mileage > -1 ? el.dataPoint.mileage : 0))
                )
              );
              setMaxHours(Math.max(...tableData.map((el) => el.dataPoint.mileage)));
              break;
            case "Hours":
              setMinHours(
                Math.min(
                  ...tableData.map((el) => (el.dataPoint.hours > -1 ? el.dataPoint.hours : 0))
                )
              );
              setMaxHours(Math.max(...tableData.map((el) => el.dataPoint.hours)));
              break;
            case "Cost of Ownership":
              setMinPrice(Math.min(...tableData.map((el) => el.dataPoint.total_cost)));
              setMaxPrice(Math.max(...tableData.map((el) => el.dataPoint.total_cost)));
              break;
            default:
              break;
          }
        }
      });
    }
  }, [tableHeaders]);

  useEffect(() => {
    const column = tableHeaders.findIndex((header) => header.header === "Mileage");
    if (column !== -1) {
      if (dtRef.current.state.filters?.[column]) {
        delete dtRef.current.state.filters[column];
      }
      dtRef.current.filter({ header: "Mileage", minMileage, maxMileage }, column, "custom");
    }
  }, [minMileage, maxMileage, tableHeaders]);

  const MileageFilterElement = () => {
    return (
      <RangeSliderInput
        minValue={minMileage}
        maxValue={maxMileage}
        setMinValue={setMinMileage}
        setMaxValue={setMaxMileage}
        valueGap={500}
        max={maxMileageRange + 500}
        buffer={500}
      />
    );
  };

  useEffect(() => {
    const column = tableHeaders.findIndex((header) => header.header === "Hours");
    if (column !== -1) {
      if (dtRef.current.state.filters?.[column]) {
        delete dtRef.current.state.filters[column];
      }
      dtRef.current.filter({ header: "Hours", minHours, maxHours }, column, "custom");
    }
  }, [minHours, maxHours, tableHeaders]);

  const HoursFilterElement = () => {
    return (
      <RangeSliderInput
        minValue={minHours}
        maxValue={maxHours}
        setMinValue={setMinHours}
        setMaxValue={setMaxHours}
        valueGap={500}
        max={maxHourRange + 500}
        buffer={500}
      />
    );
  };

  useEffect(() => {
    const column = tableHeaders.findIndex((header) => header.header === "Cost of Ownership");
    if (column !== -1) {
      if (dtRef.current.state.filters?.[column]) {
        delete dtRef.current.state.filters[column];
      }
      dtRef.current.filter({ header: "Cost of Ownership", minPrice, maxPrice }, column, "custom");
    }
  }, [minPrice, maxPrice, tableHeaders]);

  const PriceFilterElement = (colIndex) => {
    return (
      <RangeSliderInput
        minValue={minPrice}
        maxValue={maxPrice}
        setMinValue={setMinPrice}
        setMaxValue={setMaxPrice}
        valueGap={1000}
        max={maxPriceRange + 1000}
        buffer={1000}
      />
    );
  };

  const DateFilterElement = (colIndex, dateFormat, isRange = false) => {
    return (
      <div className="table-calendar">
        <Calendar
          panelClassName="dropdown-content-cal"
          className="w-100"
          placeholder={t("general.filter_placeholder", { name: tableHeaders[colIndex].header })}
          value={filters[tableFilters[colIndex]?.field]}
          showButtonBar
          showIcon
          monthNavigator
          yearNavigator
          monthNavigatorTemplate={monthNavigatorTemplate}
          yearNavigatorTemplate={yearNavigatorTemplate}
          yearRange="1980:2099"
          selectionMode={isRange ? "range" : "single"}
          onChange={(e) => {
            let selectedDate = e.target.value;
            let ColFilterField = tableFilters[colIndex].field;
            selectedDate = isRange
              ? selectedDate
              : selectedDate && moment(selectedDate).format(dateFormat);
            setFilters({ ...filters, [ColFilterField]: selectedDate });
            dtRef.current.filter(selectedDate, colIndex, isRange ? "custom" : "equals");
          }}
        />
      </div>
    );
  };

  const SelectFilterElement = (colIndex) => {
    let colFilterOption = tableFilters[colIndex]?.filterOptions;
    let colFilterField = tableFilters[colIndex]?.field;
    let valueArray = [];

    tableData.forEach((rowData) => {
      let value = rowData.dataPoint[colFilterField];
      if (valueArray.indexOf(value) < 0) valueArray.push(value);
    });

    let options = valueArray.map((value) => {
      return { name: value };
    });
    //trim instances of {} and {name: null} or {name: ''}
    options.forEach((e) => {
      for (let value in e) {
        if (e[value] === null || e[value] === "") {
          delete e[value];
        }
      }
    });
    options = options.filter((e) => Object.keys(e).length !== 0);

    let customItemTemplate = (option) => {
      if (option) {
        return !!colFilterOption?.itemTemplate
          ? colFilterOption.itemTemplate(option.name)
          : validateEmail(option.name)
          ? option.name
          : capitalize(option.name);
      }
    };
    let customValueTemplate = (option, props) => {
      if (option)
        return !!colFilterOption?.valueTemplate
          ? colFilterOption.valueTemplate(option.name)
          : validateEmail(option.name)
          ? option.name
          : capitalize(option.name);

      return <span>{props.placeholder}</span>;
    };

    return (
      <MultiSelect
        placeholder={t("general.filter_placeholder", { name: tableHeaders[colIndex].header })}
        panelClassName="table-filter-dropdown"
        options={options}
        optionLabel="name"
        className="p-column-filter"
        value={filters[colFilterField]}
        itemTemplate={customItemTemplate}
        valueTemplate={customValueTemplate}
        showClear
        filter={options.length > 10}
        filterBy="name"
        onChange={(e) => {
          let selectedFilters = e.target.value;
          let filterValue = [];
          if (selectedFilters != null) {
            filterValue = selectedFilters.map((a) => a.name);
          }
          setFilters({ ...filters, [colFilterField]: selectedFilters });
          dtRef.current.filter(filterValue, colIndex, "in");
        }}
      />
    );
  };

  let dynamicColumns = tableHeaders.map((col, colIndex) => {
    //TODO remove this logic after finish all table refactoring
    let colName = typeof col === "string" ? col : col.header;

    return (
      <Column
        key={colIndex}
        field={`${colIndex}`}
        tableData={tableData}
        header={colName}
        body={bodyTemplate}
        filter={!!tableFilters[colIndex]}
        filterPlaceholder={t("general.filter_placeholder", { name: colName })}
        filterElement={filterElement(colIndex)}
        filterFunction={filterFunction(colIndex)}
        filterField={`${colIndex}`}
        filterType={"search"}
        filterMatchMode={
          tableFilters[colIndex]?.filterOptions?.filterFunction ? "custom" : "contains"
        }
        sortable
        style={{ whiteSpace: "pre-wrap", overflowWrap: "break-word" }}
      />
    );
  });

  let list =
    tableData &&
    tableData.map((item) => {
      let data = tableFilters.map((filter, colIndex) => {
        if (!!tableFilters[colIndex]) return item.dataPoint[filter.field];
        else return item.cells[colIndex];
      });

      return {
        id: item.id,
        dataPoint: item.dataPoint,
        cells: item.cells,
        ...data,
      };
    });
  if (list.length !== 0) {
    if (list[0].dataPoint.date_created && timeOrder) {
      list.sort(
        (data1, data2) =>
          new Date(data1.dataPoint.date_created).getTime() -
          new Date(data2.dataPoint.date_created).getTime()
      );
    }
  }

  const exportCSV = () => {
    dtRef.current.exportCSV();
  };

  const handlePdfExport = (dataSource = [], columns = []) => {
    const { apiCallData } = JSON.parse(localStorage.getItem("persist:root"));
    const { userInfo } = JSON.parse(apiCallData);
    const { user } = userInfo || {};
    const head = [columns?.map((column) => column.title)];
    const body = dataSource?.reduce((pre, cur, index) => {
      const dataMap = [];
      for (const column of columns) {
        dataMap.push(cur?.dataPoint?.[column?.dataIndex] || "-");
      }
      pre.push(dataMap);
      return pre;
    }, []);
    jsPDF.autoTableSetDefaults({
      headStyles: { fillColor: [39, 38, 48] },
    });

    const doc = new jsPDF();
    doc.text("Asset Summary Report", 14, 28);
    doc.setFontSize(11);
    doc.setTextColor(100);
    doc.text(`Date of the Report : ${moment().format("YYYY-MM-DD")}`, 14, 40);
    doc.text(`Prepared By : ${user?.first_name} ${user?.last_name}`, 14, 48);
    doc.text(`Total Assets : ${total}`, 14, 56);

    autoTable(doc, {
      startY: 61,
      head: head,
      body: body,
      didDrawPage: function (data) {
        const pageSize = doc.internal.pageSize;
        const pageWidth = pageSize.width ? pageSize.width : pageSize.getWidth();
        const base64Img = logoBase64;
        doc.addImage(base64Img, "png", pageWidth - 54, 5, 40, 15);
      },
      margin: { top: 27 },
      showHead: "firstPage",
    });
    doc.save(`Asset Summary Report ${moment().format("YYYY-MM-DD HHmm")} Local Time.pdf`);
  };

  const tableToolsHeader = (
    <React.Fragment>
      {globalSearch && (
        <>
          <div className="table-tools-header p-fluid">
            <span className="p-input-icon-left">
              <i className="pi pi-search" />
              <InputText
                type="search"
                onInput={(e) => setGlobalFilter(e.target.value)}
                placeholder={t("general.table_global_filter_placeholder")}
                tooltip={t("general.table_global_filter_tooltip")}
                tooltipOptions={{ position: "top" }}
              />
            </span>
            {hasExport && (
              <div className="p-ml-3 table-export-btn" style={{ textAlign: "right" }}>
                <Button
                  type="button"
                  icon="pi pi-external-link"
                  label="Export"
                  onClick={exportCSV}
                />
              </div>
            )}
          </div>
        </>
      )}
      <div className="table-tools-header-total-col">
        {showAssetCount && <span>Total Assets ：{total || 0}</span>}
        {hasPdfExport && (
          <div className="p-ml-3 table-export-btn" style={{ textAlign: "right" }}>
            <Button
              type="button"
              icon="pi pi-external-link"
              label="Export PDF"
              onClick={() => handlePdfExport(realTableData, exportPdfColumns)}
            />
          </div>
        )}
      </div>
    </React.Fragment>
  );

  const getAllPreferences = () => {
    const cancelTokenSource = axios.CancelToken.source();
    axios
      .get(`${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Info`, {
        ...getAuthHeader(),
        cancelToken: cancelTokenSource.token,
      })
      .then((response) => {
        let arr = [];
        Object.entries(response.data.user_config.table_filter).forEach((e) => {
          // here we are just adding a 'useless' key to make the search pref unique
          // should be deleted below or there will be problem
          e[1]["useless"] = Math.floor(Math.random() * 100);
          arr.push({ label: e[0], value: e[1] });
          // handle situation that when date range has null value in the range
          convertNullToDate(e[1]);
        });
        setPreferencesArray(arr);
      })
      .catch((err) => {
        ConsoleHelper(err);
      });
  };

  useEffect(() => {
    getAllPreferences();
  }, []);

  const saveFilterOption = (name) => {
    //save current filter selection with API call
    //filters are stored in an object called "filters", seen below
    let payload = {};
    payload[name] = filters;
    for (let filterName in payload[name]) {
      if (payload[name][filterName] === null) {
        delete payload[name][filterName];
      }
    }
    axios
      .post(
        `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Update/Tablefilter`,
        payload,
        getAuthHeader()
      )
      .then((res) => {
        //update the new value when submit success
        getAllPreferences();
      })
      .catch((error) => {
        ConsoleHelper(error);
      });
  };

  const deleteFilterOption = (list) => {
    var payload = {};
    for (let i = 0; i < list.length; i++) {
      payload[list[i]] = {};
    }
    axios
      .post(
        `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Delete/Tablefilter`,
        payload,
        getAuthHeader()
      )
      .then((res) => {
        //update the new value when submit success
        getAllPreferences();
      })
      .catch((error) => {
        ConsoleHelper(error);
      });
  };

  //update the data in the table according to the filters specified by selectedDropdownFilter, used only for the search preference dropdown
  const updateFilters = (selectedDropdownFilter) => {
    let filterApplied = false;
    // check for non null value
    if (Object.keys(selectedDropdownFilter).length > 0) {
      //reset the current applied filters
      dtRef.current.state.filters = {};
      let columnFilterValues = [];
      for (const columnType in selectedDropdownFilter) {
        //if key is not null
        if (selectedDropdownFilter[columnType]) {
          let columnVal = selectedDropdownFilter[columnType];
          if (!Array.isArray(columnVal)) {
            columnVal = [columnVal];
          }
          columnFilterValues = columnVal.map((a) => {
            if (a) {
              return a instanceof Date ? a : a.name;
            } else {
              return null;
            }
          });
        }
        //if value is not null
        if (columnFilterValues) {
          //find the index of the column in the table that matches the column type specified
          const columnIndex = tableHeaders.findIndex((a) => a.colFilter.field === columnType);
          //update the table ref
          // let add = { value: columnFilterValues, matchMode: "in" };
          // dtRef.current.state.filters[columnIndex] = add;
          if (columnFilterValues.length !== 0) {
            filterApplied = true;
            if (columnFilterValues[0] instanceof Date) {
              let add = { value: columnFilterValues, matchMode: "custom" };
              dtRef.current.state.filters[columnIndex] = add;
              dtRef.current.filter(columnFilterValues, columnIndex, "custom");
            } else {
              let add = { value: columnFilterValues, matchMode: "in" };
              dtRef.current.state.filters[columnIndex] = add;
              dtRef.current.filter(columnFilterValues, columnIndex, "in");
            }
          } else {
            if (!filterApplied) {
              // no filter applied, just clear it
              dtRef.current.filter([], -1, "in");
            }
          }
        }
      }
    }
  };

  // Test whether an object is a date
  const isIsoDate = (str) => {
    if (!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z/.test(str)) return false;
    const d = new Date(str);
    return d instanceof Date && !isNaN(d.getTime()) && d.toISOString() === str; // valid date
  };
  // convert date strings in selectedDropDownFilter to actual dates
  const filterToDate = (selectedDropdownFilter) => {
    Object.keys(selectedDropdownFilter).forEach(function (key, index) {
      let ele = selectedDropdownFilter[key];
      if (isIsoDate(ele[0])) {
        selectedDropdownFilter[key] = ele.map((e) => new Date(e));
      }
    });
    return { ...selectedDropdownFilter };
  };

  const convertNullToDate = (obj) => {
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const value = obj[key];

        if (Array.isArray(value) && containsDateFormat(value)) {
          for (let i = 0; i < value.length; i++) {
            if (value[i] === null) {
              const currentDate = new Date();
              currentDate.setFullYear(currentDate.getFullYear() + 1);
              value[i] = currentDate;
            }
          }
        } else if (typeof value === "object") {
          convertNullToDate(value);
        }
      }
    }
  };

  function containsDateFormat(arr) {
    for (let i = 0; i < arr.length; i++) {
      if (arr[i] instanceof Date || (typeof arr[i] === "string" && !isNaN(Date.parse(arr[i])))) {
        return true;
      }
    }
    return false;
  }

  const handleValueChange = (values) => {
    setRealTableData(values || []);
    setTotal(values?.length || 0);
  };

  useEffect(() => {
    {
      /* update the filters when the page is loaded, will need to be updated when a new search preference is saved too */
    }
    updateFilters(filters);
  }, []);

  const filterButtons = eventTypes.map((eventType, i) => {
    return (
      <ToggleButton
        key={eventType + i}
        checked={checkedFilters[i]}
        onChange={() => filtersHandler(eventType, i)}
        onLabel={capitalize(eventType)}
        offLabel={capitalize(eventType)}
        onIcon=""
        offIcon=""
        className="p-mr-2 p-mb-2 p-button-rounded"
      />
    );
  });

  const filtersHandler = (eventType, i) => {
    let copyOfCheckedFilters = [...checkedFilters];
    copyOfCheckedFilters[i] = !checkedFilters[i];
    setCheckedFilters(copyOfCheckedFilters);
    setTheAllFilter(false);
    let copyOfEventTypeFilter = [...eventTypeFilter];
    if (eventTypeFilter.includes(eventType)) {
      copyOfEventTypeFilter = copyOfEventTypeFilter.filter((type) => type !== eventType);
      setEventTypeFilter(copyOfEventTypeFilter);
      if (copyOfEventTypeFilter.length === 0) setTheAllFilter(!theAllFilter);
    } else {
      copyOfEventTypeFilter.push(eventType);
      setEventTypeFilter(copyOfEventTypeFilter);
    }
  };

  return (
    <div
      className={`table-wrapper ${!globalSearch && !hasExport ? "no-header" : ""}`}
      ref={wrapperRef}
    >
      {/*/!* update the filters when the page is loaded, will need to be updated when a new search preference is saved too *!/*/}
      {/*{updateFilters(filters)}*/}
      <div className={"search-wrapper"} style={{paddingBottom: "1em" }}>
        {showSearchPref && (
          <div>
            {/* dropdown for selecting a search preference */}
            <Dropdown
              panelClassName="table-filter-dropdown"
              className="custom-dropdown-style"
              value={searchPreference}
              onChange={(e) => {
                let selectedDropdownFilter = e.target.value;
                // to convert the date strings into actual dates to avoid errors when using saved dates as search options
                selectedDropdownFilter = filterToDate(selectedDropdownFilter);
                setSearchPreference(selectedDropdownFilter);
                // this code is just to delete the 'useless' key defined to make the value unique
                // copy is exactly the same with the selectedDropdownFilter
                let copy = { ...selectedDropdownFilter };
                delete copy["useless"];
                setFilters(copy);
                updateFilters(copy);
              }}
              options={preferencesArray}
              placeholder={"Search preferences"}

            />
          </div>
        )}
        {showSearchPref && (
          <div className="btn-1">
            {/* button for toggling submitting search preference modal */}
            <Button
              label="Save Search Preference"
              onClick={() => setSaveFilterDialog(true)}
              className="button"
              style={{width:"240px"}}
            />
            <Button
              label="Delete Search Preference"
              onClick={() => deletepreference()}
              className="button"
              style={{width:"240px"}}

            />
          </div>
        )}
        {/* dialog for submitting new search preferences */}
        <Dialog
          className="custom-main-dialog configure-checks-dialog"
          header={"Save Custom Search Preference"}
          visible={saveFilterDialog}
          onHide={() => setSaveFilterDialog(false)}
          style={{ width: "60vw" }}
        >
          <CustomInputText
            type="name"
            placeholder="Enter search preference name"
            value={searchPreferenceName}
            onChange={setSearchPreferenceName}
            leftStatus
          />
          <div style={{ paddingTop: "1em" }}>
            <Button
              label="Submit"
              onClick={() => {
                setSaveFilterDialog(false);
                var checkempty = true;
                for (var i = 0; i < searchPreferenceName.length; i++) {
                  if (searchPreferenceName[i] != " ") {
                    checkempty = false;
                  }
                }
                if (Boolean(searchPreferenceName) != false && checkempty == false) {
                  saveFilterOption(searchPreferenceName);
                }
              }}
              className="button"
            />
          </div>
        </Dialog>
        {/* dialog for deleting search perference*/}
        <Dialog
          className="custom-main-dialog configure-checks-dialog"
          header={"Delete Custom Search Preference"}
          visible={deleteFilterDialog}
          onHide={() => setDeleteFilterDialog(false)}
          style={{ width: "60vw" }}
        >
          <p>Please select the search preference you want to delete.</p>
          {filterButtons}
          <div style={{ paddingTop: "1em" }}>
            <Button
              label="Submit"
              onClick={() => {
                setDeleteFilterDialog(false);
                const deletelist = [];
                for (let i = 0; i < filterButtons.length; i++) {
                  if (checkedFilters[i] == true) {
                    deletelist.push(eventTypes[i]);
                    checkedFilters[i] = false;
                  }
                }
                deleteFilterOption(deletelist);
              }}
              className="button"
            />
            <Button
              label="Cancel"
              onClick={() => {
                setDeleteFilterDialog(false);
                for (let i = 0; i < filterButtons.length; i++) {
                  checkedFilters[i] = false;
                }
              }}
              className="button"
            />
          </div>
        </Dialog>
      </div>

      {dataReady || (!dataReady && !isMobile) ? (
        <DataTable
          first={first}
          onPage={onPageHandler}
          onValueChange={handleValueChange}
          ref={dtRef}
          header={tableToolsHeader}
          globalFilter={globalFilter}
          value={list}
          selection={selectedRowData}
          selectionMode={selectionMode}
          dataKey="id"
          metaKeySelection={false}
          loading={!dataReady}
          rowHover
          paginator
          rows={rows ? rows : isMobile ? 5 : 8}
          pageLinkSize={isMobile ? 3 : 5}
          rowClassName={(data) => {
            return { [selectionMode]: true };
          }}
          onSelectionChange={onSelectHandle}
          emptyMessage={t("general.table_no_data_match")}
          resizableColumns
          columnResizeMode="fit"
        >
          {/*{selectionMode ? (*/}
          {/*  <Column selectionMode={selectionMode} headerStyle={{ width: "3rem" }}/>*/}
          {/*) : null}*/}
          {dynamicColumns}
          {isMobile && !disableMobileDetail && (

              <Column
                  className="detailview-indicator"
                  body={() => {
                    return (
                        <React.Fragment>
                          <hr style={{background:"#686969"}}/> {/* Horizontal line */}
                          <Button
                              label={t("general.mobile_table_detail_indicator")}
                              icon="pi pi-chevron-right"
                              className="detailview-button"
                              iconPos="right"
                              disabled
                          />
                        </React.Fragment>
                    );
                  }}
              />
          )}
        </DataTable>
      ) : (
        <LoadingAnimation />
      )}
    </div>
  );
};

export default Table;
