import { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import axios from "axios";
import * as Constants from "../../../../constants";
import { getAuthHeader } from "../../../../helpers/Authorization";
import { UPDATE_LAYOUT } from "../../../../redux/types/apiCallTypes";
import ConsoleHelper from "../../../../helpers/ConsoleHelper";

/**
 * Custom hook to manage dashboard layout functionality
 * Handles loading, saving, and editing dashboard layouts
 */
export const useDashboardLayout = () => {
  const dispatch = useDispatch();
  const [isEdit, setIsEdit] = useState(false);
  const [exec_layout, setExecLayout] = useState(null);
  const [mngr_layout, setManagerLayout] = useState(null);

  // Load dashboard layout from API
  useEffect(() => {
    const loadDashboardLayout = async () => {
      try {
        const authHeader = getAuthHeader();
        const response = await axios.get(
          `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Info`,
          authHeader
        );

        if (response.data.user_config.dashboard_layout) {
          let payload = response.data.user_config.dashboard_layout.replace(/'/g, '"');
          payload = payload.replace(/False/g, "false");
          payload = payload.replace(/None/g, "null");
          payload = JSON.parse(payload);

          setExecLayout(payload.exec_layout);
          setManagerLayout(payload.mngr_layout);
        }
      } catch (error) {
        // generalErrorAlert('Oops, some thing went wrong while loading');
        ConsoleHelper(error);
      }
    };

    loadDashboardLayout();
  }, []);

  // Save dashboard layout
  const saveLayout = async () => {
    try {
      const exec_layout = JSON.parse(window.localStorage.getItem("exec_layout"));
      const mngr_layout = JSON.parse(window.localStorage.getItem("mngr_layout"));

      if (exec_layout.xs[4].h > 4.5) {
        exec_layout.xs[4].h = 4.5;
        exec_layout.xxs[4].h = 4.5;
      }
      if (exec_layout.xs[5].h > 4.5) {
        exec_layout.xs[5].h = 4.5;
        exec_layout.xxs[5].h = 4.5;
      }
      if (mngr_layout.xs[0].h > 4.5) {
        mngr_layout.xs[0].h = 4.5;
        mngr_layout.xxs[0].h = 4.5;
      }

      const headers = getAuthHeader();
      headers.headers["Content-Type"] = "application/json";

      const data = {
        dashboard_layout: {
          exec_layout: exec_layout,
          mngr_layout: mngr_layout,
        },
      };

      dispatch({ type: UPDATE_LAYOUT, payload: data });

      const requestConfig = {
        method: "post",
        url: `${Constants.ENDPOINT_PREFIX}/api-auth/v1/User/Update/Configuration`,
        ...headers,
        data: data,
      };

      await axios(requestConfig);
    } catch (error) {
      ConsoleHelper(error);
    }
  };

  // Toggle edit mode and save if exiting edit mode
  const toggleEditMode = () => {
    const wasEditing = isEdit;
    setIsEdit(!isEdit);

    if (wasEditing) {
      saveLayout();
    }
  };

  return {
    isEdit,
    exec_layout,
    mngr_layout,
    toggleEditMode,
    saveLayout,
  };
};
