import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import ChartCard from "../ChartCard/ChartCard";
import MultipleAxesCard from "./MultipleAxesCard";
import FullWidthSkeleton from "../../ShareComponents/CustomSkeleton/FullWidthSkeleton";
import FormDropdown from "../Forms/FormDropdown";
import { Button } from "primereact/button";
import { InputText } from "primereact/inputtext";
import MultiSelectDropdown from "../../ShareComponents/Forms/MultiSelectDropdown";
import { isMobileDevice } from "../../../helpers/helperFunctions";

const CostPerProcess = ({ costPerProcessParams, dataReady, error, height }) => {
  const isMobile = isMobileDevice();
  const { t } = useTranslation();
  const [locations, setLocations] = useState([]);
  const [selectedLocations, setSelectedLocations] = useState([]);
  const [years, setYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState(null);
  const [data, setData] = useState([]);
  const processes = [
    { name: "Repair", code: "repair" },
    { name: "Maintenance", code: "maintenance" },
    { name: "Accident", code: "accident" },
  ];
  const [selectedProcess, setSelectedProcess] = useState(processes[0]);
  const [filter, setFilter] = useState("");

  let maxSelectedLoctaions = 6;
  if (isMobile) maxSelectedLoctaions = 3;

  const monthsList = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];

  useEffect(() => {
    if (costPerProcessParams && selectedLocations.length > 0 && selectedYear && selectedProcess) {
      setData([]);
      const newData = [];
      selectedLocations.forEach((selectedLocation) => {
        let x = { [selectedLocation.name]: [] };
        let temp = costPerProcessParams[selectedLocation.name][selectedYear.name];
        if (!temp) temp = {};
        temp &&
          monthsList.forEach((month) => {
            x[selectedLocation.name].push({
              [selectedProcess.code]: (month in temp
                ? temp[month][selectedProcess.code]
                : 0
              ).toFixed(2),
              date: new Date(month + " 1, " + selectedYear.name),
            });
          });
        newData.push(x);
      });
      setData(newData);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [costPerProcessParams, selectedLocations, selectedYear, selectedProcess]);

  useEffect(() => {
    let listOfLocations = [];
    if (costPerProcessParams) {
      Object.keys(costPerProcessParams).map((location) => listOfLocations.push(location));
      listOfLocations = listOfLocations.map((location) => ({ name: location, code: location }));
      setLocations(listOfLocations);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(costPerProcessParams)]);

  useEffect(() => {
    if (locations.length > 0) {
      if (selectedLocations.length === 0) {
        let topThreeLocs = [];
        Object.keys(costPerProcessParams).forEach((location) => {
          topThreeLocs.length < 3 && topThreeLocs.push({ name: location, code: location });
        });
        setSelectedLocations(topThreeLocs);
      }
    }
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [locations, selectedLocations]);

  useEffect(() => {
    if (costPerProcessParams && selectedLocations.length > 0) {
      let listOfYears = [];
      selectedLocations.forEach((selectedLocation) => {
        costPerProcessParams[selectedLocation.name] &&
          Object.keys(costPerProcessParams[selectedLocation.name]).map(
            (year) => !listOfYears.includes(year) && listOfYears.push(year)
          );
      });
      listOfYears = listOfYears.map((year) => ({ name: year, code: year }));
      setYears(listOfYears);
    }
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(costPerProcessParams), selectedLocations]);

  useEffect(() => {
    if (years.length > 0) {
      if (!selectedYear) {
        setSelectedYear(years[0]);
      }
    }
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [years, selectedYear]);

  const changeHandlerLoc = (e) => {
    setSelectedLocations(e.value);
    let listOfLocations = e.value;
    let listOfYears = [];
    listOfLocations.forEach((selectedLocation) => {
      costPerProcessParams[selectedLocation.name] &&
        Object.keys(costPerProcessParams[selectedLocation.name]).map(
          (year) => !listOfYears.includes(year) && listOfYears.push(year)
        );
    });
    listOfYears = listOfYears.map((year) => ({ name: year, code: year }));
    setYears(listOfYears);
    setSelectedYear(listOfYears[0]);
  };

  const changeHandlerYear = (code) => {
    let selected = years.find((year) => year.code === code);
    setSelectedYear(selected);
  };

  const changeHandlerProc = (code) => {
    let selected = processes.find((process) => process.code === code);
    setSelectedProcess(selected);
  };

  const panelFooterTemplate = () => {
    const length = selectedLocations ? selectedLocations.length : 0;
    return (
      <div className="p-py-2 p-px-3 text">
        <b>{length}</b> item{length > 1 ? "s" : ""} selected out of <b>{maxSelectedLoctaions}</b>
      </div>
    );
  };
  const multiselectHeaderTemplate = () => {
    return (
      <div className="p-multiselect-header">
        <div className="p-multiselect-filter-container">
          <InputText
            className="w-100"
            type="text"
            placeholder="Filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>
        <Button
          icon="pi pi-times"
          className="p-button-rounded p-button-text p-button-secondary"
          onClick={() => setFilter("")}
        />
      </div>
    );
  };

  let filteredLocations;
  filteredLocations = locations.filter((location) => location.name.toUpperCase());

  return (
    <ChartCard title={t("costPerProcessChart.title")} tooltipName="cost_per_process">
      {dataReady ? (
        error ? (
          <FullWidthSkeleton height={height} error />
        ) : (
          <div className="row no-gutters text-center mt-3 justify-content-center">
            <div className="mx-1">
              <FormDropdown
                options={processes}
                className="w-100"
                defaultValue={selectedProcess}
                onChange={changeHandlerProc}
                loading={!dataReady}
                disabled={!dataReady}
                dataReady={dataReady}
                reset="disabled"
                plain_dropdown
              />
            </div>
            <div className={`mx-1`}>
              <FormDropdown
                options={years}
                className="w-100"
                defaultValue={selectedYear}
                onChange={changeHandlerYear}
                loading={!dataReady}
                disabled={!dataReady}
                dataReady={dataReady}
                reset="disabled"
                plain_dropdown
              />
            </div>
            <div className={`custom-multi-select ${isMobile && "w-75"} mx-1`}>
              <MultiSelectDropdown
                classNames="w-100"
                value={selectedLocations}
                options={filteredLocations}
                onChange={changeHandlerLoc}
                display="chip"
                panelHeaderTemplate={multiselectHeaderTemplate}
                panelFooterTemplate={panelFooterTemplate}
                selectionLimit={maxSelectedLoctaions}
              />
            </div>

            <MultipleAxesCard
              processName={selectedProcess && selectedProcess.code}
              chartParams={data}
              height={height}
              chartName="cost-per-process"
            />
          </div>
        )
      ) : (
        <FullWidthSkeleton height={height} />
      )}
    </ChartCard>
  );
};

export default CostPerProcess;
