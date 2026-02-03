import { UPDATE_ISSUES } from "../types/issueTypes";

const initialState = {
  searchedIssues: [],
};

export const searchIssueReducer = (state = initialState, action) => {
  switch (action.type) {
    case UPDATE_ISSUES:
      return { ...state, searchedIssues: action.data };
    default:
      return state;
  }
};
