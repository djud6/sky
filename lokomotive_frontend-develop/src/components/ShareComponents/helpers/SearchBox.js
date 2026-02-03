import React from "react";
import useWindowSize from "./useWindowSize";
import { useTranslation } from "react-i18next";
import * as Constants from "../../../constants/index";
import { AutoComplete } from "primereact/autocomplete";

const SearchBox = ({
  value,
  onChange,
  autoCompleteMethod,
  filteredAssets,
}) => {
  const { t } = useTranslation();
  const size = useWindowSize();
  return (
    <div className={`p-mt-2 p-p-2 card p-shadow-2 ${value ? "search-filled" : ""}`}>
      {size.width >= Constants.MOBILE_BREAKPOINT && (
        <div className={`p-inputgroup p-d-flex`}>
          <div className="search-icon-container">
            <i className="pi pi-search" />
          </div>
          <AutoComplete
            panelClassName={filteredAssets.length === 0 ? "hide-panel" : ""}
            value={value}
            onChange={onChange}
            placeholder={t("searchBox.label_vin_search")}
            completeMethod={autoCompleteMethod}
            suggestions={filteredAssets}
            field="name"
          />
        </div>
      )}
      {/* Mobile screens */}
      {size.width < Constants.MOBILE_BREAKPOINT && (
        <div className={`p-inputgroup p-d-flex`}>
          <div className="search-icon-container">
            <i className="pi pi-search" />
          </div>
          <AutoComplete
            panelClassName={filteredAssets.length === 0 ? "hide-panel" : ""}
            value={value}
            onChange={onChange}
            placeholder={t("searchBox.label_vin_search")}
            completeMethod={autoCompleteMethod}
            suggestions={filteredAssets}
            field="name"
          />
        </div>
      )}
    </div>
  );
};

export default SearchBox;
