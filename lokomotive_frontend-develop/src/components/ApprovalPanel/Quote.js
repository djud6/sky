import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../constants";
import { RadioButton } from "primereact/radiobutton";
import { Button } from "primereact/button";
import "../../styles/dialogStyles.scss";
import "../../styles/ShareComponents/GeneralRadio.scss";
import "../../styles/helpers/button4.scss";

const Quote = ({
  files,
  quotesList,
  selectedQuote,
  setSelectedQuote,
  withApproval,
  requestStatus,
  handleQuoteApproval,
}) => {
  const { t } = useTranslation();
  const [selectedFile, setSelectedFile] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  let quotesFiles = [];

  files.forEach((data) => {
    if (data.file_purpose === "quote") {
      quotesFiles.push({
        vendor_name: data.vendor__vendor_name,
        vendor_id: data.vendor_id,
        name: data.file_name,
        url: data.file_url,
      });
    }
  });

  //TODO CHECK IF THE DUMMY DATA HAS QUOTES CORRELATED WITH FILES (NO NEED TO CHECK IN THE FUTURE)
  //NOW FOR SOME REQUESTS, QUOTE FILES DOES NOT MATCH WITH QUOTE ENTRY
  let isDataValid = true;

  quotesFiles.forEach((quote) => {
    if (!quotesList.some((el) => el.vendor_id === quote.vendor_id)) {
      isDataValid = false;
    }
  });

  //FILTER ONLY QUOTE THAT GOT APPROVED IF THE REQUEST IS APPROVED
  if (requestStatus.toLowerCase() === "approved" && isDataValid) {
    const vendorId = quotesList.find((el) => el.status?.toLowerCase() === "approved")?.vender_id;
    quotesFiles = quotesFiles.filter((quote) => quote.vender_id === vendorId);
  }

  const selectQuote = (e) => {
    if (selectedQuote && selectedQuote.vendor_id === e.value) {
      setSelectedFile(null);
      setSelectedQuote(null);
    } else {
      const selectedFile = quotesFiles.find((el) => el.vendor_id === e.value);
      const selectedQuote = quotesList.find((el) => el.vendor_id === e.value);
      setSelectedFile(selectedFile);
      setSelectedQuote(selectedQuote);
    }
  };

  return (
    <React.Fragment>
      {quotesFiles.length !== 0 && isDataValid ? (
        <div className="p-d-flex p-flex-column">
          {withApproval && requestStatus.toLowerCase() === "awaiting approval" ? (
            <React.Fragment>
              {isMobile ? (
                <h4 className="header-grey">{t("general.quote_actions")}</h4>
              ) : (
                <h3 className="font-weight-bold">{t("general.quote_actions")}</h3>
              )}
              {quotesFiles.map((file, index) => {
                return (
                  <div className="custom-radio-btn p-d-flex p-ai-center mt-2 mb-2" key={index}>
                    {/* TODO NO NEED TO CHECK IF DATA IS VALID */}
                    <RadioButton
                      value={file.vendor_id}
                      name={file.vendor_name}
                      onChange={selectQuote}
                      checked={selectedQuote?.vendor_id === file.vendor_id}
                      style={{ marginRight: 5 }}
                    />
                    <div
                      className={`p-d-flex p-jc-between w-100 ${isMobile ? "main-details" : ""}`}
                    >
                      <span className="sub-title">{file.vendor_name}:</span>
                      <span className="sub-value">
                        <a target="_blank" rel="noopener noreferrer" href={file.url}>
                          {file.name}
                        </a>
                      </span>
                    </div>
                  </div>
                );
              })}
              <div className="p-mt-3 p-d-flex p-jc-center detail-action-color-1">
                <Button
                  style={{ width: "370px" }}
                  icon="pi pi-check-circle"
                  label={
                    selectedQuote
                      ? t("approvalDetails.approve_quote_btn", {
                          vendor_name: selectedFile.vendor_name,
                        })
                      : t("approvalDetails.approve_no_quote_btn")
                  }
                  onClick={() => handleQuoteApproval()}
                  disabled={!selectedQuote}
                />
              </div>
            </React.Fragment>
          ) : (
            <React.Fragment>
              <h5 className="font-weight-bold">
                {requestStatus.toLowerCase() === "approved"
                  ? t("general.quote_files_approved")
                  : t("general.quote_files_awaiting_approval")}
              </h5>
              {quotesFiles.map((file, index) => {
                return (
                  <div className="p-d-flex p-ai-center mt-1" key={index}>
                    <div
                      className={`p-d-flex p-jc-between w-100 ${isMobile ? "main-details" : ""}`}
                    >
                      <span className="sub-title">{file.vendor_name}:</span>
                      <span className="sub-value">
                        <a
                          target="_blank"
                          rel="noopener noreferrer"
                          href={file.url}
                          style={isMobile ? { color: "white" } : null}
                        >
                          {file.name}
                        </a>
                      </span>
                    </div>
                  </div>
                );
              })}
            </React.Fragment>
          )}
        </div>
      ) : null}
    </React.Fragment>
  );
};

export default Quote;
