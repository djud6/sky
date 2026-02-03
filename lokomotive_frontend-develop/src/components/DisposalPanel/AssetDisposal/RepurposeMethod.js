import React from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import CardWidget from "../../ShareComponents/CardWidget";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import VendorOption from "./VendorOption";
import "../../../styles/helpers/textfield2.scss";

const RepurposeMethod = ({
  email,
  setEmail,
  approvedVendor,
  setApprovedVendor,
  multiSelectedVendor,
  setMultiSelectedVendor,
  isVendorSelected,
  setIsVendorSelected,
  businessUnits,
  selectedBusinessUnit,
  setSelectedBusinessUnit,
  jobSpecList,
  selectedJobSpec,
  setSelectedJobSpec,
}) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const selectBusinessUnit = (id) => {
    let selected = businessUnits.find(
      (businessUnit) => businessUnit.business_unit_id === parseInt(id)
    );
    setSelectedBusinessUnit(selected);
  };

  const selectJobSpecification = (id) => {
    let selected = jobSpecList.find((job) => job.job_specification_id === parseInt(id));
    setSelectedJobSpec(selected);
  };

  return (
    <React.Fragment>
      <div
        className={`repurpose-form-container ${
          !isMobile ? "p-sm-12 p-md-12 p-lg-6 p-xl-6" : "w-100 p-m-3"
        }`}
      >
        <h5 className="p-mb-3">{t("removalPanel.last_step_repurpose")}</h5>
        <div className="repurpose-form-content w-100">
          <CardWidget status={selectedBusinessUnit} lightBg>
            <label className="h5 p-mb-3 font-weight-bold">
              {t("removalPanel.repurpose_new_department")}
            </label>
            <div>
              <FormDropdown
                defaultValue={
                  selectedBusinessUnit && {
                    name: selectedBusinessUnit.name,
                    code: selectedBusinessUnit.business_unit_id,
                  }
                }
                onChange={selectBusinessUnit}
                options={
                  businessUnits &&
                  businessUnits.map((businessUnit) => ({
                    name: businessUnit.name,
                    code: businessUnit.business_unit_id,
                  }))
                }
                loading={!businessUnits}
                disabled={!businessUnits}
                dataReady={businessUnits}
                plain_dropdown
                reset="disabled"
              />
            </div>
          </CardWidget>
          <CardWidget status={selectedJobSpec} lightBg>
            <label className="h5 p-mb-3 font-weight-bold">
              {t("removalPanel.repurpose_job_specification")}
            </label>
            <div>
              <FormDropdown
                defaultValue={
                  selectedJobSpec && {
                    name: selectedJobSpec.name,
                    code: selectedJobSpec.job_specification_id,
                  }
                }
                onChange={selectJobSpecification}
                options={
                  jobSpecList &&
                  jobSpecList.map((job) => ({
                    name: job.name,
                    code: job.job_specification_id,
                  }))
                }
                loading={!jobSpecList}
                disabled={!jobSpecList}
                dataReady={jobSpecList}
                plain_dropdown
                reset="disabled"
              />
            </div>
          </CardWidget>
          <CardWidget status={isVendorSelected} lightBg>
            <VendorOption
              method={t("removalPanel.repurpose")}
              email={email}
              setEmail={setEmail}
              approvedVendor={approvedVendor}
              setApprovedVendor={setApprovedVendor}
              multiSelectedVendor={multiSelectedVendor}
              setMultiSelectedVendor={setMultiSelectedVendor}
              setIsVendorSelected={setIsVendorSelected}
              vendorType="disposal"
            />
          </CardWidget>
        </div>
      </div>
      {!isMobile && <div className="p-sm-12 p-md-12 p-lg-6 p-xl-6">{""}</div>}
    </React.Fragment>
  );
};

export default RepurposeMethod;
