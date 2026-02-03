import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "primereact/button";
import { ToggleButton } from "primereact/togglebutton";
import CustomInputText from "../ShareComponents/CustomInputText";
import FileUploadInput from "../ShareComponents/FileUploadInput";
import FormDropdown from "../ShareComponents/Forms/FormDropdown";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../constants";

export const PasswordDialog = ({
  password,
  setPassword,
  matchError,
  emptyError,
  newPassword,
  setNewPassword,
  confirmPassword,
  setConfirmPassword,
  submitPassword,
  setSubmitPassword,
}) => {
  const { t } = useTranslation();

  return (
    <div>
      <div>
        <label htmlFor="currentPassword">{t("accountOptions.old_password_label")}</label>
        <CustomInputText
          required
          leftStatus
          type="password"
          className={`form-control ${submitPassword && !password && "is-invalid"}`}
          id="currentPassword"
          placeholder="Password"
          onChange={(val) => {
            setSubmitPassword(false);
            setPassword(val);
          }}
        />
      </div>
      <div className="p-mt-3">
        <label htmlFor="newPassword">{t("accountOptions.new_password_label")}</label>
        <CustomInputText
          required
          leftStatus
          type="password"
          className={`form-control ${
            submitPassword && (matchError || !newPassword) && "is-invalid"
          }`}
          id="newPassword"
          placeholder="New Password"
          onChange={(val) => {
            setSubmitPassword(false);
            setNewPassword(val);
          }}
        />
      </div>
      <div className="p-mt-3">
        <label htmlFor="confirmPassword">{t("accountOptions.new_password_again_label")}</label>
        <CustomInputText
          required
          leftStatus
          type="password"
          className={`form-control ${
            submitPassword && (matchError || !confirmPassword) && "is-invalid"
          }`}
          id="confirmPassword"
          placeholder="Confirm Password"
          onChange={(val) => {
            setSubmitPassword(false);
            setConfirmPassword(val);
          }}
        />
      </div>
      {/* fixme: doesn't appear? */}
      {submitPassword && matchError && (
        <div className="invalid-feedback">{t("accountOptions.passwords_match_error")}</div>
      )}
      {submitPassword && emptyError && (
        <div className="invalid-feedback">{t("accountOptions.passwords_empty_error")}</div>
      )}
    </div>
  );
};

export const ImageDialog = ({ selectedFile, setSelectedFile, fileLoading, setFileLoading }) => {
  const [imageFileName, setImageFileName] = useState("");

  return (
    <div className="custom-file input-files-container">
      <FileUploadInput
        images={selectedFile}
        setImages={setSelectedFile}
        imageNames={imageFileName}
        setImageNames={setImageFileName}
        fileLoading={fileLoading}
        setFileLoading={setFileLoading}
      />
      <div className="p-d-flex p-jc-end" />
    </div>
  );
};

export const ConfigDialog = ({
  defaultCategory,
  allCategory,
  onCategoryChange,
  configurations,
  setConfigurations,
  setAllConfigurations,
}) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  return isMobile ? (
    <div>
      <>
        <Button onClick={() => setAllConfigurations(true)} className="btn-enable btn-block btn-secondary mt-3">
          {t("accountOptions.set_config_all_enabled")}
        </Button>
        <Button onClick={() => setAllConfigurations(false)} className="btn-default btn-block btn-secondary mt-3">
          {t("accountOptions.set_config_all_disabled")}
        </Button>
      </>
      <label htmlFor="emailConfigCategory" className="p-pt-2">{t("accountOptions.email_config_category")}</label>
      <FormDropdown
        id="emailConfigCategory"
        defaultValue={{ name: t(`accountOptions.${defaultCategory}`), code: defaultCategory }}
        options={allCategory.map((category) => {
          return { name: t(`accountOptions.${category}`), code: category };
        })}
        onChange={onCategoryChange}
        dataReady={defaultCategory && allCategory}
        reset="disabled"
        leftStatus
        plain_dropdown
      />
      <div className="d-flex flex-column">
        {Object.entries(configurations).map(([key, value], index) => (
          <div key={index} className="d-flex flex-column p-mt-2">
            <label htmlFor={key}>{t(`accountOptions.${key}`)}</label>
            <ToggleButton
              id={key}
              checked={value}
              onChange={setConfigurations(key)}
              onIcon="pi pi-check"
              offIcon="pi pi-times"
              onLabel="enabled"
              offLabel="disabled"
            />
          </div>
        ))}
      </div>
    </div>
  ) : (
    <div>
      <>
        <Button onClick={() => setAllConfigurations(true)} className="btn-enable btn btn-secondary mt-1">
          {t("accountOptions.set_config_all_enabled")}
        </Button>
        <Button onClick={() => setAllConfigurations(false)} className="btn-default btn btn-secondary mt-1 ml-3">
          {t("accountOptions.set_config_all_disabled")}
        </Button>
      </>
      <FormDropdown
        label={t("accountOptions.email_config_category")}
        defaultValue={{ name: t(`accountOptions.${defaultCategory}`), code: defaultCategory }}
        options={allCategory.map((category) => {
          return { name: t(`accountOptions.${category}`), code: category };
        })}
        onChange={onCategoryChange}
        dataReady={defaultCategory && allCategory}
        reset="disabled"
        leftStatus
        plain_dropdown
      />
      {Object.entries(configurations).map(([key, value], index) => (
        <div key={index} className="p-d-flex p-jc-between mt-2">
          <label htmlFor={key}>{t(`accountOptions.${key}`)}</label>
          <ToggleButton
            className="p-ml-1"
            id={key}
            checked={value}
            onChange={setConfigurations(key)}
            onIcon="pi pi-check"
            offIcon="pi pi-times"
            onLabel="&nbsp;enabled"
            offLabel="disabled"
          />
        </div>
      ))}
    </div>
  );
};
