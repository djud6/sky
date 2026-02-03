import { combineReducers } from "redux";
import { audioReducer } from "./reducers/audioReducers";
import { weatherReducer } from "./reducers/weatherReducer";
import { apiCallReducer } from "./reducers/apiCallReducer";
import { searchIssueReducer } from "./reducers/searchIssueReducer";

const reducer = combineReducers({
  ctrlAudios: audioReducer,
  weatherData: weatherReducer,
  apiCallData: apiCallReducer,
  searchIssueData: searchIssueReducer,
});

export default reducer;
