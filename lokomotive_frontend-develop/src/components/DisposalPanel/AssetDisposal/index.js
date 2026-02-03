import React, { useState, useEffect } from "react";
import axios from "axios";
import { useDispatch, useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { useLocation } from "react-router-dom";
import { useMediaQuery } from "react-responsive";
import * as Constants from "../../../constants";
import { CTRL_AUDIO_PLAY } from "../../../redux/types/audioTypes";
import { getAuthHeader } from "../../../helpers/Authorization";
import { faRecycle } from "@fortawesome/free-solid-svg-icons";
import { Button } from "primereact/button";
import { ProgressBar } from "primereact/progressbar";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import QuickAccessTabs from "../../ShareComponents/QuickAccessTabs";
import PanelHeader from "../../ShareComponents/helpers/PanelHeader";
import VINSearch from "../../ShareComponents/helpers/VINSearch";
import WarningMsg from "../../ShareComponents/WarningMsg";
import { loadingAlert, successAlert, generalErrorAlert } from "../../ShareComponents/CommonAlert";
import UploadFiles from "./UploadFiles";
import AssetDisposalForm from "./AssetDisposalForm";
import DisposalMethod from "./DisposalMethod";
import Recipient from "./Recipient";
import ScrapMethod from "./ScrapMethod";
import RepurposeMethod from "./RepurposeMethod";
import DisposalRequestPreview from "./DisposalRequestPreview";
import ConsoleHelper from "../../../helpers/ConsoleHelper";
import "../../../styles/ShareComponents/Table/table.scss";
import "../../../styles/helpers/button5.scss";
import "../../../styles/DisposalPanel/AssetDisposal.scss";

const RemoveAssetTable = ({ vehicle }) => {
  const { t } = useTranslation();
  return (
    <div className="darkTable disposal-table">
      <DataTable value={vehicle}>
        <Column field="VIN" header={t("removalPanel.vin_label")}>
          {""}
        </Column>
        <Column field="asset_type" header={t("removalPanel.asset_type_label")}>
          {""}
        </Column>
        <Column field="current_location" header={t("removalPanel.location_label")}>
          {""}
        </Column>
        <Column field="date_of_manufacture" header={t("removalPanel.year_label")}>
          {""}
        </Column>
        <Column field="manufacturer" header={t("removalPanel.manufacturer_label")}>
          {""}
        </Column>
        <Column field="model_number" header={t("removalPanel.model_label")}>
          {""}
        </Column>
        <Column field="colour" header={t("removalPanel.colour_label")}>
          {""}
        </Column>
        <Column field="mileage" header={t("general.km_hrs")}>
          {""}
        </Column>
      </DataTable>
    </div>
  );
};

const RemoveAssetForm = ({ vehicle, setVehicle, setForceUpdate }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [step, setStep] = useState(1);
  const [vinImage, setVinImage] = useState([]);
  const [vinImageName, setVinImageName] = useState([]);
  const [mileageImage, setMileageImage] = useState([]);
  const [mileageImageName, setMileageImageName] = useState([]);
  const [vinImagePreview, setVinImagePreview] = useState([]);
  const [mileageImagePreview, setMileageImagePreview] = useState([]);
  const [otherDocs, setOtherDocs] = useState([]);
  const [otherDocsName, setOtherDocsName] = useState([]);
  const [refurbishRequired, setRefurbishRequired] = useState({});
  const [interiorCond, setInteriorCond] = useState({});
  const [interiorDets, setInteriorDets] = useState("");
  const [exteriorCond, setExteriorCond] = useState({});
  const [exteriorDets, setExteriorDets] = useState("");
  const [disposalReason, setDisposalReason] = useState({});
  const [replacementResaon, setReplacementResaon] = useState("");
  const [disposalMethod, setDisposalMethod] = useState({});
  const [isStripped, setIsStripped] = useState({});
  const [selectedBusinessUnit, setSelectedBusinessUnit] = useState(null);
  const [selectedJobSpec, setSelectedJobSpec] = useState(null);
  const [approvedRepairVendor, setApprovedRepairVendor] = useState(null);
  const [multiSelectedRepairVendor, setMultiSelectedRepairVendor] = useState([]);
  const [repairVendoremail, setRepairVendorEmail] = useState("");
  const [isRepairVendorSelected, setIsRepairVendorSelected] = useState(false);
  const [repairdDescription, setRepairDescription] = useState("");
  const [hours, setHours] = useState("");
  const [mileage, setMileage] = useState("");
  const [pickupDate, setPickupDate] = useState(null);
  const [disposalPickupDate, setDisposalPickupDate] = useState(null);
  const [quoteDeadline, setQuoteDeadline] = useState(null);
  const [disposalQuoteDeadline, setDisposalQuoteDeadline] = useState(null);
  const [requestDate, setRequestDate] = useState(null);
  const [approvedVendor, setApprovedVendor] = useState(null);
  const [multiSelectedVendor, setMultiSelectedVendor] = useState([]);
  const [email, setEmail] = useState("");
  const [isVendorSelected, setIsVendorSelected] = useState(false);
  const [disableCountinue, setDisableCountinue] = useState(false);
  const [disposalVendorTransportToVendor, setDisposalVendorTransportToVendor] = useState(null);
  const [repairVendorTransportToVendor, setRepairVendorTransportToVendor] = useState(null);
  const [repairVendorTransportToClient, setRepairVendorTransportToClient] = useState(null);
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });
  const { listBusinessUnits, listJobSpecs } = useSelector((state) => state.apiCallData);

  const dependencyList = [
    step,
    vinImage,
    vinImageName,
    mileageImage,
    mileageImageName,
    refurbishRequired,
    interiorCond,
    exteriorCond,
    disposalReason,
    interiorDets,
    exteriorDets,
    disposalMethod,
    isStripped,
    isRepairVendorSelected,
    isVendorSelected,
    repairdDescription,
    mileage,
    hours,
    pickupDate,
    disposalPickupDate,
    requestDate,
    selectedBusinessUnit,
    selectedJobSpec,
    quoteDeadline,
    disposalQuoteDeadline,
    disposalVendorTransportToVendor,
    repairVendorTransportToVendor,
    repairVendorTransportToClient,
  ];

  useEffect(() => {
    setStep(1);
    setVinImage([]);
    setVinImageName([]);
    setMileageImage([]);
    setMileageImageName([]);
    setVinImagePreview([]);
    setMileageImagePreview([]);
    setOtherDocs([]);
    setOtherDocsName([]);
    setRefurbishRequired({});
    setInteriorCond({});
    setInteriorDets("");
    setExteriorCond({});
    setExteriorDets("");
    setDisposalReason({});
    setReplacementResaon("");
    setDisposalMethod({});
    setIsStripped({});
    setSelectedBusinessUnit(null);
    setSelectedJobSpec(null);
    setApprovedRepairVendor(null);
    setMultiSelectedRepairVendor([]);
    setRepairVendorEmail("");
    setIsRepairVendorSelected(false);
    setRepairDescription("");
    setHours("");
    setMileage("");
    setPickupDate(null);
    setDisposalPickupDate(null);
    setRequestDate(null);
    setApprovedVendor(null);
    setMultiSelectedVendor([]);
    setEmail("");
    setIsVendorSelected(false);
    setDisableCountinue(false);
    setQuoteDeadline(null);
    setDisposalQuoteDeadline(null);
    setDisposalVendorTransportToVendor(null);
    setRepairVendorTransportToVendor(null);
    setRepairVendorTransportToClient(null);
  }, [vehicle]);

  useEffect(() => {
    if (step === 1 && vinImage.length === 0) {
      setDisableCountinue(true);
      return;
    } else {
      setDisableCountinue(false);
    }
    if (
      step === 2 &&
      (Object.keys(interiorCond).length === 0 ||
        Object.keys(exteriorCond).length === 0 ||
        Object.keys(disposalReason).length === 0 ||
        Object.keys(refurbishRequired).length === 0 ||
        !interiorDets ||
        !exteriorDets ||
        !disposalQuoteDeadline ||
        disposalVendorTransportToVendor === null ||
        (disposalVendorTransportToVendor !== null && !disposalPickupDate))
    ) {
      setDisableCountinue(true);
      return;
    } else if (
      step === 2 &&
      refurbishRequired.name.toLowerCase() === "yes" &&
      (!isRepairVendorSelected ||
        !repairdDescription ||
        repairVendorTransportToVendor === null ||
        (repairVendorTransportToVendor !== null && !pickupDate) ||
        repairVendorTransportToClient === null ||
        (repairVendorTransportToClient !== null && !requestDate) ||
        !quoteDeadline)
    ) {
      setDisableCountinue(true);
      return;
    } else {
      setDisableCountinue(false);
    }
    if (step === 3 && Object.keys(disposalMethod).length === 0) {
      setDisableCountinue(true);
      return;
    } else {
      setDisableCountinue(false);
    }
    if (
      step === 4 &&
      !isVendorSelected &&
      (disposalMethod.name === t("removalPanel.company_directed_sale") ||
        disposalMethod.name === t("removalPanel.trade_in") ||
        disposalMethod.name === t("removalPanel.auction") ||
        disposalMethod.name === t("removalPanel.donate") ||
        disposalMethod.name === t("removalPanel.write_off"))
    ) {
      setDisableCountinue(true);
      return;
    } else {
      setDisableCountinue(false);
    }
    if (
      step === 4 &&
      disposalMethod.name === t("removalPanel.scrap") &&
      (Object.keys(isStripped).length === 0 || !isVendorSelected)
    ) {
      setDisableCountinue(true);
      return;
    } else {
      setDisableCountinue(false);
    }
    if (
      step === 4 &&
      disposalMethod.name === t("removalPanel.repurpose") &&
      (!selectedBusinessUnit || !isVendorSelected)
    ) {
      setDisableCountinue(true);
      return;
    } else {
      setDisableCountinue(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(dependencyList)]);

  useEffect(() => {
    setApprovedVendor(null);
    setMultiSelectedVendor([]);
    setEmail("");
    setIsVendorSelected(false);
    setIsStripped({});
    setSelectedBusinessUnit(null);
    setSelectedJobSpec(null);
  }, [disposalMethod]);

  const resetForm = () => {
    setVehicle(null);
    setForceUpdate(Date.now());
  };

  const handleDisposalSubmit = () => {
    dispatch({ type: CTRL_AUDIO_PLAY, payload: "submit" });
    let required_data = {
      disposal_data: {
        VIN: vehicle.VIN,
        disposal_type: disposalMethod.name.toLowerCase(),
        interior_condition: interiorCond.name.toLowerCase(),
        interior_condition_details: interiorDets,
        exterior_condition: exteriorCond.name.toLowerCase(),
        exterior_condition_details: exteriorDets,
        disposal_reason: disposalReason.name.toLowerCase(),
        ...(disposalReason.name.toLowerCase() ===
          t("removalPanel.being_replaced").toLowerCase() && {
          replacement_reason: replacementResaon.name.toLowerCase(),
        }),
        ...(approvedVendor === t("general.approved_vendors")
          ? {
              vendor: null, //TODO need to auto setup this in the future
              potential_vendor_ids: `-${multiSelectedVendor.map((el) => el.code).join("-")}-`,
            }
          : null),
        primary_vendor_email: approvedVendor === t("general.other_vendors") ? email : null,
        ...(refurbishRequired.name === t("general.yes")
          ? { refurbished: true }
          : { refurbished: false }),
        ...(disposalMethod.name === t("removalPanel.scrap")
          ? isStripped.name === t("general.yes")
            ? { is_stripped: true }
            : { is_stripped: false }
          : null),
        vendor_transport_to_vendor: disposalVendorTransportToVendor,
        available_pickup_date: disposalPickupDate.toISOString(),
        quote_deadline: disposalQuoteDeadline.toISOString(),
      },

      // TODO: Replace the placeholder info for approval_data
      approval_data: {
        title: "Disposal Approval",
        description: "This is an approval made for testing purposes.",
      },
    };

    let required_file_specs = {
      file_info: [
        {
          file_name: vinImage[0].name,
          purpose: "vin",
        },
      ],
    };
    for (let i = 0; i < mileageImage.length; i++) {
      required_file_specs.file_info.push({ file_name: mileageImage[i].name, purpose: "usage" });
    }
    for (let i = 0; i < otherDocs.length; i++) {
      required_file_specs.file_info.push({ file_name: otherDocs[i].name, purpose: "other" });
    }

    let disposalReport = new FormData();
    disposalReport.append("files", vinImage[0]);
    for (let i = 0; i < mileageImage.length; i++) {
      disposalReport.append("files", mileageImage[i]);
    }
    for (let i = 0; i < otherDocs.length; i++) {
      disposalReport.append("files", otherDocs[i]);
    }
    submitDisposalRequest(required_data, required_file_specs, disposalReport);
  };

  const submitDisposalRequest = (data, file_specs, disposalReport) => {
    disposalReport.append("data", JSON.stringify(data));
    disposalReport.append("file_specs", JSON.stringify(file_specs));
    let APIsuffix = "";
    if (disposalMethod.name === t("removalPanel.donate")) {
      APIsuffix = "Donation";
    }
    if (disposalMethod.name !== t("removalPanel.donate")) {
      APIsuffix = disposalMethod.name.replace(/[^A-Z0-9]/gi, "");
    }

    loadingAlert();
    const headers = getAuthHeader();
    headers.headers["Content-Type"] = "application/json";

    const requestConfig = {
      method: "post",
      url: `${Constants.ENDPOINT_PREFIX}/api/v1/AssetDisposal/Add/${APIsuffix}`,
      ...headers,
      data: disposalReport,
    };
    axios(requestConfig)
      .then((response) => {
        let disposalID = response.data.disposal_id;
        let repurposeData = {
          VIN: vehicle.VIN,
          notify_managers: true,
          ...(selectedJobSpec && { job_specification: selectedJobSpec.job_specification_id }),
          ...(selectedBusinessUnit && { business_unit: selectedBusinessUnit.business_unit_id }),
        };

        if (refurbishRequired.name === t("general.yes")) {
          let repairRequestData = new FormData();
          repairRequestData.append(
            "data",
            JSON.stringify({
              repair_data: {
                VIN: vehicle.VIN,
                is_refurbishment: true,
                disposal: disposalID,
                description: repairdDescription,
                is_complete: false,
                vendor_transport_to_vendor: repairVendorTransportToVendor,
                requested_delivery_date: requestDate.toISOString(),
                vendor_transport_to_client: repairVendorTransportToClient,
                available_pickup_date: pickupDate.toISOString(),
                quote_deadline: quoteDeadline.toISOString(),
                ...(approvedRepairVendor === t("general.approved_vendors")
                  ? {
                      vendor: null, //TODO need to auto setup this in the future
                      potential_vendor_ids: `-${multiSelectedVendor
                        .map((el) => el.code)
                        .join("-")}-`,
                    }
                  : null),
                ...(approvedRepairVendor === t("general.other_vendors")
                  ? { vendor_email: repairVendoremail }
                  : null),
                is_urgent: false,
                ...(vehicle.hours_or_mileage.toLowerCase() === "both" && {
                  mileage: parseFloat(mileage),
                  hours: parseFloat(hours),
                }),
                ...(vehicle.hours_or_mileage.toLowerCase() === "mileage" && {
                  mileage: parseFloat(mileage),
                }),
                ...(vehicle.hours_or_mileage.toLowerCase() === "hours" && {
                  hours: parseFloat(hours),
                }),
              },
              assetissuemodel_set: { issue_set: [] },
              // TODO: Replace the placeholder info for approval_data
              approval_data: {
                title: "Repair Approval",
                description: "This is an approval made for testing purposes.",
              },
            })
          );

          // TODO: file placeholder info
          let required_file_specs = {
            file_info: [],
          };

          repairRequestData.append("file_specs", JSON.stringify(required_file_specs));

          let repairRequestAPIcall = axios.post(
            `${Constants.ENDPOINT_PREFIX}/api/v1/Repair/Add`,
            repairRequestData,
            getAuthHeader()
          );

          if (disposalMethod.name === t("removalPanel.repurpose")) {
            let repurposeAPIcall = axios.post(
              `${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Reassign`,
              repurposeData,
              getAuthHeader()
            );
            axios
              .all([repairRequestAPIcall, repurposeAPIcall])
              .then((res) => {
                successAlert(t("removalPanel.disposal_title"));
                dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
                resetForm();
              })
              .catch((error) => {
                ConsoleHelper(error);
                generalErrorAlert(error.customErrorMsg);
                dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
              });
          } else {
            axios
              .all([repairRequestAPIcall])
              .then((res) => {
                successAlert(t("removalPanel.disposal_title"));
                dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
                resetForm();
              })
              .catch((error) => {
                ConsoleHelper(error);
                generalErrorAlert(error.customErrorMsg);
                dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
              });
          }
        } else if (disposalMethod.name === t("removalPanel.repurpose")) {
          axios
            .post(
              `${Constants.ENDPOINT_PREFIX}/api/v1/Assets/Reassign`,
              repurposeData,
              getAuthHeader()
            )
            .then((response) => {
              successAlert(t("removalPanel.disposal_title"));
              dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
              resetForm();
            })
            .catch((error) => {
              ConsoleHelper(error);
              generalErrorAlert(error.customErrorMsg);
              dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
            });
        } else {
          successAlert(t("removalPanel.disposal_title"));
          dispatch({ type: CTRL_AUDIO_PLAY, payload: "success_alert" });
          resetForm();
        }
      })
      .catch((error) => {
        generalErrorAlert(error.customErrorMsg);
        dispatch({ type: CTRL_AUDIO_PLAY, payload: "error_alert" });
      });
  };

  const onContinue = () => {
    if (step < 5) setStep(step + 1);
  };

  const onBack = () => {
    if (step > 1) setStep(step - 1);
  };

  return (
    <div className={`${isMobile ? "p-mx-3 p-mb-5" : ""}`}>
      <div className="p-grid disposal-form-container">
        <div className="p-col-12">
          <ProgressBar value={(step - 1) * 25}>{""}</ProgressBar>
        </div>
        {step === 1 ? (
          <UploadFiles
            vin={vehicle.VIN}
            vinImage={vinImage}
            setVinImage={setVinImage}
            vinImageName={vinImageName}
            setVinImageName={setVinImageName}
            mileageImage={mileageImage}
            setMileageImage={setMileageImage}
            mileageImageName={mileageImageName}
            setMileageImageName={setMileageImageName}
            vinImagePreview={vinImagePreview}
            setVinImagePreview={setVinImagePreview}
            mileageImagePreview={mileageImagePreview}
            setMileageImagePreview={setMileageImagePreview}
            otherDocs={otherDocs}
            setOtherDocs={setOtherDocs}
            otherDocsName={otherDocsName}
            setOtherDocsName={setOtherDocsName}
          />
        ) : null}
        {step === 2 ? (
          <AssetDisposalForm
            vehicle={vehicle}
            refurbishRequired={refurbishRequired}
            setRefurbishRequired={setRefurbishRequired}
            interiorCond={interiorCond}
            setInteriorCond={setInteriorCond}
            interiorDets={interiorDets}
            setInteriorDets={setInteriorDets}
            exteriorCond={exteriorCond}
            setExteriorCond={setExteriorCond}
            exteriorDets={exteriorDets}
            setExteriorDets={setExteriorDets}
            disposalReason={disposalReason}
            setDisposalReason={setDisposalReason}
            replacementResaon={replacementResaon}
            setReplacementResaon={setReplacementResaon}
            approvedRepairVendor={approvedRepairVendor}
            setApprovedRepairVendor={setApprovedRepairVendor}
            multiSelectedRepairVendor={multiSelectedRepairVendor}
            setMultiSelectedRepairVendor={setMultiSelectedRepairVendor}
            repairVendoremail={repairVendoremail}
            setRepairVendorEmail={setRepairVendorEmail}
            isRepairVendorSelected={isRepairVendorSelected}
            setIsRepairVendorSelected={setIsRepairVendorSelected}
            repairdDescription={repairdDescription}
            setRepairDescription={setRepairDescription}
            hours={hours}
            setHours={setHours}
            mileage={mileage}
            setMileage={setMileage}
            pickupDate={pickupDate}
            disposalPickupDate={disposalPickupDate}
            setPickupDate={setPickupDate}
            setDisposalPickupDate={setDisposalPickupDate}
            requestDate={requestDate}
            setRequestDate={setRequestDate}
            quoteDeadline={quoteDeadline}
            setQuoteDeadline={setQuoteDeadline}
            disposalQuoteDeadline={disposalQuoteDeadline}
            setDisposalQuoteDeadline={setDisposalQuoteDeadline}
            disposalVendorTransportToVendor={disposalVendorTransportToVendor}
            setDisposalVendorTransportToVendor={setDisposalVendorTransportToVendor}
            repairVendorTransportToVendor={repairVendorTransportToVendor}
            setRepairVendorTransportToVendor={setRepairVendorTransportToVendor}
            repairVendorTransportToClient={repairVendorTransportToClient}
            setRepairVendorTransportToClient={setRepairVendorTransportToClient}
          />
        ) : null}
        {step === 3 ? (
          <DisposalMethod disposalMethod={disposalMethod} setDisposalMethod={setDisposalMethod} />
        ) : null}
        {step === 4 &&
        (disposalMethod.name === t("removalPanel.company_directed_sale") ||
          disposalMethod.name === t("removalPanel.trade_in") ||
          disposalMethod.name === t("removalPanel.auction") ||
          disposalMethod.name === t("removalPanel.donate") ||
          disposalMethod.name === t("removalPanel.write_off")) ? (
          <Recipient
            method={disposalMethod.name}
            email={email}
            setEmail={setEmail}
            approvedVendor={approvedVendor}
            setApprovedVendor={setApprovedVendor}
            multiSelectedVendor={multiSelectedVendor}
            setMultiSelectedVendor={setMultiSelectedVendor}
            isVendorSelected={isVendorSelected}
            setIsVendorSelected={setIsVendorSelected}
          />
        ) : null}
        {step === 4 && disposalMethod.name === t("removalPanel.scrap") ? (
          <ScrapMethod
            email={email}
            setEmail={setEmail}
            approvedVendor={approvedVendor}
            setApprovedVendor={setApprovedVendor}
            multiSelectedVendor={multiSelectedVendor}
            setMultiSelectedVendor={setMultiSelectedVendor}
            isVendorSelected={isVendorSelected}
            setIsVendorSelected={setIsVendorSelected}
            isStripped={isStripped}
            setIsStripped={setIsStripped}
          />
        ) : null}
        {step === 4 && disposalMethod.name === t("removalPanel.repurpose") ? (
          <RepurposeMethod
            email={email}
            setEmail={setEmail}
            approvedVendor={approvedVendor}
            setApprovedVendor={setApprovedVendor}
            multiSelectedVendor={multiSelectedVendor}
            setMultiSelectedVendor={setMultiSelectedVendor}
            isVendorSelected={isVendorSelected}
            setIsVendorSelected={setIsVendorSelected}
            businessUnits={listBusinessUnits}
            selectedBusinessUnit={selectedBusinessUnit}
            setSelectedBusinessUnit={setSelectedBusinessUnit}
            jobSpecList={listJobSpecs}
            selectedJobSpec={selectedJobSpec}
            setSelectedJobSpec={setSelectedJobSpec}
          />
        ) : null}
        {step === 5 ? (
          <DisposalRequestPreview
            vin={vehicle.VIN}
            vinImagePreview={vinImagePreview}
            mileageImagePreview={mileageImagePreview}
            interiorCond={interiorCond}
            interiorDets={interiorDets}
            exteriorCond={exteriorCond}
            exteriorDets={exteriorDets}
            disposalReason={disposalReason}
            replacementResaon={replacementResaon}
            disposalMethod={disposalMethod}
            multiSelectedVendor={multiSelectedVendor}
            email={email}
            selectedBusinessUnit={selectedBusinessUnit}
            selectedJobSpec={selectedJobSpec}
            refurbishRequired={refurbishRequired}
            multiSelectedRepairVendor={multiSelectedRepairVendor}
            repairVendoremail={repairVendoremail}
            repairdDescription={repairdDescription}
            hours={hours}
            mileage={mileage}
            pickupDate={pickupDate}
            requestDate={requestDate}
            disposalPickupDate={disposalPickupDate}
            disposalQuoteDeadline={disposalQuoteDeadline}
            repairQuoteDeadline={quoteDeadline}
            disposalVendorTransportToVendor={disposalVendorTransportToVendor}
            repairVendorTransportToVendor={repairVendorTransportToVendor}
            repairVendorTransportToClient={repairVendorTransportToClient}
          />
        ) : null}
        <div className={`${!isMobile ? "p-sm-12 p-md-12 p-lg-6 p-xl-6" : "w-100 p-mx-3 p-my-3"}`}>
          <div className="p-d-flex p-jc-between">
            <div className="btn-5 disable-bg">
              <Button
                label={t("general.back")}
                icon="pi pi-angle-left"
                onClick={onBack}
                disabled={step === 1}
              />
            </div>
            {step < 5 ? (
              <div className="btn-5">
                <Button
                  label={`${step === 4 ? t("general.review") : t("general.continue")}`}
                  icon="pi pi-angle-right"
                  iconPos="right"
                  onClick={onContinue}
                  disabled={disableCountinue}
                />
              </div>
            ) : null}
            {step === 5 ? (
              <div className="btn-5 active-bg">
                <Button
                  className="p-button-success"
                  label={t("general.submit")}
                  icon="pi pi-check"
                  iconPos="right"
                  onClick={() => handleDisposalSubmit()}
                />
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};

const RemoveAssetPanel = () => {
  const location = useLocation();
  const { t } = useTranslation();
  const [vehicle, setVehicle] = useState(null);
  const [vehicleArray, setVehicleArray] = useState([]);
  const [forceUpdate, setForceUpdate] = useState(Date.now());
  const isMobile = useMediaQuery({ query: `(max-width: ${Constants.MOBILE_BREAKPOINT}px)` });

  useEffect(() => {
    setVehicleArray([vehicle]);
  }, [vehicle]);

  return (
    <div className="disposal-panel">
      {isMobile && (
        <QuickAccessTabs
          tabs={["Asset Removal", "Removal History"]}
          activeTab={"Asset Removal"}
          urls={["/asset-removal", "/asset-removal/history"]}
        />
      )}
      <PanelHeader icon={faRecycle} text={t("removalPanel.disposal_title")} />
      {!isMobile && (
        <React.Fragment>
          <QuickAccessTabs
            tabs={["Asset Removal", "Asset Removal History"]}
            activeTab={"Asset Removal"}
            urls={["/asset-removal", "/asset-removal/history"]}
          />
          <div className="p-mt-4">
            <VINSearch
              key={forceUpdate}
              defaultValue={`${!vehicle && location.state ? location.state.vehicle.VIN : ""}`}
              onVehicleSelected={(v) => {
                Array.isArray(v) && v.length === 0 ? setVehicle(null) : setVehicle(v);
              }}
            />
          </div>
        </React.Fragment>
      )}
      {isMobile && (
        <div className="mobile-searchbar p-m-3">
          <div className="title">{t("removalPanel.mobile_title")}</div>
          <div className="p-mb-4">
            <VINSearch
              key={forceUpdate}
              defaultValue={`${!vehicle && location.state ? location.state.vehicle.VIN : ""}`}
              onVehicleSelected={(v) => {
                Array.isArray(v) && v.length === 0 ? setVehicle(null) : setVehicle(v);
              }}
            />
          </div>
        </div>
      )}
      {!!vehicle && vehicleArray.length !== 0 ? (
        !vehicle.has_disposal && vehicle.status.toLowerCase() !== "disposed-of" ? (
          <div>
            {!isMobile && (
              <RemoveAssetTable vehicle={vehicleArray} resetForm={() => setVehicle(null)} />
            )}
            <RemoveAssetForm
              vehicle={vehicle}
              setVehicle={setVehicle}
              setForceUpdate={setForceUpdate}
            />
          </div>
        ) : (
          <div className={`${isMobile ? "p-mx-3" : ""}`}>
            <WarningMsg message={t("removalPanel.submitted_disposal")} />
          </div>
        )
      ) : null}
    </div>
  );
};

export default RemoveAssetPanel;
