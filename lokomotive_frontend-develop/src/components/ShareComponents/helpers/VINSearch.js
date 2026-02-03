import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import SearchBox from "./SearchBox";
import { getAuthHeader } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import { debounce } from "lodash";
import Table from "../Table/Table";
import Spinner from "../Spinner";
import ReactTooltip from "react-tooltip";
import { Button } from "primereact/button";
import { useTranslation } from "react-i18next";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/ShareComponents/helpers/VINSearch.scss";
import "../../../styles/ShareComponents/autoComplete.scss";
/* Takes props:

onVehicleSelected -- A function taking one argument, called when the user selects a vehicle.  Function parameter is the selected vehicle object

*/
function VINSearch({
  onVehicleSelected,
  tooltip = false,
  tooltipText,
  tooltipId,
  defaultValue,
  reset,
}) {
  const [fieldValue, setFieldValue] = useState("");
  const [choices, setChoices] = useState(null);
  const [filteredAssets, setFilteredAssets] = useState([]);
  const [showAll, setShowAll] = useState(false);
  const [assetSelected, setAssetSelected] = useState(false);
  const [dataReady, setDataReady] = useState("");
  let tableHeaders = ["VIN", "Type", "Business Unit", "Location"];
  let tableData = null;
  const { t } = useTranslation();

  useEffect(() => {
    if (defaultValue) setFieldValue(defaultValue);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (reset) setFieldValue("");
  }, [reset]);

  useEffect(() => {
    if (filteredAssets) setFilteredAssets([]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fieldValue]);

  if (Array.isArray(choices) && choices.length > 1) {
    if (showAll || choices.length <= 3) {
      tableData = choices.map((vehicle) => {
        return {
          id: vehicle.VIN,
          dataPoint: vehicle,
          cells: [vehicle.VIN, vehicle.Asset_Type, vehicle.businessUnit, vehicle.current_location],
        };
      });
    } else {
      tableData = choices.slice(0, 3).map((vehicle) => {
        return {
          id: vehicle.VIN,
          dataPoint: vehicle,
          cells: [vehicle.VIN, vehicle.Asset_Type, vehicle.businessUnit, vehicle.current_location],
        };
      });
    }
  }

  const debouncedSearch = useRef(
    debounce((cancelToken, fieldValue) => {
      setDataReady(false);
      onVehicleSelected(null);
      axios
        .get(`${Constants.ENDPOINT_PREFIX}/api/v1/AssetsByLast/VIN/UnitNumber/${fieldValue}`, {
          ...getAuthHeader(),
          cancelToken: cancelToken,
        })
        .then((response) => {
          setChoices(response.data);
          setAssetSelected(false);
          setDataReady(true);
          onVehicleSelected(response.data[0]);
          setFilteredAssets([]);
        })
        .catch((e) => {
          ConsoleHelper(e);
          if (e.response.status === 300) {
            let assetArray = e.response.data.map((asset) => ({ name: asset }));
            setFilteredAssets([...assetArray]);
          } else if (e.response.status === 400) {
            setFilteredAssets([{ name: t("navigationBar.no_matching_assets_found") }]);
            onVehicleSelected(null); // return null to let other components deal with error
          }
          setDataReady(true);
        });
    }, 1000)
  ).current;

  const autoCompleteMethod = (event) => {
    const { token } = axios.CancelToken.source();
    if (event.query.trim().length >= 2) {
      debouncedSearch(token, fieldValue);
    }
  };

  const handleChange = (e) => {
    if (e.value === t("navigationBar.no_matching_assets_found")) return null;
    if (typeof e.value !== "object") {
      setFieldValue(e.value);
    } else {
      setFieldValue(e.value.name);
    }
  };

  useEffect(() => {
    const { token, cancel } = axios.CancelToken.source();
    if (fieldValue.length >= 2) {
      debouncedSearch(token, fieldValue);
    }
    return () => cancel("No longer latest query") || debouncedSearch.cancel();
  }, [debouncedSearch, fieldValue]);

  let choiceContent = (
    <div className="text-center">
      <h2>No matching vehicles found</h2>
    </div>
  );

  if (choices != null && choices.length > 1) {
    choiceContent = (
      <div>
        <Table
          tableHeaders={tableHeaders}
          tableData={tableData}
          hasSelection
          onSelectionChange={(v) => {
            setAssetSelected(true);
            onVehicleSelected(v);
          }}
        />
        {choices.length > 3 && !showAll && (
          <div className="text-center">
            <Button
              label="Load More"
              className="p-button-secondary"
              onClick={() => setShowAll(true)}
            />
          </div>
        )}
      </div>
    );
  } else if (choices != null && choices.length === 1) {
    choiceContent = "";
  }

  return (
    <div className={"VIN"} data-tip data-for={tooltipId}>
      <SearchBox
        value={fieldValue}
        onChange={handleChange}
        autoCompleteMethod={autoCompleteMethod}
        filteredAssets={filteredAssets}
      />
      {dataReady === false && <Spinner />}
      {choices != null && !assetSelected ? choiceContent : null}
      {tooltip && (
        <ReactTooltip id={tooltipId} effect="solid" type="dark">
          {tooltipText}
        </ReactTooltip>
      )}
    </div>
  );
}

export default VINSearch;
