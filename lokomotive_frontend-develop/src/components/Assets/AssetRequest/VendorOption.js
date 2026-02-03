import React, { useEffect } from "react";
import { useTranslation } from "react-i18next";
import StarRating from "react-svg-star-rating";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faLeaf } from "@fortawesome/free-solid-svg-icons";
import FormDropdown from "../../ShareComponents/Forms/FormDropdown";
import MultiSelectDropdown from "../../ShareComponents/Forms/MultiSelectDropdown";
import CustomInputText from "../../ShareComponents/CustomInputText";

const VendorOption = ({
  dataReady,
  approvedVendors,
  approvedVendor,
  setApprovedVendor,
  multiSelectedVendor,
  setMultiSelectedVendor,
  vendorEmail,
  setVendorEmail,
  setIsVendorSelected,
  dropdownReset,
}) => {
  const { t } = useTranslation();

  const approvedVendorOption = [
    { name: t("general.approved_vendors"), code: 1 },
    { name: t("general.other_vendors"), code: 2 },
  ];

  useEffect(() => {
    if (approvedVendor) {
      if (approvedVendor === t("general.approved_vendors") && multiSelectedVendor.length) {
        setIsVendorSelected(true);
      } else if (approvedVendor === t("general.other_vendors")) {
        if (vendorEmail) {
          setIsVendorSelected(true);
        } else {
          setIsVendorSelected(false);
        }
      }
    } else {
      setIsVendorSelected(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [approvedVendor, multiSelectedVendor, vendorEmail, setIsVendorSelected]);

  const selectApprovedVendor = (id) => {
    let selected = approvedVendorOption.find((v) => v.code === parseInt(id));
    setApprovedVendor(selected.name);
  };

  const itemTemplate = (option) => {
    const rating = option.rating?.toFixed(1);
    return (
      <div>
        <span>
          <i>{option.name}</i>
          {option.is_vendor_green && (
            <FontAwesomeIcon
              icon={faLeaf}
              color={"#54d67b"}
              style={{ margin: "0 3px", verticalAlign: "middle" }}
            />
          )}
        </span>{" "}
        {option.code !== 9999 && (
          <>
            (<span> {rating} </span>
            <StarRating
              unit="float"
              initialRating={rating}
              activeColor={"#2196F3"}
              isReadOnly
              style={{ display: "inline-block" }}
              size={20}
            />
            )
          </>
        )}
      </div>
    );
  };

  return (
    <React.Fragment>
      <div className="p-d-flex p-jc-between p-ai-center p-mb-2">
        <label className="h5">{t("general.select_vendor")}</label>
        <div className="w-50">
          <FormDropdown
            reset={dropdownReset}
            onChange={selectApprovedVendor}
            options={approvedVendorOption}
            loading={!approvedVendorOption}
            disabled={!approvedVendorOption}
            plain_dropdown
            leftStatus
          />
        </div>
      </div>
      {approvedVendor === t("general.approved_vendors") ? (
        <div className="p-d-flex p-jc-between p-ai-center p-mb-2">
          <label className="h5">{t("general.approved_vendor")}</label>
          <div className="w-50">
            <MultiSelectDropdown
              style={{ minWidth: 0 }}
              value={multiSelectedVendor}
              options={
                approvedVendors
                  ? approvedVendors.map((vendor) => ({
                      name: `${vendor.vendor_name}${
                        vendor.primary_email ? " - " + vendor.primary_email : ""
                      }`,
                      is_vendor_green: vendor.is_vendor_green,
                      rating: vendor.rating,
                      code: vendor.vendor_id,
                    }))
                  : []
              }
              disabled={!dataReady}
              itemTemplate={itemTemplate}
              onChange={(e) => setMultiSelectedVendor(e.value)}
              maxSelectedLabels={3}
              selectedItemsLabel={"{0} vendors selected"}
              placeholder={t("general.approved_vendors_placeholder")}
              leftStatus
            />
          </div>
        </div>
      ) : null}
      {approvedVendor === t("general.other_vendors") ? (
        <div className="p-d-flex p-jc-between p-ai-center p-mb-2 email-field">
          <label className="h5">{t("assetRequest.email_label")}</label>
          <div className="w-50">
            <CustomInputText
              type="email"
              placeholder={t("repairRequestPanel.vendor_email_placeholder")}
              value={vendorEmail}
              onChange={setVendorEmail}
              leftStatus
            />
          </div>
        </div>
      ) : null}
    </React.Fragment>
  );
};

export default VendorOption;
