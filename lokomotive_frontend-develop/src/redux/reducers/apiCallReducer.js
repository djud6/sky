import {
  GET_INIT_DATA,
  RESET_INIT_DATA,
  GET_USER_DATA,
  UPDATE_LAYOUT,
} from "../types/apiCallTypes";

const initialState = {
  initDataLoaded: false,
  userInfo: {},
  userConfig: null,
  listLocations: null,
  listBusinessUnits: null,
  listJobSpecs: null,
  listCurrencies: null,
  listFuelUnits: null,
  listAssetRequestJust: null,
  listAssetTypeChecks: null,
  listIssueCategories: null,
};

export const apiCallReducer = (state = initialState, action = {}) => {
  switch (action.type) {
    case GET_INIT_DATA:
      return {
        ...state,
        initDataLoaded: true,
        userInfo: {
          user: action.payload.user,
          detailed_user: action.payload.detailed_user,
        },
        userConfig: action.payload.user_config,
        listLocations: action.payload.locations,
        listBusinessUnits: action.payload.business_units,
        listJobSpecs: action.payload.job_specifications,
        listCurrencies: action.payload.currencies,
        listFuelUnits: action.payload.fuel_volume_units,
        listAssetRequestJust: action.payload.asset_request_justifications,
        listAssetTypeChecks: action.payload.asset_type_check_fields,
        listIssueCategories: action.payload.issue_categories,
        platform: 'lokomotive'  // this is used to check if this login info is for this platform only
      };

    case RESET_INIT_DATA:
      return {
        ...state,
        initDataLoaded: false,
        userInfo: {},
        userConfig: null,
        listLocations: null,
        listBusinessUnits: null,
        listJobSpecs: null,
        listCurrencies: null,
        listFuelUnits: null,
        listAssetRequestJust: null,
        listAssetTypeChecks: null,
        listIssueCategories: null,
      };

    case GET_USER_DATA:
      return {
        ...state,
        userInfo: action.payload,
      };

    case UPDATE_LAYOUT:
      return {
        ...state,
        userConfig: {
          ...state.userConfig,
          dashboard_layout: action.payload.dashboard_layout,
        },
      };

    default:
      return state;
  }
};
