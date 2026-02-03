import React, { useState, useEffect } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import { getAuthHeader } from "../../../helpers/Authorization";
import * as Constants from "../../../constants";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import CustomInputText from "../../ShareComponents/CustomInputText";
import { RadioButton } from "primereact/radiobutton";
import MultiSelectDropdown from "../../ShareComponents/Forms/MultiSelectDropdown";
import StarRating from "react-svg-star-rating";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faLeaf } from "@fortawesome/free-solid-svg-icons";

const VendorOption = ({
  method,
  email,
  setEmail,
  approvedVendor,
  setApprovedVendor,
  multiSelectedVendor,
  setMultiSelectedVendor,
  setIsVendorSelected,
  vendorType,
}) => {
  const { t } = useTranslation();
  const [approvedVendors, setApprovedVendors] = useState(null);
  const [dataReady, setDataReady] = useState(false);

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    setDataReady(false);

    let approvedVendorsAPI;

    if (vendorType === "repair") {
      approvedVendorsAPI = `${Constants.ENDPOINT_PREFIX}/api/v1/ApprovedVendor/List/By/Task/repair`;
    } else if (vendorType === "disposal") {
      approvedVendorsAPI = `${Constants.ENDPOINT_PREFIX}/api/v1/ApprovedVendor/List/By/Task/disposal`;
    }

    axios
      .get(approvedVendorsAPI, getAuthHeader())
      .then((res) => {
        setApprovedVendors(res.data);
        setDataReady(true);
      })
      .catch((err) => {
        ConsoleHelper(err);
      });

    return () => {
      cancelTokenSource.cancel("cancel the asynchronous api call");
    };
  }, [vendorType]);

  useEffect(() => {
    (approvedVendor === t("general.other_vendors") && email) ||
    (approvedVendor === t("general.approved_vendors") && multiSelectedVendor.length)
      ? setIsVendorSelected(true)
      : setIsVendorSelected(false);

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [approvedVendor, email, multiSelectedVendor, setIsVendorSelected]);

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
      <label htmlFor="vendor" className="h5">
        {t("general.vendor_question", { request_type: vendorType })}
      </label>
      <div className="p-d-flex darkRadio">
        <div className="p-field-radiobutton p-mr-3 p-mb-0">
          <RadioButton
            inputId="approvedVendorTrue"
            name="vendor"
            value={t("general.approved_vendors")}
            onChange={(e) => {
              setApprovedVendor(e.value);
              setEmail("");
            }}
            checked={approvedVendor === t("general.approved_vendors")}
          />
          <label className="p-m-0 p-m-2" htmlFor="approvedVendorTrue">
            {t("general.approved_vendors")}
          </label>
        </div>
        <div className="p-field-radiobutton p-mb-0">
          <RadioButton
            inputId="approvedVendorFalse"
            name="vendor"
            value={t("general.other_vendors")}
            onChange={(e) => {
              setApprovedVendor(e.value);
              setMultiSelectedVendor([]);
            }}
            checked={approvedVendor === t("general.other_vendors")}
          />
          <label className="p-m-0 p-m-2" htmlFor="approvedVendorFalse">
            {t("general.other_vendors")}
          </label>
        </div>
      </div>
      {approvedVendor === t("general.approved_vendors") && (
        <React.Fragment>
          <label className="h5 p-mt-3">{t("general.approved_vendor")}</label>
          <MultiSelectDropdown
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
          />
        </React.Fragment>
      )}
      {approvedVendor === t("general.other_vendors") && (
        <React.Fragment>
          <label className="h5 p-mt-3">
            {t("removalPanel.recipient_title", { method: method })}
          </label>
          <div className="txtField-2">
            <CustomInputText className="w-100" value={email} onChange={setEmail} />
          </div>
        </React.Fragment>
      )}
    </React.Fragment>
  );
};

export default VendorOption;
