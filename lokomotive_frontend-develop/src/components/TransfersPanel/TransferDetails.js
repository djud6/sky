import React from "react";
import moment from "moment";
import { useTranslation } from "react-i18next";
import { useMediaQuery } from "react-responsive";
import { Button } from "primereact/button";
import * as Constants from "../../constants";
import { capitalize } from "../../helpers/helperFunctions";
import DetailslView from "../ShareComponents/DetailView/DetailsView";
import DetailsViewMobile from "../ShareComponents/DetailView/DetailsViewMobile";
import "../../styles/helpers/button4.scss";

const TransferDetails = ({
  transfer,
  setSelectedTransfer,
  setMobileDetails,
  disableMobileVersion,
  detailsReady,
}) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  const onBack = () => {
    setMobileDetails(false);
    setSelectedTransfer(null);
  };

  let detailViewTitles = [
    t("general.id"),
    t("general.status"),
    t("general.business_unit"),
    t("transfersSection.current_location"),
    t("transfersSection.transfer_location"),
    t("general.created_by"),
    t("general.modified_by"),
    t("general.date_created"),
    t("general.date_updated"),
  ];
  let detailViewValues = [
    transfer.custom_id,
    capitalize(transfer.status),
    transfer.business_unit,
    transfer.current_location,
    transfer.destination_location,
    transfer.created_by,
    transfer.modified_by,
    moment(transfer.date_created).format("YYYY-MM-DD"),
    moment(transfer.date_modified).format("YYYY-MM-DD"),
  ];

  return (
    <div>
      {isMobile && !disableMobileVersion ? (
        <div className="p-my-3">
          <div className="no-style-btn p-my-3">
            <Button
              label={t("general.back")}
              className="p-button-link"
              icon="pi pi-chevron-left"
              onClick={() => onBack()}
            />
          </div>
          <DetailsViewMobile
            header={t("general.header_vin", { vin: transfer.VIN })}
            titles={detailViewTitles}
            values={detailViewValues}
            description={[
              t("assetTransferPanel.transfer_justification"),
              transfer.justification || t("general.not_applicable"),
            ]}
            files={transfer.files}
          />
        </div>
      ) : (
        <DetailslView
          headers={[
            t("assetTransferPanel.transfer_details"),
            t("general.header_vin", { vin: transfer.VIN }),
          ]}
          titles={detailViewTitles}
          values={detailViewValues}
          description={[
            t("assetTransferPanel.transfer_justification"),
            transfer.justification || t("general.not_applicable"),
          ]}
          files={transfer.files}
          onHideDialog={setSelectedTransfer}
          detailsReady={detailsReady}
        />
      )}
    </div>
  );
};

export default TransferDetails;
