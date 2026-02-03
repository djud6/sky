import React from "react";
import ReactTooltip from "react-tooltip";

/**
 * Dashboard Edit Controls Component
 * Handles the edit/save dashboard layout functionality
 */
const DashboardEditControls = ({ isEdit, onToggleEdit }) => {
  return (
    <div className="row">
      <div
        onClick={onToggleEdit}
        data-tip={`${isEdit ? "Save" : "Edit"} your dashboard layout`}
        className={`edit-dashboard ${isEdit ? "save-layout-icon" : "edit-layout-icon"}`}
      />
      <label className="form-tooltip">
        <ReactTooltip place="left" />
      </label>
    </div>
  );
};

export default DashboardEditControls;
